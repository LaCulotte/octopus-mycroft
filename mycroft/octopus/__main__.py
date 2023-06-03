"""Mycroft octopus service.

    This handles the connection to an Octopus server
"""
from mycroft.util import (
    check_for_signal,
    reset_sigint_handler,
    start_message_bus_client,
    wait_for_exit_signal
)
from mycroft.util.log import LOG
from mycroft.util.process_utils import ProcessStatus, StatusCallbackMap
from mycroft.messagebus.message import Message

from .OctopusClient import OctopusClient

client: OctopusClient = None

def on_ready():
    LOG.info('Octopus service is ready.')


def on_error(e='Unknown'):
    LOG.error('Octopus service failed to launch ({}).'.format(repr(e)))
    global client
    if client is not None:
        client.stop()
        client = None

def on_stopping():
    LOG.info('Octopus service is shutting down...')
    global client
    if client is not None:
        client.stop()
        client = None

def handle_speech_wave(event: Message):
    LOG.info("Got speechwave, sending to octopus")
    client.sendBroadcastMessage("speech_wave", event.data)
    LOG.info(f"Speech_wave length : {len(event.data.get('soundwave', []))}")

def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping):
    """Start the Audio Service and connect to the Message Bus"""
    LOG.info("Starting Octopus Service")
    try:
        reset_sigint_handler()
        bus = start_message_bus_client("OCTOPUS", whitelist=None)
        callbacks = StatusCallbackMap(on_ready=ready_hook, on_error=error_hook,
                                      on_stopping=stopping_hook)
        status = ProcessStatus('octopus', bus, callbacks)

        bus.on('speech_wave', handle_speech_wave)

        status.set_started()

        global client
        client = OctopusClient(3000, bus)
        client.start()
    except Exception as e:
        status.set_error(e)
    else:
        status.set_ready()
        wait_for_exit_signal()
        status.set_stopping()

if __name__ == '__main__':
    main()
