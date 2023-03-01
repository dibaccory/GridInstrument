#!/usr/bin/python
#
# Quick usage example of "grid_instrument" with MIDI output port.
# Works with all Launchpads: Mk1, Mk2, S/Mini, Pro, XL and LaunchKey
# 
#
# David Hilowitz 1/15/19
# decided.ly / davehilowitz.com
#

from grid_instrument import GridInstrument
import rtmidi
import time

CC_CH14 = "0x9D"
CC_CH6 = "B5"
user_mode = "110"

def note_callback(messageType, midiNote, velocity):
	if messageType == "note_on":
		midiout.send_message([0x9D, midiNote, velocity])
	elif messageType == "note_off":
		midiout.send_message([0x8D, midiNote, velocity])

# Create a MIDI output port
midiout = rtmidi.MidiOut()
available = midiout.get_ports()
#midiout.list_output_ports()
midiout.open_virtual_port("LP Extension")

try:
	# Set up GridInstrument
	instrument = GridInstrument()
	instrument.intro_message = '8=D'
	instrument.note_callback = note_callback
	instrument.launchpad_pro_velocity_multiplier = 2.5
	instrument.min_velocity = 100
	instrument.max_velocity = 100
	instrument.default_velocity = 100

	instrument.start()
	#note_callback(CC_CH14, user_mode, "7F")

except KeyboardInterrupt:
	print("Ending program...")
	del midiout