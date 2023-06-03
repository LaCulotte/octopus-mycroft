source .venv/bin/activate
test=$@
python -m mycroft.messagebus.send speak "{\"utterance\" : \"$test\"}"
#python -m mycroft.messagebus.send speak "{\"utterance\" : \"$(cat text.txt)\"}"
