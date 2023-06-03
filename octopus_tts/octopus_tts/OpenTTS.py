# Copyright 2020 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import requests
import wave
import numpy as np
import base64
import time

from mycroft.tts import TTS, TTSValidator
from mycroft.configuration import Configuration
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG

import ntplib

import math

base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def b64encode(iterable):
    ret = ""
    char3_array = [0] * 3
    char4_array = [0] * 4
    i = 0
    for num in iterable:
        char3_array[i] = num
        i += 1
        if i == 3:
            char4_array[0] = (char3_array[0] & 0xfc) >> 2
            char4_array[1] = ((char3_array[0] & 0x03) << 4) + ((char3_array[1] & 0xf0) >> 4)
            char4_array[2] = ((char3_array[1] & 0x0f) << 2) + ((char3_array[2] & 0xc0) >> 6)
            char4_array[3] = char3_array[2] & 0x3f
            for k in char4_array:
                ret += base64_chars[k]
            i = 0
    if i != 0:
        for j in range(i, 3):
            char3_array[j] = 0
        char4_array[0] = (char3_array[0] & 0xfc) >> 2
        char4_array[1] = ((char3_array[0] & 0x03) << 4) + ((char3_array[1] & 0xf0) >> 4)
        char4_array[2] = ((char3_array[1] & 0x0f) << 2) + ((char3_array[2] & 0xc0) >> 6)
        char4_array[3] = char3_array[2] & 0x3f
        for k in range(0, i+1):
            ret += base64_chars[char4_array[k]]
        for j in range(i, 3):
            ret += '='
    return ret

def get_opt_value(ampl_list, median, step):
    # s = 0
    # for i in ampl_list:
    #     s += (i/256)*(i/256)

    # [max(i-step*5, 0):i+(6*step)]
    s = 0
    n = 0
    for i in range(median-5*step, median+6*step, step):
        if i < 0 or i >= len(ampl_list):
            continue
        m=max(ampl_list[i: i+step])/256
        s+=m*m
        n+=1
    
    # LOG.info(s)
    # LOG.info(s/len(ampl_list))

    if n <= 0:
        return 0

    return math.sqrt(s/n)

class OpenTTS(TTS):
    def __init__(self, lang="en-us", config=None):
        if config is None:
            self.config = Configuration.get().get("tts", {}).get("mozilla", {})
        else:
            self.config = config
        super(OpenTTS, self).__init__(lang, self.config,
                                         OpenTTSValidator(self))
        self.url = self.config['url'] + "/api/tts"
        self.type = 'wav'

        self.ntpclient = ntplib.NTPClient()

    def send_speech_wave(self, file):
        LOG.info(f"{time.time()} : 0")
        wave_file = wave.open(file, 'rb')
        LOG.info(f"{time.time()} : 1")
        signal = wave_file.readframes(-1)# Convert audio bytes to integers
        soundwave = np.frombuffer(signal, dtype='int16')# Get the sound wave frame rate


        # TODO : target framerate instead of static step 
        framerate = wave_file.getframerate()# Find the sound wave timestamps
        step = 100
        time_step = step / framerate

        LOG.info(f"{time.time()} : 2")
        soundwave_compressed = (int(get_opt_value(soundwave, i, step)) for i in range(0, len(soundwave), step))
        LOG.info(f"{time.time()} : 3")

        # bytes_send = bytearray(int(len(soundwave)/step)+1)
        # LOG.info(f"{time.time()} : 3.5")
        # for i, ampl in enumerate(soundwave_compressed):
        #     bytes_send[i] = ampl
        #     bytes_send[i] = ampl.to_bytes(1, "little")
        # LOG.info(f"{i}")
        to_send = b64encode(soundwave_compressed)
        LOG.info(f"{time.time()} : 4")
        
        res = self.ntpclient.request('fr.pool.ntp.org', version=3)
        t = res.tx_time 
        LOG.info(t)
        # t=time.time()
        play_timestamp = (t+1)

        message_content = {
            "play_timestamp": int(play_timestamp * 1000 + 30),
            
            "timestep": time_step * 1000, # in ms 
            "soundwave": to_send
        }

        LOG.info(f"Sent timestamp : {message_content['play_timestamp']/1000}")

        LOG.info(f"Sending speech_wave")
        self.bus.emit(Message("speech_wave", data=message_content))
        wave_file.close()

        try:
            res = self.ntpclient.request('fr.pool.ntp.org', version=3)
            t = res.tx_time 
            time.sleep(play_timestamp - t)
        except ValueError:
            LOG.info("VALUE ERROR !!")
            pass        

    # def begin_audio(self, wav_file):
    #     pass

    def get_tts(self, sentence, wav_file):
        response = requests.get(self.url, params={'text': sentence, 'voice': "nanotts:fr-FR", "lang": "fr", "vocoder": "medium", "cache": False})

        with open(wav_file, 'wb') as f:
            f.write(response.content)

        # self.send_speech_wave(wav_file)
            
        return (wav_file, None)  # No phonemes

class OpenTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(OpenTTSValidator, self).__init__(tts)

    def validate_dependencies(self):
        pass

    def validate_lang(self):
        # TODO
        pass

    def validate_connection(self):
        url = self.tts.config['url']
        response = requests.get(url)
        if not response.status_code == 200:
            raise ConnectionRefusedError

    def get_tts_class(self):
        return OpenTTS
