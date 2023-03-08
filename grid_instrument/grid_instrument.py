import time
import random
import math
import collections
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


GRID_LAYOUT_OFFSET = {
	"Diatonic 4th": 3,
	"Diatonic 5th": 4,
	"Chromatic":	5
}

KEY_OPTIONS = {
	"settings": {
		"key": sorted([
				 	(1,7),  (2,7),  	(4,7), (5,7), (6,7), 
				(1,6), (2,6), (3,6), (4,6), (5,6), (6,6), (7,6)
			]),
		"scale": [
			(1,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (8,4),
			(1,3), (2,3), (3,3), (4,3), (5,3), (6,3), (7,3), (8,3),
			(1,2), (2,2), (3,2), (4,2), (5,2), (6,2), (7,2), (8,2),
			(1,1), (2,1)
			],
		#"layout": [(8,6), (8,7), (8,8)] update to left/right arrows?
	}
	#TODO note mode options
}

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


	WHITE_KEYS = SCALE['Major']

	NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

	NOTE_COLORS = { 
		"Mk1": { 
			"note.pressed": [0, 63],    
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
			"note.pressed": 		[0x3F, 0X3F, 0], 
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
	_pressed_notes = []
	_pressed_buttons = []
	_pressed_chords = []
	_active_scale = 'Major'
	_grid_octave = 3
	_active_key = 0
	_grid_layout = "Diatonic 4th" # possible values are "Diatonic 4th" and "Chromatic"
	_launchpad_mode = "notes" # possible values are "notes" and "settings"
	_chord_mode = False
	_chord = None

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

	def _main_loop(self):
		self.lp.ButtonFlush()
		self.lp.Reset()

		self._color_buttons()

		randomButton = None
		randomButtonCounter = 0
		randomButtonModeEnabled = False

		while True:
			time.sleep(0.005) # 5ms wait between loops
			but = self.lp.ButtonStateXY()

			#TODO: Convert to sequencer / Arpeggiator
			if randomButtonModeEnabled:
				if randomButtonCounter > 30:
					if randomButton:
						self._button_released(randomButton[0], randomButton[1])  
						randomButton = None
					# Make a new randomButton
					randomButton = [random.randint(1,8), random.randint(1,8)]
					self._button_pressed(randomButton[0], randomButton[1], 100)
					randomButtonCounter = 0
				randomButtonCounter = randomButtonCounter + 1

			if but != []:
				#TODO: Convert x,y back to original coord state... it's inverted
				x = but[0] + 1
				y = (8 - but[1]) + 1 #why invert this??
				pressed = (but[2] > 0) or (but[2] == True)

				if self._launchpad_mode == "notes":
					if (x < 9) and (y < 9):
						if pressed:
							velocity = self.default_velocity
							if self._launchpad_model == "Pro":
								velocity = min(but[2] * self.launchpad_pro_velocity_multiplier, self.max_velocity)

							self._button_pressed(x, y, velocity)
						else:

							self._button_released(x, y)
					#TODO: Change tuples to Enumeration for readability
					elif (x,y) == (9,1) and pressed:
						# Clear screen
						self.lp.Reset()
						self._all_buttons_released()
					elif (x,y) == (9,2):
						# Random button mode
						if pressed:
							randomButtonModeEnabled = True
							randomButton = None
							randomButtonCounter = 0
						else:
							randomButtonModeEnabled = False
							if randomButton:
								self._button_released(randomButton[0], randomButton[1])
								randomButton = None
								

				#Settings
				if self._launchpad_mode == "settings":
					self._all_buttons_released()
					if (x,y) == (6,8) and self._grid_layout != "Diatonic 4th":
						self._grid_layout = "Diatonic 4th"
						self._color_buttons()
					elif (x,y) == (7,8) and self._grid_layout != "Diatonic 5th":
						self._grid_layout = "Diatonic 5th"
						self._color_buttons()
					elif (x,y) == (8,8) and self._grid_layout != "Chromatic":
						self._grid_layout = "Chromatic"
						self._color_buttons()
					#(x,y) < (8,6)
					elif (((1 <= x < 8) and (y == 6)) or ((x in [1, 2, 4, 5, 6]) and y == 7)) and pressed:
						# Grid Key
						self._active_key = self.WHITE_KEYS[x - 1] + (y == 7)
						self._color_buttons()
						print("Key is ", self.NOTE_NAMES[self._active_key])
					elif (x,y) in KEY_OPTIONS["settings"]["scale"]:
						if pressed:
							self._highlight_keys_in_scale()
						self._active_scale_button_pressed(x, y)

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

				elif pressed and (x,y) == (9,3):
						#Chord mode
						if self._chord is None:
							self._chord = Chord(self._active_scale)
						self._chord_mode = not self._chord_mode
						print("CHORD MODE ", ("ON" if self._chord_mode else "OFF"))		
				
				if self.debugging is True:
					print(" event: ", but, x, y)

	def _color_note_button(self, x, y, note_interval=1, pressed=False):
		if pressed:
			key = "note.pressed"
		elif note_interval not in SCALE[self._active_scale]:
			key = "note.out_scale"
		elif note_interval == 0:
			key = "note.root"
		else:
			key = "note.in_scale"

		self._color_button(x, y, key)


	def _color_button(self, x, y, buttonType):
		lpX = x - 1
		lpY = -1 * (y - 9)

		if self._launchpad_model == "Mk1":
			colorSet = "Mk1"
			self.lp.LedCtrlXY(lpX, lpY, self.NOTE_COLORS[colorSet][buttonType][0], self.NOTE_COLORS[colorSet][buttonType][1])
		else:
			colorSet = "Mk2"
			self.lp.LedCtrlXY(lpX, lpY, self.NOTE_COLORS[colorSet][buttonType][0], self.NOTE_COLORS[colorSet][buttonType][1], self.NOTE_COLORS[colorSet][buttonType][2])

	def _scroll_text(self, text, colorKey):
		if self._launchpad_model == "Mk1":
			colorSet = "Mk1"
			self.lp.LedCtrlString(text, self.NOTE_COLORS[colorSet][colorKey][0], self.NOTE_COLORS[colorSet][colorKey][1], self.lp.SCROLL_LEFT, 20)
		else:
			colorSet = "Mk2"
			self.lp.LedCtrlString(text, self.NOTE_COLORS[colorSet][colorKey][0], self.NOTE_COLORS[colorSet][colorKey][1], self.NOTE_COLORS[colorSet][colorKey][2], self.lp.SCROLL_LEFT, 20)

	#Colors whole layout on mode change. Like an initalization for each mode
	def _color_buttons(self):
		if self._launchpad_mode == "notes":
			for x in range(1, 9):
				for y in range(1, 9):
					self._color_note_button(x, y, self._get_note_interval(x, y), (self._get_midi_note(x, y) in self._pressed_notes))

		#Settings > Scales			
		elif self._launchpad_mode == "settings":

			self._color_button(6, 8, "settings.layout_" + ("on" if self._grid_layout == "Diatonic 4th" else "off"))
			self._color_button(7, 8, "settings.layout_" + ("on" if self._grid_layout == "Diatonic 5th" else "off"))           
			self._color_button(8, 8, "settings.layout_" + ("on" if self._grid_layout == "Chromatic" else "off"))                

			#for i in GRID_KEY.len
			#	colorbutton(GRID_KEY[i], "on" if _gridkey = i else "pff")
			key_i = 0
			for x,y in KEY_OPTIONS["settings"]["key"]:
				self._color_button(x,y, "settings.key_" + ("on" if self._active_key == key_i else "off") )
				key_i +=1

			scale_i = 0
			for x,y in KEY_OPTIONS["settings"]["scale"]:
				self._color_button(x,y, "settings.scale_" + ("on" if self._active_scale == SCALE_NAMES[scale_i] else "off") )
				scale_i +=1
			
		self._color_button(9, 6, "note.pressed") # octave up
		self._color_button(9, 5, "note.pressed") # octave down
		self._color_button(9, 8, "note.pressed") # settings
		
		if self.kid_mode is not True:
			self._color_button(1, 9, "note.pressed") # sample down
			self._color_button(2, 9, "note.pressed") # sample up

	def _is_interval_in_scale(self, x, y):
		return self._get_note_interval(x, y) in SCALE[self._active_scale]

	def _minimum_note_on_board(self):
		return ((self._grid_octave + 1) * 12) + self._active_key

	def _get_scale_length(self):
		return len(SCALE[self._active_scale]) if self._grid_layout != "Chromatic" else 12

	def _get_note_grid_index(self, x, y):
		return (x-1) + (y-1) * GRID_LAYOUT_OFFSET[self._grid_layout]

	def _get_scale_degree(self, x, y):
		return self._get_note_grid_index(x,y) % self._get_scale_length()

	def _get_note_interval(self, x, y):
		scale_degree = self._get_scale_degree(x, y)
		return SCALE[self._active_scale][scale_degree] if self._grid_layout != "Chromatic" else scale_degree

	def _get_midi_note(self, x, y):
		note_octave = self._get_note_grid_index(x, y) // self._get_scale_length()
		return self._minimum_note_on_board() + self._get_note_interval(x, y) + 12 * note_octave

	def get_note_info(self, x, y):
		pass

	def diff(first, second):
		second = set(second)
		return [item for item in first if item not in second]

	def _get_buttons_for_midi_note(self, x, y):
		buttons = []
		if self._grid_layout == "Diatonic 4th":
			#if x=1 and y>2, then there are three buttons to highlight, TWO BELOW
			#if x=8 and y<6, then there are three buttons to highlight, TWO ABOVE
			#top notes always x < 2, middle notes always 3 < x < 6, bottom are always x > 6

			#What's stopping us from getting XYs for note interval / scale degree?
			#Then take only XYs in the same note_octave?
			i = x-1
			in_bounds = (x,y) not in [ (x,9), (9,y) ]
			btn_left 	=	[ int(i%3 + 1), y + int(i/3) % 3] if y < 9 - (int(i/3) % 3) else None
			btn_center 	=	[ int(i%3 + 4),	y + int(x/3) - 1] if y < 9 - (int(x/3) - 1) and (x%3 != 0) else None
			btn_right	=	[ int(x%3 + 6), y + (int(x/3) % 3 - 2)]
			
			buttons = [ btn for btn in [btn_left, btn_center, btn_right] if btn is not None]

		elif self._grid_layout == "Diatonic 5th":
			other_x = (x - 1)%4 + (1 if x < 4 else 5)
			buttons.append([other_x, y + int(math.copysign(1, x - other_x))])
			buttons.append([x,y])
		
		elif self._grid_layout == "Chromatic":
			other_x = (x - 1)%5 + (6 if x < 4 else 1)
			if (x,y) not in [ (4,y),(5,y),(x,9) ]:
				buttons.append( [other_x, y + int(math.copysign(1, x - other_x))] )
			buttons.append([x,y])

		#print("actual btn: ", [x,y],"\tbuttons to highlight: ", buttons)
		return buttons

	def get_currently_playing_midi_notes(self):
		midiNotes = []
		for buttonNumber in self._pressed_buttons:
			x = int(math.floor(buttonNumber % 8)) + 1
			y = (buttonNumber // 8) + 1
			midi_note = self._get_midi_note(x, y)
			if midi_note not in midiNotes:
				midiNotes.append(midi_note)
		return midiNotes

	# This takes 1-based coordinates with 1,1 being the lower left button
	def _button_pressed(self, x, y, velocity):
		#print("BTN_DWN\t x: ", x, "\t y: ", y)
		buttonNumber = (x-1)  + ((y-1) * 8)
		self._pressed_buttons.append(buttonNumber)

		midiNote = self._get_midi_note(x, y)
		scale_degree = self._get_scale_degree(x, y)

		if self._chord_mode:
			new_chord = self._chord(scale_degree)
			if new_chord not in self._pressed_chords:
				for note in new_chord:
					self._play_note(x,y, midiNote-self._get_note_interval(x, y) + note[1], velocity)
				self._pressed_chords.append(new_chord)

		else:
			self._play_note(x,y, midiNote, velocity)

		print("end _button_pressed: ", self.get_currently_playing_midi_notes())

	def _play_note(self, x,y, midiNote, velocity):
		if midiNote not in self._pressed_notes:
			self.note_callback("note_on", midiNote, velocity)
			buttons = self._get_buttons_for_midi_note(x,y)
			for btn_x, btn_y in buttons:
				self._color_note_button(btn_x, btn_y, pressed=True)

			self._pressed_notes.append(midiNote)
		else:
			#play note again
			self.note_callback("note_off", midiNote, velocity)
			self.note_callback("note_on", midiNote, velocity)

		print("NOTE ON:\t", midiNote)

	# Todo, we should actually 
	def _all_buttons_released(self):
		for midiNote in self._pressed_notes:
			self.note_callback('note_off', midiNote, 0)

		del self._pressed_notes[:]
		del self._pressed_buttons[:]

	# This takes 1-based coordinates with 1,1 being the lower left button
	def _button_released(self, x, y):
		buttonNumber = (x-1)  + ((y-1) * 8)

		if buttonNumber not in self._pressed_buttons:
			return

		midiNote = self._get_midi_note(x, y)
		#print("Pressed buttons: ", self._pressed_buttons)
		self._pressed_buttons.remove(buttonNumber)
		new_pressed_notes = self.get_currently_playing_midi_notes()

		if midiNote not in new_pressed_notes:
			if self._chord_mode:
				#turn off all associated notes
				root = midiNote - self._get_note_interval(x, y)
				released_chord = self._chord(self._get_scale_degree(x, y))
				for note in released_chord:
					print("CHORD NOTE: ", note)
					self._stop_note(x, y, root + note[1])
				self._pressed_chords.remove(released_chord)
					
			else:
				self._stop_note(x, y, midiNote)

		
		self._pressed_notes = new_pressed_notes
		print("end _button_released: ", self.get_currently_playing_midi_notes())

	def _stop_note(self, x,y, midiNote):
		self.note_callback('note_off', midiNote, 0)
		buttons = self._get_buttons_for_midi_note(x,y)

		for btn_x, btn_y in buttons:
			self._color_note_button(btn_x, btn_y, self._get_note_interval(btn_x, btn_y))

		print("NOTE OFF:\t", midiNote)


	def _active_scale_button_pressed(self, x, y):
		index = (x - 1) + ((4 - y) * 8)
		self._active_scale = SCALE_NAMES[index]
		if self.debugging:
			print("Musical mode is", self._active_scale)
			pass
		if self._chord_mode:
			self._chord.update_scale(self._active_scale)

		self._all_buttons_released()
		self._color_buttons()

	def _highlight_keys_in_scale(self):
		root = self._active_key
		for key in range(root, root+11):
			self._color_button(KEY_OPTIONS["settings"]["key"][key%11][0], KEY_OPTIONS["settings"]["key"][key%11][1], "note.in_scale")