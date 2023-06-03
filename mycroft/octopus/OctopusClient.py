import websocket
import time
import threading
import socket
import json
import uuid
from enum import Enum

from mycroft.util.log import LOG

class AppState(Enum):
    INIT = 0,
    READY = 1

class OctopusClient:
    def __init__(self, udpPort, bus):
        self.bus = bus
        
        self.udpPort = udpPort
        self.udpThread: threading.Thread = None
        self.udpSocket = None
        self.exploredServers: dict[str, int] = {}

        self.websocket = None
        self.websocketThread: threading.Thread = None
        self.udpStarting = False

        self.stopUdpLock = threading.Lock()
        self.stopWSLock = threading.Lock()
        self.stopping = False

        self.currState = AppState.INIT

    def start(self):
        self.stop()
        self.stopping = False
        self.startUdp()

    def startUdp(self):
        if self.udpStarting:
            return

        LOG.info("Start udp")

        self.udpStarting = True

        self.udpThread = threading.Thread(target=self._udpRun)
        self.udpThread.daemon = True
        self.udpThread.start()


    def _udpRun(self):
        LOG.info("Begin udp loop")
        self.stopWS()

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udpSocket.bind(("0.0.0.0", self.udpPort))

        try:
            while True:
                recv, addr = self.udpSocket.recvfrom(1024)

                if len(recv) <= 0:
                    break

                host = addr[0]

                now = time.time()
                # 30s timeout
                if now - self.exploredServers.get(host, 0) < 30:
                    continue

                self.exploredServers[host] = now

                try:
                    json_recv = json.loads(recv)
                except json.JSONDecodeError as e:
                    continue

                if json_recv.get("type") == "OctopusServerBroadcast" and type(json_recv.get("content", {}).get("websocket", None)) == int:
                    self.udpSocket.close()
                    self.udpStarting = False
                    # self.stopWS()

                    self.websocketThread = threading.Thread(target=self._wsRun, args=(host, json_recv["content"]["websocket"]))
                    self.websocketThread.daemon = True
                    self.websocketThread.start()

                    LOG.info("switching to ws")
                    break
            

        except OSError as e:
            LOG.info("Udp socket closed")

        LOG.info("End udp loop")
        self.udpStarting = False

    def _wsRun(self, host, port):
        LOG.info("Begin ws run")
        self.stopUdp()
        self.websocket = websocket.WebSocketApp(f"ws://{host}:{port}/", 
                                            on_open=self.on_open, 
                                            on_message=self.on_message,
                                            on_error=self.on_error,
                                            on_close=self.on_close)

        self.websocket.run_forever()
        LOG.info("End ws run")

        self.currState = AppState.INIT

    def stop(self):
        self.stopping = True
        self.stopWS() 
        self.stopUdp() 
        
    def stopWS(self):
        with self.stopWSLock:
            if self.websocket is not None:
                self.websocket.close()
                self.websocketThread.join(timeout=10)
                self.websocket = None
                self.websocketThread = None

    def stopUdp(self):
        with self.stopUdpLock:
            if self.udpSocket is not None:
                self.udpSocket.close()
                self.udpThread.join(timeout=10)
                self.udpSocket = None
                self.udpThread = None

    def on_open(self, ws):
        LOG.info("Connected to octopus with WS")
        self.currState = AppState.INIT

        init_msg = {
            "type": "init",
            "app": {
                "type": "Mycroft",
                "desc": "Mycroft octopus plugin."
            }
        }

        self.websocket.send(json.dumps(init_msg))

    def on_close(self, ws, code, msg):
        LOG.info("WS connection closed")
        self.websocket.close()
        self.startUdp()

    def on_error(self, ws, err):
        LOG.info("WS connection errored")
        self.websocket.close()
        self.startUdp()

    def on_message(self, ws, message):
        LOG.info(str(message))
        LOG.info(type(message))

        try: 
            json_msg = json.loads(message)
        except json.JSONDecodeError as e:
            LOG.error(f"Error while decoding octopus message : {e}")
            return

        if self.currState == AppState.INIT:
            self.onMessageInit(json_msg)
        else:
            self.onMessageRunning(json_msg)

    def onMessageInit(self, message: dict):
        if message.get("type") == "init":
            if message.get("data") == "OK":
                LOG.info("Got initialization message from octopus")
        
    def onMessageRunning(self, message: dict):
        LOG.warning(f"Received message from octopus {message}")
        LOG.warning(f"Message reception is not yet handled")

    # TODO : broadcast subscription and message reception


    def sendMessage(self, message):
        if self.websocket is None:
            LOG.error(f"Could not send message : Not connected to websocket (message = {message})")

        if self.currState != AppState.READY:
            LOG.error(f"Could not send message : App not in READY state (self.currState = {self.currState})")

        self.websocket.send(json.dumps(message))

    def sendBroadcastMessage(self, channel, content):
        message = {
                "type": "broadcast",
                "channel": channel, 
                "id": str(uuid.uuid4()),
                "content": content
            }

        self.sendMessage(message)