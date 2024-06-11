import time
import random
import math
from itertools import product
import numpy as np
import sys
from .colors import *
from .layout_maker import *
from .scales import *
from .constants import *
from .chording import Chord

try:
	from grid_instrument import lp as launchpad
except ImportError:
	try:
		print("import error, use native")
		#import launchpad_py as launchpad
	except ImportError:
		sys.exit("error loading launchpad.py")



INIT_SCALE = CHORD.scale.copy()

SCALE_NAMES = list(SCALE.keys())

PAD_MODES = {
	"chord": {
		"default": PadLayout(CHORD_LAYOUT["default"], "chord", INIT_SCALE)
	}
}

SCALE_POS = [ 
	(2,2), (1,3), (2,3), (3,3), 
	(1,2), (1,1), (2,1), (3,1),
	(3,2), (7,2), (8,3), (7,3), 
	(6,3), (8,2), (8,1), (7,1), 
	(6,1), (6,2)]

MODE_POS = [ (4,3), (5,3), (4,2), (5,2) ]

SETTINGS = {
	"key": sorted((
				(1,7),  (2,7),  	(4,7), (5,7), (6,7), 
			(1,6), (2,6), (3,6), (4,6), (5,6), (6,6), (7,6)
	)),
	"layout": ((5,8),(6,8),(7,8),(8,8)), 

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

		"base_minor": [("Minor", 		(7,2))],
		"minor": [
			("Melodic Minor", 			(8,3)),
			("Harmonic Minor",	 		(7,3)),
			("Neopolitan Minor", 		(6,3)),
			("Minor Pentatonic", 		(8,2)),
		],
		"jazz_minor": [
			("9 Harmonic Major Blues",	(8,1)),
			("m7b5 Dim. Scale",			(7,1)),
			("Diminished", 				(6,1)),
			("Minor Blues", 			(6,2)),
		]
	},

	"mode": {#( (4,3), (5,3), (4,2), (5,2) ),
		"reset":  (4,3),
		"up": 		(5,3),
		"down": 	(5,2),
		"fif":	 	(4,2)
	},
	#"layout": [(8,6), (8,7), (8,8)] update to left/right arrows?
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

	#NOTE_MODE_OFFSET
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

	_chord_mode = False
	_chord = CHORD
	_active_scale = _chord.scale
	_active_mode = PAD_MODES["chord"]
	_active_mode_layout = PAD_MODES["chord"]["default"]

	_active_notes = []
	_pressed_pads = []
	_pressed_notes = []
	_pressed_buttons = []
	_pressed_chords = [[]] * 90 #TODO: initalize this better
	_grid_octave = 3
	_scale_key = 0
	
	_layout_index = 1
	_layout_name = GRID_LAYOUT[0][0]
	_layout_offset = GRID_LAYOUT[0][1]


	
	_launchpad_mode = "notes" #modes: notes, settings, chord
	_LED_mode = "Pressed" #modes: Pressed, fireworks, pattern by interval?
	

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
			self._scroll_text(self.intro_message, NOTE_COLORS["settings"]["scale_selected"])
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
				x = but[0] + 1
				y = (8 - but[1]) + 1 #why invert this??
				pressed = (but[2] > 0) or (but[2] == True)

				if self._launchpad_mode == "notes":
					self._note_mode_handler(x,y, pressed, but[2])

				elif self._launchpad_mode == "chord":
					self._chord_mode_handler(x,y, pressed, but[2])

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
						
					elif (x,y) in SCALE_POS:
						scales = [ scale for key in SETTINGS["scale"].keys() for scale in SETTINGS["scale"][key] ]
						name = [t[0] for t in scales if (x,y) == t[1]]
						if pressed:
							self._highlight_keys_in_scale()
						else:
							self._active_scale_button_pressed(*name)
						self._highlight_keys_in_scale()


					elif (x,y) in MODE_POS and pressed:
						mode_inc = 0
						if (x,y) == SETTINGS["mode"]["reset"]:
							mode_inc = 0
						elif (x,y) == SETTINGS["mode"]["up"]:
							mode_inc = 1
						elif (x,y) == SETTINGS["mode"]["down"]:
							mode_inc = -1
						elif (x,y) == SETTINGS["mode"]["fif"]:
							if 	 7 in self._active_scale["span"]:
								mode_inc = self._active_scale["span"].index(7)
							elif 6 in self._active_scale["span"]:
								mode_inc = self._active_scale["span"].index(6)

						self._update_scale(mode_inc=mode_inc)
						

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
			i = self._layout_index
			self._layout_index = (i - 1)%len(self.GRID_LAYOUT) if i > 0 else len(self.GRID_LAYOUT)-1
			#self.GRID_LAYOUT = self.GRID_LAYOUT[-1:] + self.GRID_LAYOUT[:-1]
			self._layout_name, self._layout_offset = self.GRID_LAYOUT[i]
			self._color_buttons()
		elif (x,y) == (4,9) and pressed:
			i = self._layout_index
			self._layout_index = (i + 1)%len(self.GRID_LAYOUT) if i < len(self.GRID_LAYOUT) else 0
			#self.GRID_LAYOUT = self.GRID_LAYOUT[-1:] + self.GRID_LAYOUT[:-1]
			self._layout_name, self._layout_offset = self.GRID_LAYOUT[i]
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

	def _chord_mode_handler(self, x, y, pressed, lp_vel):
		self._chord_mode = False
		#TODO: create a USER_BUTTON_PRESSED flag to denote the xy of the user button being pressed. If not none then true
		#if self._active_mode_layout.get_pad(x,y).type in ["user", "chord", "scale"]:
		if (x < 9) and (y < 9):
			if pressed:
				velocity = self.default_velocity
				if self._launchpad_model == "Pro":
					velocity = min(lp_vel * self.launchpad_pro_velocity_multiplier, self.max_velocity)
				#TODO: integrate a use for self._active_mode_layout.get_pad(x,y).data
				#for user, chord, and scale, data contains scale degrees
				self._pad_pressed(x, y, velocity)
			else:
				self._pad_released(x, y)

	def _global_func_handler(self, x, y, pressed):
		#Change sample mode??
		if pressed and (x,y) in [(1,9), (2,9)]:
			if self._launchpad_mode == "notes":
				self._launchpad_mode = "chord"
			elif self._launchpad_mode == "chord":
				self._launchpad_mode = "notes"
			self.lp.Reset()
			self._color_buttons()

		elif (x,y) == (9,8):
			if pressed:
				self._prev_mode = self._launchpad_mode
				self._launchpad_mode = "settings"
				self.lp.Reset()
				self._color_buttons()
			else:
				self._launchpad_mode = self._prev_mode
				self._color_buttons()

		elif pressed and (x,y) == (9,6):
			if self._grid_octave < 8:
				self._grid_octave += 1

		elif pressed and (x,y) == (9,5):
			if self._grid_octave > 0:
				self._grid_octave -= 1

	def _color_note_button(self, x, y, note_interval=1, pressed=False):
		if pressed:
			key =  "tonic" if note_interval%12 == 0 else "on"
		elif note_interval not in self._active_scale["span"]:
			key = "out_scale"
		elif note_interval == 0:
			key = "root"
		else:
			key = "in_scale"

		self._color_button(x, y, NOTE_COLORS["note"][key])

	def _color_mutual_note_pads(self, pad):
		mutual_pads = [*set(p for note in pad.data for p in self._active_mode_layout.get_pads_by_note(note))]
		
		[self._color_button(*p.xy, p.get_color(is_active=pad.pressed, is_root=(p.xy[1] == pad.xy[1]))) for p in mutual_pads]

	def _color_button(self, x,y, color):
		lpX = x - 1
		lpY = -1 * (y - 9)
		#TODO: Convert RGB to RG if Mk1
		self.lp.LedCtrlXY(lpX, lpY, *color)

	def _scroll_text(self, text, colorKey):
		self.lp.LedCtrlString(text, *colorKey, self.lp.SCROLL_LEFT, 20)

	#Colors whole layout on mode change. Like an initalization for each mode
	def _color_buttons(self):
		if self._launchpad_mode == "notes":
			for x in range(1, 9):
				for y in range(1, 9):
					self._color_note_button(x, y, self._get_note_interval(x, y), (self._get_midi_note(x, y) in self._pressed_notes))

		elif self._launchpad_mode == "chord":
			for xy in product(range(1,9),range(1,9)):
				pad =  self._active_mode_layout.get_pad(*xy)
				c = pad.color
				self._color_button(*xy, c)
		#Settings > Scales			
		elif self._launchpad_mode == "settings":

			for i, scale_xy in enumerate(SETTINGS["layout"]):
				self._color_button(*scale_xy, NOTE_COLORS["settings"]["layout" + ("_selected" if self._layout_name == self.GRID_LAYOUT[i][0] else "")] )
		
			#for i in GRID_KEY.len
			#	colorbutton(GRID_KEY[i], "on" if _gridkey = i else "pff")
			for i, scale_xy in enumerate(SETTINGS["key"]):
				self._color_button(*scale_xy, NOTE_COLORS["settings"]["key" + ("_selected" if self._scale_key == i else "")] )

			for scale_type, scale_list in SETTINGS["scale"].items():
				for name, scale_xy in scale_list:
					if self._active_scale["name"] == name:
						self._color_button(*scale_xy, NOTE_COLORS["settings"]["scale_selected"])
					else:
						self._color_button(*scale_xy, NOTE_COLORS["settings"]["scale"][scale_type])
			
			self._color_button(*SETTINGS["mode"]["reset"], Color.GREEN) 
			self._color_button(*SETTINGS["mode"]["fif"], 	Color.BLUE) 
			self._color_button(*SETTINGS["mode"]["up"], 	Color.WHITE) 
			self._color_button(*SETTINGS["mode"]["down"], 	Color.WHITE) 

		self._color_button(9, 6, NOTE_COLORS["note"]["on"]) # octave up
		self._color_button(9, 5, NOTE_COLORS["note"]["on"]) # octave down
		self._color_button(9, 8, NOTE_COLORS["note"]["on"]) # settings
		

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
			deg = (self._active_scale["span"].index(inv % 12) + (self._get_scale_length()) * (inv // 12)) if self._layout_name != "Chromatic" else inv
			#print("Scale degree of inv ", inv, ":\t", deg)
			return deg

	def _get_note_interval(self, x, y):
		scale_degree = self._get_scale_degree(x, y)
		return self._active_scale["span"][scale_degree] if self._layout_name != "Chromatic" else scale_degree

	def _get_midi_note(self, x, y):
		note_octave = self._XY_to_grid_index(x, y) // self._get_scale_length()
		return self._minimum_note_on_board() + self._get_note_interval(x, y) + 12 * note_octave

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

	def _XY_to_button(self, x, y):
		return 8*(y-1) + (x-1)

	def get_currently_playing_midi_notes(self):
		notes = []
		for button_number in self._pressed_buttons:
			x, y = self._button_to_XY(button_number)
			midi_note = self._get_midi_note(x, y)
			if midi_note not in notes:
				notes.append(midi_note)
		return notes
	
	def _pad_pressed(self, x, y, velocity):

		button_number = self._XY_to_button(x, y)
		self._pressed_buttons.append(button_number)

		pad = self._active_mode_layout.get_pad(x, y)
		pad.pressed = True
		if pad.type == "note" and not self._active_mode_layout.get_pads_by_type("lock")[0].data:
			[usr_pad.data.append(pad.data[0]) if pad.data[0] not in usr_pad.data else usr_pad.data.remove(pad.data[0]) for usr_pad in self._active_mode_layout.get_pressed_pads("user")]
		
		if pad.type in ["note", "chord", "user"]:
			#if [], then it won't play anything
			[(self._note_on(note, velocity)) for note in pad.data]
			self._color_mutual_note_pads(pad)
		elif pad.type == "sustain":
			pad.toggle()
		elif pad.type == "lock":
			pass

		self._color_button(*pad.xy, pad.get_color())

	def _note_on(self, note, velocity):

		if note is None:
			return
		
		midi_note = self._minimum_note_on_board() + note

		if note not in self._active_notes:
			self.note_callback("note_on", midi_note, velocity)
			self._active_notes.append(note)

		else:
			#play note again
			self.note_callback("note_off", midi_note, velocity)
			self.note_callback("note_on", midi_note, velocity)

	def _pad_released(self, x, y):

		button_number = self._XY_to_button(x, y)
		if button_number not in self._pressed_buttons:
			return
		
		pad = self._active_mode_layout.get_pad(x, y)	
		pad.pressed = False

		if pad.type in ["note", "chord", "user"]:
			#If sustain is active, don't keep all MIDI notes on
			if self._active_mode_layout.get_pads_by_type("sustain")[0].data:
				return
			#if [], then it won't play anything
			all_pressed_pad_notes = self._active_mode_layout.get_notes_for_pressed_pads()
			[(self._note_off(note))  for note in pad.data if note not in all_pressed_pad_notes]
			self._color_mutual_note_pads(pad)
		elif pad.type == "sustain":
			pad.toggle()
			#note_off for all notes that are not pressed but the corresponding MIDI note is playing
			notes = self._active_notes.copy()
			all_pressed_pad_notes = self._active_mode_layout.get_notes_for_pressed_pads()
			[self._note_off(note) for note in notes if note not in all_pressed_pad_notes]

		elif pad.type == "lock":
			pad.toggle()

		
		self._pressed_buttons.remove(button_number)

		self._color_button(*pad.xy, pad.get_color())

	def _note_off(self, note):
		midi_note = self._minimum_note_on_board() + note
		self.note_callback('note_off', midi_note, 0)

		if note in self._active_notes:
			self._active_notes.remove(note)
		#print("NOTE OFF:\t", midi_note)


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


	def _update_scale(self, name=None, mode_inc=None):
		if name is not None:
			self._active_scale["name"] = name
			self._active_scale["span"] = SCALE[self._active_scale["name"]]
			#gross lol TODO: would ordered dict fix this?
			i = self.GRID_LAYOUT.index(self.SCALE_LAYOUT)
			self.GRID_LAYOUT[i][1] = len(self._active_scale["span"])
			self.SCALE_LAYOUT[1] = len(self._active_scale["span"])
			print("new scale: ", self._active_scale["span"])

		if mode_inc is not None:
			#new_scale = {"name": self.scale["name"], "mode": 0, "span": []}
			if mode_inc != 0:
				shifted_span = self._active_scale["span"][mode_inc:] + self._active_scale["span"][:mode_inc]
				self._active_scale["mode"] += mode_inc
				self._active_scale["span"] = [(interval - shifted_span[0])%12 for interval in shifted_span]
			else:
				self._active_scale["mode"] = 0
				self._active_scale["span"] = SCALE[self._active_scale["name"]]

		self._chord.update_scale(self._active_scale)
		self._active_mode_layout.update_scale(self._active_scale)
		#print(self._active_scale)

	def _active_scale_button_pressed(self, name):
		#scale_index = (x - 1) + ((4 - y) * 8)
		#self._active_scale["name"] = SCALE_NAMES[index]
		self._update_scale(name)
		self._pressed_chords = [[]] * 2 * self._XY_to_grid_index(8,8)
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
				self._color_button(x, y, NOTE_COLORS["note"]["in_scale"])