import time
import random
import math
import collections
import numpy as np
import sys
from .scales import *
from .chording import Chord

try:
	from grid_instrument import lp as launchpad
except ImportError:
	try:
		print("import error, use native")
		#import launchpad_py as launchpad
	except ImportError:
		sys.exit("error loading launchpad.py")


SCALE_NAMES = list(SCALE.keys())

SETTINGS = {
	"key": sorted([
				(1,7),  (2,7),  	(4,7), (5,7), (6,7), 
			(1,6), (2,6), (3,6), (4,6), (5,6), (6,6), (7,6)
		]),
	"scale": {
		"base_major": [("Major", 		(2,2))],
		"major": [
			("Melodic Major", 			(1,3)),
			("Harmonic Major",	 		(2,3)),
			("Neopolitan Major", 		(3,3)),
			("Major Pentatonic", 		(1,2)),
		],
		"jazz_major": [
			("9 Melodic Major Blues",	(1,1)),
			("Bebop Major",	 			(2,1)),
			("Bebop Dominant", 			(3,1)),
			("Major Blues", 			(3,2)),
		],

		"base_minor": [("Minor", 		(2,2))],
		"minor": [
			("Melodic Minor", 			(8,3)),
			("Harmonic Minor",	 		(7,3)),
			("Neopolitan Minor", 		(6,3)),
			("Minor Pentatonic", 		(8,2)),
		],
		"jazz_minor": [
			("9 Melodic Major Blues",	(8,1)),
			("Bebop Major",	 			(7,1)),
			("Bebop Dominant", 			(6,1)),
			("Major Blues", 			(6,2)),
		]
	},

	"mode": [
		("reset", 	(4,3))
		("up", 		(5,3))
		("down", 	(4,2))
		("fif", 	(5,2))
	]
	#"layout": [(8,6), (8,7), (8,8)] update to left/right arrows?
}

NOTE_COLORS = {
	"note": {
            "on": 			[0X3F, 0X3F, 0X00],
	        "root": 		[0X20, 0X00, 0X3F],
            "tonic": 		[0X3F, 0X25, 0X00],
            "in_scale": 	[0X03, 0X01, 0X10],
            "out_scale": 	[0X00, 0X00, 0X00]
        },
	"settings": {
        "scale_on": 			[0X00, 0X28, 0X00],
		"scale_off": 			[0X00, 0X0A, 0X00],
        "scale_on": 			[0X00, 0X02, 0X3F],
		"scale_off": 			[0x01, 0X01, 0X05],
		
	}
}

NOTE_COLORS_ol = { 
	"Mk1": { 
		"note.on": [0, 63],    
		"note.root": [3, 0],      
		"note.in_scale": [1, 1],
		"note.out_scale": [0, 0],
		"settingsKeyOff": [0, 4],
		"settingsKeyOn":  [0, 20],
		"settings.key_off": [1, 1],
		"settings.key_on":  [3, 3],
		"settings.scale_off": [0, 1],
		"settings.scale_on":  [0, 3],
		"settings.layout_off": [1, 0],
		"settings.layout_on":  [3, 0],

	}, 
	"Mk2": { 
		
		"note.on": 				[0x3F, 0X3F, 0], 
		#"note.on.alt": 				[0x1F, 0X1F, 0], 
		"note.on.chord_root": 	[0x3F, 0X25, 0], 
		#"note.on.chord_root.alt": 	[0x1F, 0X09, 0], 
		"note.root": 			[0X20, 0, 0x3F], 
		"note.in_scale": 		[0X03, 0X01, 10],
		"note.out_scale":		[0, 0, 0],
		"settingsKeyOff": 		[0, 0X0A, 0],
		"settingsKeyOn":  		[0, 0X28, 0],
		"settings.key_off": 	[0X05, 0, 0],
		"settings.key_on":  	[0X3F, 0X00, 0],
		"settings.scale_off": 	[0x01, 0X01, 0X05],
		"settings.scale_on":  	[0, 0X02, 0X3F],
		"settings.layout_off": 	[0, 0, 0X0F],
		"settings.layout_on":	[0, 0, 0X3F],
	}
}

