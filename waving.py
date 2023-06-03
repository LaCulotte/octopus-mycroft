import wave
import numpy as np
import matplotlib.pyplot as plt

import base64

# Open wav file and read frames as bytes
sf_filewave = wave.open('test.wav', 'r')
signal_sf = sf_filewave.readframes(-1)# Convert audio bytes to integers
soundwave_sf = np.frombuffer(signal_sf, dtype='int16')# Get the sound wave frame rate
framerate_sf = sf_filewave.getframerate()# Find the sound wave timestamps
# f, ax = plt.subplots(figsize=(15, 3))# Setup the title and axis titles

def get_max_ampl(l):
    i_max = 0
    m = abs(l[0])
    for i, v in enumerate(l[1:]):
        if abs(v) > m:
            i_max = i
            m = abs(v)

    return l[i]


step = 100
th = 200
# soundwave_sf = [abs(v) for i, v in enumerate(soundwave_sf)]
# for i in range(len(soundwave_sf) - 1, 0, -1):
#     if soundwave_sf[i] >= th:
#         break

# soundwave_sf = soundwave_sf[:i]

time_sf = np.linspace(start=0,
                      stop=len(soundwave_sf)/framerate_sf,
                      num=len(soundwave_sf))# Set up plot

soundwave_sf_2 = (max(soundwave_sf[(i//step)*step:((i//step )+ 1)*step]) for i, _ in enumerate(soundwave_sf))
soundwave_sf_3 = [soundwave_sf[(i//step)*step] for i, _ in enumerate(soundwave_sf)]

soundwave_sf_2 = list(soundwave_sf_2)
soundwave_send = [int(soundwave_sf_2[i]/256) for i in range(0, len(soundwave_sf_2), step)]

soundwave_send_uncompressed = []
for i in soundwave_send:
    for _ in range(step):
        soundwave_send_uncompressed.append(i * 256)

for _ in range(len(soundwave_send_uncompressed), len(time_sf)):
    soundwave_send_uncompressed.append(soundwave_send_uncompressed[-1])
soundwave_send_uncompressed = soundwave_send_uncompressed[:len(time_sf)]


print(len(soundwave_send_uncompressed))
print(soundwave_send)
th = 1
for i in range(len(soundwave_send) - 1, 0, -1):
    if soundwave_send[i] >= th:
        break

soundwave_send = soundwave_send[:i]

print(len(time_sf))

print(len(soundwave_sf))
print(len(soundwave_sf_2)/step)

import json
print(len(json.dumps(soundwave_send)))
b_send = bytes()
for i in soundwave_send:
    b_send += i.to_bytes(1, "little")

print(len(b_send))
print(len(base64.b64encode(b_send)))
print(len(base64.b64decode(base64.b64encode(b_send))))


# plt.title('Amplitude over Time')
# plt.ylabel('Amplitude')
# plt.xlabel('Time (seconds)')# Add the audio data to the plot

# plt.plot(time_sf, soundwave_sf, label='Warm Memories', alpha=1)
# # plt.plot(time_sf, soundwave_sf_2, label='estimated', alpha=0.5)
# # plt.plot(time_sf, soundwave_sf_3, label='estimated 2', alpha=0.1)

# plt.legend()
# plt.show()

plt.title('Amplitude over Time')
plt.ylabel('Amplitude')
plt.xlabel('Time (seconds)')# Add the audio data to the plot

plt.scatter(time_sf, soundwave_sf, label='Warm Memories', alpha=1)
plt.scatter(time_sf, soundwave_sf_2, label='estimated', alpha=1, s=1)
# plt.plot(time_sf, soundwave_sf_3, label='estimated 2', alpha=0.1)

plt.legend()
plt.show()

# plt.title('Amplitude over Time')
# plt.ylabel('Amplitude')
# plt.xlabel('Time (seconds)')# Add the audio data to the plot

# plt.scatter(time_sf, soundwave_sf, label='Warm Memories', alpha=1)
# # plt.plot(time_sf, soundwave_sf_2, label='estimated', alpha=0.5)
# plt.scatter(time_sf, soundwave_sf_3, c="red", label='estimated 2', alpha=1)

# plt.legend()
# plt.show()

plt.title('Amplitude over Time')
plt.ylabel('Amplitude')
plt.xlabel('Time (seconds)')# Add the audio data to the plot

plt.scatter(time_sf, soundwave_sf, label='Warm Memories', alpha=1)
# plt.plot(time_sf, soundwave_sf_2, label='estimated', alpha=0.5)
plt.scatter(time_sf, soundwave_send_uncompressed, c="red", label='estimated 2', alpha=1, s=1)

plt.legend()
plt.show()

plt.title('Amplitude over Time')
plt.ylabel('Amplitude')
plt.xlabel('Time (seconds)')# Add the audio data to the plot

# plt.plot(time_sf, soundwave_sf_2, label='estimated', alpha=0.5)
plt.scatter(time_sf, soundwave_sf_2, label='estimated 2', alpha=1, s=1)
plt.scatter(time_sf, soundwave_send_uncompressed, c="red", label='estimated 2', alpha=1, s=1)

plt.legend()
plt.show()
