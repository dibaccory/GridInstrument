import time
import random
import math
import collections
import sys

try:
	from grid_instrument import lp as launchpad
except ImportError:
	try:
		print("import error, use native")
		#import launchpad_py as launchpad
	except ImportError:
		sys.exit("error loading launchpad.py")

class GridInstrument:

	# Constants
	MUSICAL_MODES = collections.OrderedDict([
		('Major', [0, 2, 4, 5, 7, 9, 11]),
		('Minor', [0, 2, 3, 5, 7, 8, 10]),
		('Dorian', [0, 2, 3, 5, 7, 9, 10]),
		('Mixolydian', [0, 2, 4, 5, 7, 9, 10]),
		('Lydian', [0, 2, 4, 6, 7, 9, 11]),
		('Phrygian', [0, 1, 3, 5, 7, 8, 10]),
		('Locrian', [0, 1, 3, 5, 6, 8, 10]),
		('Diminished', [0, 1, 3, 4, 6, 7, 9, 10]),

		('Whole-half', [0, 2, 3, 5, 6, 8, 9, 11]),
		('Whole Tone', [0, 2, 4, 6, 8, 10]),
		('Minor Blues', [0, 3, 5, 6, 7, 10]),
		('Minor Pentatonic', [0, 3, 5, 7, 10]),
		('Major Pentatonic', [0, 2, 4, 7, 9]),
		('Harmonic Minor', [0, 2, 3, 5, 7, 8, 11]),
		('Melodic Minor', [0, 2, 3, 5, 7, 9, 11]),
		('Super Locrian', [0, 1, 3, 4, 6, 8, 10]),

		('Bhairav', [0, 1, 4, 5, 7, 8, 11]),
		('Hungarian Minor', [0, 2, 3, 6, 7, 8, 11]),
		('Minor Gypsy', [0, 1, 4, 5, 7, 8, 10]),
		('Hirojoshi', [0, 2, 3, 7, 8]),
		('In-Sen', [0, 1, 5, 7, 10]),
		('Iwato', [0, 1, 5, 6, 10]),
		('Kumoi', [0, 2, 3, 7, 9]),
		('Pelog', [0, 1, 3, 4, 7, 8]),

		('Spanish', [0, 1, 3, 4, 5, 6, 8, 10]),
		('IonEol', [0, 2, 3, 4, 5, 7, 8, 9, 10, 11])
	])

	WHITE_KEYS = MUSICAL_MODES['Major']

	NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

	NOTE_COLORS = { 
		"Mk1": { 
			"pressed": [0, 63],    
			"root": [3, 0],      
			"noteInScale": [1, 1],
			"noteOutOfScale": [0, 0],
			"settingsKeyOff": [0, 4],
			"settingsKeyOn":  [0, 20],
			"settingsGridKeyOff": [1, 1],
			"settingsGridKeyOn":  [3, 3],
			"settingsGridMusicalModeOff": [0, 1],
			"settingsGridMusicalModeOn":  [0, 3],
			"settingsGridLayoutOff": [1, 0],
			"settingsGridLayoutOn":  [3, 0],

		}, 
		"Mk2": { 
			"pressed": [0, 50, 0], 
			"root": [0, 10, 30], 
			"noteInScale": [10, 10, 15],
			"noteOutOfScale": [0, 0, 0],
			"settingsKeyOff": [0, 4, 0],
			"settingsKeyOn":  [0, 20, 0],
			"settingsGridKeyOff": [10, 4, 0],
			"settingsGridKeyOn":  [20, 8, 0],
			"settingsGridMusicalModeOff": [0, 4, 0],
			"settingsGridMusicalModeOn":  [0, 20, 0],
			"settingsGridLayoutOff": [0, 0, 4],
			"settingsGridLayoutOn":  [0, 0, 20],
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
	_grid_musical_mode = 'Major'
	_grid_octave = 3
	_grid_key = 0
	_grid_layout = "Diatonic 4th" # possible values are "Diatonic 4th" and "Chromatic"
	_launchpad_mode = "notes" # possible values are "notes" and "settings"


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
				x = but[0] + 1
				y = (8 - but[1]) + 1
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
					if x == 6 and y == 8 and self._grid_layout != "Diatonic 4th":
						self._grid_layout = "Diatonic 4th"
						self._color_buttons()
					elif x == 7 and y == 8 and self._grid_layout != "Chromatic":
						self._grid_layout = "Chromatic"
						self._color_buttons()
					elif (((1 <= x < 8) and (y == 6)) or ((x in [1, 2, 4, 5, 6]) and y == 7)) and pressed:
						# Grid Key
						self._grid_key = self.WHITE_KEYS[x - 1] + (y == 7)
						self._color_buttons()
						print("Key is ", self.NOTE_NAMES[self._grid_key])
					elif (1 <= x <= 8) and (1 <= y <= 4):
						self._grid_musical_mode_button_pressed(x, y)

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
				
				if self.debugging is True:
					print(" event: ", but, x, y)

	def _color_note_button(self, x, y, noteInterval=1, pressed=False, inScale=True):
		if pressed:
			key = "pressed"
		elif noteInterval is None:
			key = "noteOutOfScale"
		elif noteInterval == 0:
			key = "root"
		else:
			key = "noteInScale"

		self._color_button(x, y, key)


	def _color_button(self, x, y, buttonType):
		lpX = x - 1
		lpY = -1 * (y - 9)

		if self._launchpad_model == "Mk1":
			colorSet = "Mk1"
			self.lp.LedCtrlXY(lpX, lpY, self.NOTE_COLORS[self._launchpad_model][buttonType][0], self.NOTE_COLORS[self._launchpad_model][buttonType][1])
		else:
			colorSet = "Mk2"
			self.lp.LedCtrlXY(lpX, lpY, self.NOTE_COLORS[colorSet][buttonType][0], self.NOTE_COLORS[colorSet][buttonType][1], self.NOTE_COLORS[colorSet][buttonType][2])

	def _scroll_text(self, text, colorKey):
		if self._launchpad_model == "Mk1":
			colorSet = "Mk1"
			self.lp.LedCtrlString(text, self.NOTE_COLORS[self._launchpad_model][colorKey][0], self.NOTE_COLORS[self._launchpad_model][colorKey][1], self.lp.SCROLL_LEFT, 20)
		else:
			colorSet = "Mk2"
			self.lp.LedCtrlString(text, self.NOTE_COLORS[colorSet][colorKey][0], self.NOTE_COLORS[colorSet][colorKey][1], self.NOTE_COLORS[colorSet][colorKey][2], self.lp.SCROLL_LEFT, 20)


	def _color_buttons(self):
		if self._launchpad_mode == "notes":
			for x in range(1, 9):
				for y in range(1, 9):
					noteInfo = self._get_note_info(x, y)
					scaleNoteNumber = noteInfo[2]
					self._color_note_button(x, y, scaleNoteNumber, (noteInfo[0] in self._pressed_notes))

		#Settings > Scales			
		elif self._launchpad_mode == "settings":
			self._color_button(6, 8, "settingsGridLayoutOn" if self._grid_layout == "Diatonic 4th" else "settingsGridLayoutOff")                
			self._color_button(7, 8, "settingsGridLayoutOn" if self._grid_layout == "Chromatic" else "settingsGridLayoutOff")                

			
			self._color_button(1, 6, "settingsGridKeyOn" if self._grid_key == 0 else "settingsGridKeyOff")                
			self._color_button(1, 7, "settingsGridKeyOn" if self._grid_key == 1 else "settingsGridKeyOff")                
			self._color_button(2, 6, "settingsGridKeyOn" if self._grid_key == 2 else "settingsGridKeyOff")                
			self._color_button(2, 7, "settingsGridKeyOn" if self._grid_key == 3 else "settingsGridKeyOff")                
			self._color_button(3, 6, "settingsGridKeyOn" if self._grid_key == 4 else "settingsGridKeyOff")
			self._color_button(4, 6, "settingsGridKeyOn" if self._grid_key == 5 else "settingsGridKeyOff")
			self._color_button(4, 7, "settingsGridKeyOn" if self._grid_key == 6 else "settingsGridKeyOff")
			self._color_button(5, 6, "settingsGridKeyOn" if self._grid_key == 7 else "settingsGridKeyOff")
			self._color_button(5, 7, "settingsGridKeyOn" if self._grid_key == 8 else "settingsGridKeyOff")
			self._color_button(6, 6, "settingsGridKeyOn" if self._grid_key == 9 else "settingsGridKeyOff")
			self._color_button(6, 7, "settingsGridKeyOn" if self._grid_key == 10 else "settingsGridKeyOff")
			self._color_button(7, 6, "settingsGridKeyOn" if self._grid_key == 11 else "settingsGridKeyOff")

			self._color_button(1, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Major"  else "settingsGridMusicalModeOff")
			self._color_button(2, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Minor"  else "settingsGridMusicalModeOff")
			self._color_button(3, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Dorian" else "settingsGridMusicalModeOff")
			self._color_button(4, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Mixolydian"  else "settingsGridMusicalModeOff")
			self._color_button(5, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Lydian"  else "settingsGridMusicalModeOff")
			self._color_button(6, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Phrygian"  else "settingsGridMusicalModeOff")
			self._color_button(7, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Locrian"  else "settingsGridMusicalModeOff")
			self._color_button(8, 4, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Diminished"  else "settingsGridMusicalModeOff")
			
			self._color_button(1, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Whole-half"  else "settingsGridMusicalModeOff")
			self._color_button(2, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Whole Tone"  else "settingsGridMusicalModeOff")
			self._color_button(3, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Minor Blues" else "settingsGridMusicalModeOff")
			self._color_button(4, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Minor Pentatonic"  else "settingsGridMusicalModeOff")
			self._color_button(5, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Major Pentatonic"  else "settingsGridMusicalModeOff")
			self._color_button(6, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Harmonic Minor"  else "settingsGridMusicalModeOff")
			self._color_button(7, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Melodic Minor"  else "settingsGridMusicalModeOff")
			self._color_button(8, 3, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Super Locrian"  else "settingsGridMusicalModeOff")
			
			self._color_button(1, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Bhairav"  else "settingsGridMusicalModeOff")
			self._color_button(2, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Hungarian Minor"  else "settingsGridMusicalModeOff")
			self._color_button(3, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Minor Gypsy" else "settingsGridMusicalModeOff")
			self._color_button(4, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Hirojoshi"  else "settingsGridMusicalModeOff")
			self._color_button(5, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "In-Sen"  else "settingsGridMusicalModeOff")
			self._color_button(6, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Iwato"  else "settingsGridMusicalModeOff")
			self._color_button(7, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Kumoi"  else "settingsGridMusicalModeOff")
			self._color_button(8, 2, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Pelog"  else "settingsGridMusicalModeOff")
			
			self._color_button(1, 1, "settingsGridMusicalModeOn" if self._grid_musical_mode == "Spanish"  else "settingsGridMusicalModeOff")
			self._color_button(2, 1, "settingsGridMusicalModeOn" if self._grid_musical_mode == "IonEol"  else "settingsGridMusicalModeOff")
			
		self._color_button(9, 6, "pressed") # octave up
		self._color_button(9, 5, "pressed") # octave down
		self._color_button(9, 8, "pressed") # settings
		
		if self.kid_mode is not True:
			self._color_button(1, 9, "pressed") # sample down
			self._color_button(2, 9, "pressed") # sample up

	def _minimum_note_on_board(self):
		return ((self._grid_octave + 1) * 12) + self._grid_key

	def get_note_info(self, x, y):
		return self._get_note_info(x, y)

	def _get_note_info(self, x, y):
		#midiNote = None
		if self._grid_layout == "Diatonic 4th":

			base8NoteNumber = (x-1) + (3 * (y-1))
			notesPerOctave = len(self.MUSICAL_MODES[self._grid_musical_mode])
			# notePerOctave = 7
			# noteOctave = 1
			notePositionInScale = int(base8NoteNumber % notesPerOctave)
			noteInterval = self.MUSICAL_MODES[self._grid_musical_mode][notePositionInScale]

		elif self._grid_layout == "Chromatic":
			# eg. x, y = 2, 1
			base8NoteNumber = (x-1) + (5 * (y-1))
			#print("Base 8 number:\t", base8NoteNumber)
			# base8No4teNumber = 1
			notesPerOctave = 12
			# noteOctave = 0
			noteInterval = base8NoteNumber % notesPerOctave

		noteOctave = int(math.floor(base8NoteNumber / notesPerOctave))
		midiNote = self._minimum_note_on_board() + noteInterval + 12 * noteOctave
		#print("midiNote calculated:\t", midiNote)
		return [midiNote, noteOctave, noteInterval if noteInterval in self.MUSICAL_MODES[self._grid_musical_mode] else None]

	#def _get_note_info_old(self, x, y):
	#	base8NoteNumber = (x-1) + (3 * (y-1))
	#	noteOctave = int(base8NoteNumber / 7)
	#	scaleNoteNumber = base8NoteNumber % 7
	#	midiNote = self._minimum_note_on_board() + self.MUSICAL_MODES[self._grid_musical_mode][scaleNoteNumber] + 12 * noteOctave
	#	return [midiNote, noteOctave, scaleNoteNumber]

	def diff(first, second):
		second = set(second)
		return [item for item in first if item not in second]

	def _get_buttons_for_midi_note(self, x, y):
		buttons = []
		#if we have the midi note info, can't we just extrapolate all the buttons with this note instead of going through the whole list?
		#midiNote = ((self._grid_octave + 1) * 12) + self._grid_key + noteInterval + 12 * noteOctave
		# 	MIDI_MIN_NOTE = 12 (C-1)
		#	If midiNote is 12, then base8Note is 0, self._grid_key is 0, self._grid_octave is 0
		#	minimum_note_on_board = ( 12 * self._grid_octave + self._grid_key + MIDI_MIN_NOTE) => 12*(self._grid_octave + 1) + self._grid_key
		#	lowest_button_number = (midiNote - minimum_note_on_board)
		#	noteOctave = lowest_button_number / notesPerOctave
		#	notePositionInScale = lowest_button_number % notesPerOctave
		if self._grid_layout == "Diatonic 4th":
			#if x=1 and y>2, then there are three buttons to highlight, TWO BELOW
			#if x=8 and y<6, then there are three buttons to highlight, TWO ABOVE
			#top notes always x < 2, middle notes always 3 < x < 6, bottom are always x > 6
			i = x-1
			in_bounds = (x,y) not in [ (x,9), (9,y) ]
			btn_left 	=	[ int(i%3 + 1), y + int(i/3) % 3] if y < 9 - (int(i/3) % 3) else None
			btn_center 	=	[ int(i%3 + 4),	y + int(x/3) - 1] if y < 9 - (int(x/3) - 1) and (x%3 != 0) else None
			btn_right	=	[ int(x%3 + 6), y + (int(x/3) % 3 - 2)]
			
			buttons = [ btn for btn in [btn_left, btn_center, btn_right] if btn is not None]

		elif self._grid_layout == "Chromatic":
			other_x = (x - 1)%5 + (6 if x < 4 else 1)
			if (x,y) not in [ (4,y),(5,y),(x,9) ]:
				buttons.append( [other_x, y + int(math.copysign(1, x - other_x))] )
			buttons.append([x,y])

		print("actual btn: ", [x,y],"\tbuttons to highlight: ", buttons)
		return buttons

	def get_currently_playing_midi_notes(self):
		midiNotes = []
		for buttonNumber in self._pressed_buttons:
			x = int(math.floor(buttonNumber % 8)) + 1
			y = (buttonNumber / 8) + 1
			print("Btn: ", buttonNumber, "\tx: ", x, "\ty: ", y)
			#buttonNumber 4 -> x: 5, y: 1.5
			#buttonNumber 9 -> x: 2, y: 2.125
			noteInfo = self._get_note_info(x, y)
			if noteInfo[0] not in midiNotes:
				midiNotes.append(noteInfo[0])
		return midiNotes

	# This takes 1-based coordinates with 1,1 being the lower left button
	def _button_pressed(self, x, y, velocity):
		#print("BTN_DWN\t x: ", x, "\t y: ", y)
		buttonNumber = (x-1)  + ((y-1) * 8)
		noteInfo = self._get_note_info(x, y)
		midiNote = noteInfo[0]
		scaleNoteNumber = noteInfo[2]

		self._pressed_buttons.append(buttonNumber)

		self.note_callback("note_on", midiNote, velocity)
		if midiNote not in self._pressed_notes:
			buttons = self._get_buttons_for_midi_note(x,y)
			for newButton in buttons:
				self._color_note_button(newButton[0], newButton[1], scaleNoteNumber, True)
			self._pressed_notes.append(midiNote)
		if self.debugging:
			print("Button", buttonNumber, "pressed with MIDI note number", midiNote, "and velocity", velocity)
			pass
		print("PRESSED:\t", midiNote, "\t current: ", self.get_currently_playing_midi_notes())

	# Todo, we should actually 
	def _all_buttons_released(self):
		for midiNote in self._pressed_notes:
			self.note_callback('note_off', midiNote, 0)
			#print("releasing all buttons")

		del self._pressed_notes[:]
		del self._pressed_buttons[:]

	# This takes 1-based coordinates with 1,1 being the lower left button
	def _button_released(self, x, y):
		buttonNumber = (x-1)  + ((y-1) * 8)
		# Question: what new notes (not buttons) are now no longer being pressed 
		# Answer: probably by using the self._pressed_notes list you made silly
		if buttonNumber not in self._pressed_buttons:
			return

		noteInfo = self._get_note_info(x, y)
		midiNote = noteInfo[0]
		#print("Pressed buttons: ", self._pressed_buttons)

		

		self._pressed_buttons.remove(buttonNumber)
		
		new_pressed_notes = self.get_currently_playing_midi_notes()
		print("RELEASED:\t", midiNote, "\t current: ", new_pressed_notes)

		if midiNote not in new_pressed_notes:
			self.note_callback('note_off', midiNote, 0)
			buttons = self._get_buttons_for_midi_note(x,y)

			for newButton in buttons:
				noteInfo = self._get_note_info(newButton[0], newButton[1])
				scaleNoteNumber = noteInfo[2]
				self._color_note_button(newButton[0], newButton[1], scaleNoteNumber)

		self._pressed_notes = new_pressed_notes

	def _grid_musical_mode_button_pressed(self, x, y):
		index = (x - 1) + ((4 - y) * 8)
		self._grid_musical_mode = list(self.MUSICAL_MODES.keys())[index]
		if self.debugging:
			print("Musical mode is", self._grid_musical_mode)
			pass

		self._all_buttons_released()
		self._color_buttons()