#TODO: MidiMatrix
class GridInstrument:

	# Constants

	#NOTE: may be cleaner to have each button like this... but it may take some more memory
	#Question: How much more memory would this take compared to what's currently being used?

	#class Button:
	#	def __init__(self, x, y, color=[0,0,0], pressed=False):
	#		self.x = x
	#		self.y = y
	#		self.color = color
	#		self.pressed = pressed
	GRID_LAYOUT = [
		["Scale",		7],
		["Diatonic 4th", 3],
		["Diatonic 5th", 4],
		["Chromatic",	5]
	]

	SCALE_LAYOUT = ["Scale", 7]

	NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

	




	# Settings
	note_callback = None
	func_button_callback = None
	kid_mode = False
	debugging = False
	intro_message = None
	launchpad_pro_velocity_multiplier = 1
	max_velocity = 127
	default_velocity = 100

	# State Variables
	_launchpad_model = None
	lp = None
	
	_active_scale = {
		"name": "Major",
		"mode": 0, #0 is "ionian", but since we aren't dealing with only 7-note scales (diatonic, namely), we index instead
		"span": SCALE["Major"]
	}
	_pressed_notes = []
	_pressed_buttons = []
	_pressed_chords = [[]] * 28 #TODO: initalize this better
	_grid_octave = 3
	_scale_key = 0
	
	_layout_index = 1
	_layout_name = GRID_LAYOUT[0][0]
	_layout_offset = GRID_LAYOUT[0][1]
	
	_launchpad_mode = "notes" #modes: notes, settings, chord
	_LED_mode = "Pressed" #modes: Pressed, fireworks, pattern by interval?
	_chord_mode = False
	_chord = Chord(_active_scale)

	randomButton = None
	randomButtonCounter = 0
	randomButtonModeEnabled = False

	def __init__( self ):
		print("LaunchpadScalemode Initialized!")

	def start( self ):
		self.discover_launchpad(True)
		self._main_loop()
		
	def discover_launchpad(self, keep_checking=False):
		# create an instance
		self.lp = launchpad.Launchpad()
		while self._launchpad_model is None:
			# lp.ListAll()
			# check what we have here and override lp if necessary
			if self.lp.Check( 0, "pro" ):
				self.lp = launchpad.LaunchpadPro()
				if self.lp.Open():
					print("Launchpad Pro")
					self._launchpad_model = "Pro"
					
			elif self.lp.Check( 0, "mk2" ):
				self.lp = launchpad.LaunchpadMk2()
				if self.lp.Open():
					print("Launchpad Mk2")
					self._launchpad_model = "Mk2"    
			else:
				if self.lp.Open():
					print("Launchpad Mk1/S/Mini")
					self._launchpad_model = "Mk1"

			if self._launchpad_model is None:
				if keep_checking is False:
					print("Did not find any Launchpads, meh...")					
					return
				else:
					time.sleep(2)
		if self.intro_message is not None and len(self.intro_message) > 0:
			self._scroll_text(self.intro_message, 'settingsKeyOff')
			pass

	#TODO: Make prettier. Maybe make 
	def _main_loop(self):
		self.lp.ButtonFlush()
		self.lp.Reset()

		self._color_buttons()

		while True:
			time.sleep(0.005) # 5ms wait between loops
			but = self.lp.ButtonStateXY()

			#TODO: Convert to sequencer / Arpeggiator
			if self.randomButtonModeEnabled:
				if self.randomButtonCounter > 30:
					if self.randomButton:
						self._button_released(self.randomButton[0], self.randomButton[1])  
						self.randomButton = None
					# Make a new randomButton
					self.randomButton = [random.randint(1,8), random.randint(1,8)]
					self._button_pressed(self.randomButton[0], self.randomButton[1], 100)
					self.randomButtonCounter = 0
				self.randomButtonCounter = self.randomButtonCounter + 1

			if but != []:
				#TODO: Convert x,y back to original coord state... it's inverted
				x = but[0] + 1
				y = (8 - but[1]) + 1 #why invert this??
				pressed = (but[2] > 0) or (but[2] == True)

				if self._launchpad_mode == "notes":
					self._note_mode_handler(x,y,pressed, but[2])

				#Settings
				elif self._launchpad_mode == "settings":
					self._all_buttons_released()
					#(x,y) < (8,6)
					if (x,y) in SETTINGS["key"] and pressed:
						# Active Key
						self._scale_key = SETTINGS["key"].index((x,y))
						print("Key is ", self.NOTE_NAMES[self._scale_key])

						self.GRID_LAYOUT[self.GRID_LAYOUT.index(self.SCALE_LAYOUT)][1] = len(self._active_scale["span"])
						self._color_buttons()
						
					elif (x,y) in SETTINGS["scale"]:
						if pressed:
							self._highlight_keys_in_scale()
						else:
							self._active_scale_button_pressed(x, y)
						self._highlight_keys_in_scale()

				self._global_func_handler(x,y,pressed)


	def _note_mode_handler(self, x, y, pressed, lp_vel):
		if (x < 9) and (y < 9):
			if pressed:
				velocity = self.default_velocity
				if self._launchpad_model == "Pro":
					velocity = min(lp_vel * self.launchpad_pro_velocity_multiplier, self.max_velocity)

				self._button_pressed(x, y, velocity)
			else:
				self._button_released(x, y)
		elif pressed and (x,y) == (9,3):
			#Chord mode
			#if self._chord is None:
			#	self._chord = Chord(self._active_scale)
			self._chord_mode = not self._chord_mode
			print("CHORD MODE ", ("ON" if self._chord_mode else "OFF"))	
		#TODO: Change tuples to Enumeration for readability
		elif (x,y) == (9,1) and pressed:
			# Clear screen
			self.lp.Reset()
			self._all_buttons_released()
		elif (x,y) == (9,2):
			# Random button mode
			if pressed:
				self.randomButtonModeEnabled = True
				self.randomButton = None
				self.randomButtonCounter = 0
			else:
				self.randomButtonModeEnabled = False
				if self.randomButton:
					self._button_released(self.randomButton[0], self.randomButton[1])
					self.randomButton = None
		elif (x,y) == (3,9) and pressed:
			#self._layout_index = (self._layout_index - 1)%len(self.GRID_LAYOUT)
			self.GRID_LAYOUT = self.GRID_LAYOUT[-1:] + self.GRID_LAYOUT[:-1]
			self._layout_name = self.GRID_LAYOUT[0][0]
			self._layout_offset = self.GRID_LAYOUT[0][1]
			self._color_buttons()
		elif (x,y) == (4,9) and pressed:
			#self._layout_index = (self._layout_index + 1)%len(self.GRID_LAYOUT)
			self.GRID_LAYOUT = self.GRID_LAYOUT[1:] + self.GRID_LAYOUT[:1]
			self._layout_name = self.GRID_LAYOUT[0][0]
			self._layout_offset = self.GRID_LAYOUT[0][1]
			self._color_buttons()
		
		#if (x,y) == (6,8) and self._layout != "Diatonic 4th":
		#	self._layout = "Diatonic 4th"
		#	self._color_buttons()
		#elif (x,y) == (7,8) and self._layout != "Diatonic 5th":
		#	self._layout = "Diatonic 5th"
		#	self._color_buttons()
		#elif (x,y) == (8,8) and self._layout != "Chromatic":
		#	self._layout = "Chromatic"
		#	self._color_buttons()
					
	def _global_func_handler(self, x, y, pressed):
		#Change sample mode??
		if pressed and (x,y) in [(1,9), (2,9)] and (self.kid_mode is not True):
			#self.func_button_callback(x, y, pressed)
			print("SAMPLE CHANGE BUTTON - TODO")
		elif (x,y) == (9,8):
			if pressed:
				self._launchpad_mode = "settings"
				self.lp.Reset()
				self._color_buttons()
			else:
				self._launchpad_mode = "notes"
				self._color_buttons()

		elif pressed and (x,y) == (9,6):
			if self._grid_octave < 8:
				self._grid_octave += 1

		elif pressed and (x,y) == (9,5):
			if self._grid_octave > 0:
				self._grid_octave -= 1

	def _color_note_button(self, x, y, note_interval=1, pressed=False):
		if pressed:
			key = "note.on" + (".chord_root" if note_interval%12 == 0 else "")# + (".alt" if indirect else "")
		elif note_interval not in self._active_scale["span"]:
			key = "note.out_scale"
		elif note_interval == 0:
			key = "note.root"
		else:
			key = "note.in_scale"

		self._color_button(x, y, key)


	def _color_button(self, x,y, color):
		lpX = x - 1
		lpY = -1 * (y - 9)
		self.lp.LedCtrlXY(lpX, lpY, *color)


	#def _color_button(self, x, y, buttonType):
	#	lpX = x - 1
	#	lpY = -1 * (y - 9)
