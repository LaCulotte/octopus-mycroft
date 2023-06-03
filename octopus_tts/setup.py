#!/usr/bin/env python3
from setuptools import setup

PLUGIN_ENTRY_POINT = 'octopus_tts = octopus_tts:OpenTTS'
setup(
    name='octopus_tts',
    packages=['octopus_tts'],
    keywords='octopus plugin tts',
    entry_points={'mycroft.plugin.tts': PLUGIN_ENTRY_POINT},
    requires=["wave"]
)