#
	#	if self._launchpad_model == "Mk1":
	#		colorSet = "Mk1"
	#		self.lp.LedCtrlXY(lpX, lpY, NOTE_COLORS[colorSet][buttonType][0], NOTE_COLORS[colorSet][buttonType][1])
	#	else:
	#		colorSet = "Mk2"
	#		self.lp.LedCtrlXY(lpX, lpY, NOTE_COLORS[colorSet][buttonType][0], NOTE_COLORS[colorSet][buttonType][1], NOTE_COLORS[colorSet][buttonType][2])

	def _scroll_text(self, text, colorKey):
		if self._launchpad_model == "Mk1":
			colorSet = "Mk1"
			self.lp.LedCtrlString(text, NOTE_COLORS[colorSet][colorKey][0], NOTE_COLORS[colorSet][colorKey][1], self.lp.SCROLL_LEFT, 20)
		else:
			colorSet = "Mk2"
			self.lp.LedCtrlString(text, NOTE_COLORS[colorSet][colorKey][0], NOTE_COLORS[colorSet][colorKey][1], NOTE_COLORS[colorSet][colorKey][2], self.lp.SCROLL_LEFT, 20)

	#Colors whole layout on mode change. Like an initalization for each mode
	def _color_buttons(self):
		if self._launchpad_mode == "notes":
			for x in range(1, 9):
				for y in range(1, 9):
					self._color_note_button(x, y, self._get_note_interval(x, y), (self._get_midi_note(x, y) in self._pressed_notes))

		#Settings > Scales			
		elif self._launchpad_mode == "settings":

			self._color_button(5, 8, "settings.layout_" + ("on" if self._layout_name == "Scale" else "off"))
			self._color_button(6, 8, "settings.layout_" + ("on" if self._layout_name == "Diatonic 4th" else "off"))
			self._color_button(7, 8, "settings.layout_" + ("on" if self._layout_name == "Diatonic 5th" else "off"))           
			self._color_button(8, 8, "settings.layout_" + ("on" if self._layout_name == "Chromatic" else "off"))                

			#for i in GRID_KEY.len
			#	colorbutton(GRID_KEY[i], "on" if _gridkey = i else "pff")
			key_i = 0
			for x,y in SETTINGS["key"]:
				self._color_button(x,y, "settings.key_" + ("on" if self._scale_key == key_i else "off") )
				key_i +=1

			scale_i = 0
			for scale_type, ar in SETTINGS["scale"].items():

				self._color_button(x,y, NOTE_COLORS[self._launchpad_model][scale_type][scale_name])#"settings.scale_" + ("on" if self._active_scale["name"] == SCALE_NAMES[scale_i] else "off") )
				scale_i +=1

			#scale_i = 0
			#for scale_type, scale_coords in KEY_OPTIONS["settings"]["scale"].items():
			#	scale_key_on = f"settings.scale.{scale_type}.on"
			#	scale_key_off = f"settings.scale.{scale_type}.off"
			#	self._color_button(*scale_coords, scale_key_on if self._active_scale["name"] == SCALE_NAMES[scale_i] else scale_key_off)
			#	scale_i += 1
			
		self._color_button(9, 6, "note.on") # octave up
		self._color_button(9, 5, "note.on") # octave down
		self._color_button(9, 8, "note.on") # settings
		
		if self.kid_mode is not True:
			self._color_button(1, 9, "note.on") # sample down
			self._color_button(2, 9, "note.on") # sample up

	def _is_key_in_scale(self, key):
		return key in self._active_scale["span"]
	
	def _is_interval_in_scale(self, x, y):
		return self._get_note_interval(x, y) in self._active_scale["span"]

	def _minimum_note_on_board(self):
		return ((self._grid_octave + 1) * 12) + self._scale_key

	def _get_scale_length(self):
		return len(self._active_scale["span"]) if self._layout_name != "Chromatic" else 12

	def _XY_to_grid_index(self, x, y):
		offset = self._layout_offset if self._layout_offset < 8 else 8
		return (x-1) + (y-1) * offset

	def _grid_index_to_XY(self, index):
		offset = self._layout_offset if self._layout_offset < 8 else 8
		return (index%offset + 1), (index//offset + 1)

	def _get_scale_degree(self, x=None, y=None, inv=None):
		if x is not None and y is not None:
			return self._XY_to_grid_index(x,y) % self._get_scale_length()
		elif inv is not None:
			#print(inv)
			#There exists a d in span Scale[self._active_scale] s.t. inv%d = 0 , thus inv % 12 will always be indexed
			deg = (self._active_scale["span"].index(inv % 12) + (self._get_scale_length()) * (inv // 12)) if self._layout_name != "Chromatic" else inv

			#print("Scale degree of inv ", inv, ":\t", deg)
			return deg

	def _get_note_interval(self, x, y):
		scale_degree = self._get_scale_degree(x, y)
		return self._active_scale["span"][scale_degree] if self._layout_name != "Chromatic" else scale_degree

	def _get_midi_note(self, x, y):
		note_octave = self._XY_to_grid_index(x, y) // self._get_scale_length()
		return self._minimum_note_on_board() + self._get_note_interval(x, y) + 12 * note_octave

	def get_note_info(self, x, y):
		pass

	def diff(first, second):
		second = set(second)
		return [item for item in first if item not in second]
	
	def get_scale(self):
		return self._active_scale
	
	def _in_matrix_bounds(self, i, j):
		return 0 < i < 9 and 0 < j < 9

	def _get_buttons_for_midi_note(self, x, y):
		os = self._layout_offset
		possible_btns = [(x-2*os,y+2), (x-os,y+1), (x,y), (x+os,y-1), (x+2*os, y-2)]
		return [ btn for btn in possible_btns if self._in_matrix_bounds(btn[0], btn[1]) ]
	
	def _button_to_XY(self, btn):
		return (btn%8 + 1), (btn//8 + 1)

	def get_currently_playing_midi_notes(self):
		notes = []
		for button_number in self._pressed_buttons:
			x, y = self._button_to_XY(button_number)
			midi_note = self._get_midi_note(x, y)
			if midi_note not in notes:
				notes.append(midi_note)
		return notes

	# This takes 1-based coordinates with 1,1 being the lower left button
	def _button_pressed(self, x, y, velocity):
		
		button_number = (x-1)  + ((y-1) * 8)
		pressed_grid_index = self._XY_to_grid_index(x, y)
		print(f"Button:\t{button_number}\t index\t: {pressed_grid_index} \t(x,y):\t({x},{y})")
		self._pressed_buttons.append(button_number)

		pressed_MIDI_note = self._get_midi_note(x, y)
		scale_degree = self._get_scale_degree(x, y)
		btn_inv = self._get_note_interval(x, y)

		if self._chord_mode:
			#if Chromatic, then scale_degree == btn_inv
			is_in_scale = self._is_key_in_scale(btn_inv)
			new_chord = self._chord(self._active_scale["span"].index(btn_inv) if (scale_degree == btn_inv and is_in_scale) else scale_degree, in_scale=is_in_scale)
			root = pressed_MIDI_note - btn_inv
			chord_notes = [root + i for i in new_chord]
			#if chord_notes not in self._pressed_chords:
			print("CHORD:", new_chord)
		
			#TODO: Pythonize
			for note_pos in new_chord:
				note = root + note_pos
				#chord_notes.append(note)
				#print(f"new_btn_num = {button_number} - {scale_degree} + self._get_scale_degree(inv={note_pos})")
				new_grid_index = pressed_grid_index - scale_degree + self._get_scale_degree(inv=note_pos)
				#new_btn_num = button_number - scale_degree + self._get_scale_degree(inv=note_pos)
				print("\tNew grid index\t", new_grid_index)
				ntx , nty = self._grid_index_to_XY(new_grid_index)
				#ntx , nty = self._button_to_XY(new_grid_index)
				print(ntx, nty)
				self._play_note(ntx,nty, note, velocity, btn_inv)

			if chord_notes not in self._pressed_chords:
				self._pressed_chords[pressed_grid_index] = chord_notes

		else:
			self._play_note(x,y, pressed_MIDI_note, velocity, btn_inv)

		#print("end _button_pressed: ", self.get_currently_playing_midi_notes())

	# This takes 1-based coordinates with 1,1 being the lower left button
	def _button_released(self, x, y):
		button_number = (x-1)  + ((y-1) * 8)
		released_grid_index = self._XY_to_grid_index(x, y)
		if button_number not in self._pressed_buttons:
			return

		released_MIDI_note = self._get_midi_note(x, y)
		#print("Pressed buttons: ", self._pressed_buttons)
		self._pressed_buttons.remove(button_number)
		scale_degree = self._get_scale_degree(x, y)
		btn_inv = self._get_note_interval(x, y)

		if self._chord_mode:
			is_in_scale = self._is_key_in_scale(btn_inv)
			released_chord = self._chord(self._active_scale["span"].index(btn_inv) if (scale_degree == btn_inv and is_in_scale) else scale_degree, in_scale=is_in_scale)
			root = released_MIDI_note - btn_inv

			chord_notes = [root + i for i in released_chord]

			if chord_notes in self._pressed_chords:
				self._pressed_chords[released_grid_index] = []

			new_pressed_notes = [note_interval for chord in self._pressed_chords for note_interval in chord]

			pressed_grid_index = self._XY_to_grid_index(x, y)

			for note_pos in released_chord:
				note = root + note_pos
				#chord_notes.append(note)
				if note not in new_pressed_notes:
					new_grid_index = pressed_grid_index - scale_degree + self._get_scale_degree(inv=note_pos)
					#new_btn_num = button_number - scale_degree + self._get_scale_degree(inv=note_pos)
					ntx , nty = self._grid_index_to_XY(new_grid_index)
					#ntx , nty = self._button_to_XY(new_grid_index)
					self._stop_note(ntx, nty, note)
					
				else:
					#keep playing if note is still in active chord
					pass

			
		else:
			new_pressed_notes = self.get_currently_playing_midi_notes()
			if released_MIDI_note not in new_pressed_notes:
				self._stop_note(x, y, released_MIDI_note)
		
		self._pressed_notes = new_pressed_notes
		#print("end _button_released: ", self.get_currently_playing_midi_notes())

	def _play_note(self, x,y, midi_note, velocity, pressed_note_interval):

		if midi_note not in self._pressed_notes:
			note_inv = self._get_note_interval(x, y)
			self.note_callback("note_on", midi_note, velocity)
			buttons = self._get_buttons_for_midi_note(x,y)

			for btn_x, btn_y in buttons:
				self._color_note_button(btn_x, btn_y, abs(pressed_note_interval - note_inv), pressed=True)

			self._pressed_notes.append(midi_note)
		else:
			#play note again
			self.note_callback("note_off", midi_note, velocity)
			self.note_callback("note_on", midi_note, velocity)

		#print("NOTE ON:\t", midi_note)


	def _stop_note(self, x,y, midi_note):
		self.note_callback('note_off', midi_note, 0)
		buttons = self._get_buttons_for_midi_note(x,y)

		for btn_x, btn_y in buttons:
			self._color_note_button(btn_x, btn_y, self._get_note_interval(btn_x, btn_y))

		#print("NOTE OFF:\t", midi_note)


	# Todo, we should actually 
	def _all_buttons_released(self):
		for midi_note in self._pressed_notes:
			self.note_callback('note_off', midi_note, 0)

		del self._pressed_notes[:]
		del self._pressed_buttons[:]
		self._pressed_chords = [[]] * self._XY_to_grid_index(8,8)


	def _update_scale(self, index=None, mode=0):
		if index is not None:
			self._active_scale["name"] = SCALE_NAMES[index]
			self._active_scale["span"] = SCALE[self._active_scale["name"]]
			#gross lol TODO: would ordered dict fix this?
			i = self.GRID_LAYOUT.index(self.SCALE_LAYOUT)
			self.GRID_LAYOUT[i][1] = len(self._active_scale["span"])
			self.SCALE_LAYOUT[1] = len(self._active_scale["span"])
			print("new scale: ", self._active_scale["span"])

		if mode > 0:
			self._active_scale["mode"] += mode #update scale mode 		(self.scale_mode)
			mode_interval = self._active_scale["mode"]
			rotated_scale = self._active_scale["span"][-mode:] + self._active_scale["span"][:-mode]
			self._active_scale["span"] = [ (x+12 - mode_interval)%12 for x in rotated_scale ]
			print(rotated_scale)

		self._chord.update_scale(self._active_scale)
		print(self._active_scale)

	def _active_scale_button_pressed(self, x, y):
		scale_index = (x - 1) + ((4 - y) * 8)
		#self._active_scale["name"] = SCALE_NAMES[index]
		self._update_scale(scale_index)
		self._pressed_chords = [[]] * self._XY_to_grid_index(8,8)
		print(self._active_scale)
		if self._chord_mode:
			pass
			#self._chord.update_scale(self._active_scale)

		self._all_buttons_released()
		self._color_buttons()

	def _highlight_keys_in_scale(self):
		root = self._scale_key
		for key in range(root+1, root+11):
			key %= 12
			if self._is_key_in_scale(key):
				x = SETTINGS["key"][key][0]
				y = SETTINGS["key"][key][1]
				self._color_button(x, y, "note.in_scale")