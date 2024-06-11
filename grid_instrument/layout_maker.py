from itertools import product
from .colors import *
from .chording import *
from .constants import *

CHORD_LAYOUT = {
	"default": (
		#initial conditions based on diatonic major
		#will change on _active_scale update
		#(function name, info)
		#scale = takes whole column, starting note degree (if empty, cont from prev row end), octave
		#chord = takes whole column, holds chord notations (need to create get_chord_by_notation inchord class)
		#user = takes specified cells. When pressed, saves all "scale", "chord", or "ext" pressed buttons
		("scale", 0, 0),
		("scale", 4, 0),
		("scale", 2, 1),
		("scale", 6, 0),
		("scale", 4, 1),
		("chord", 0),
		("user", (
			(7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (7,8), 
			(8,2), (8,3), (8,4), (8,5), (8,6), (8,7), (8,8) 
		)),
		("lock", (8,1), False),
		("sustain", (7,1), False)
	),
	"chord_map": (
	
		#5, 6, 7, [1] | [5], 4 3 2
		("roman", ("V", "vi", "vii", "I", "V", "IV", "iii", "ii")), #COL 4
		#mode 5 (Aeolian): 5, 6, 7, [1] | [5], 4 3 2
		("roman", ("v", "bVI", "bVII", "I", "v", "IV", "bIII", "ii")), #COL 5

	),
}

EXT_TONES = ["a9", "a11", "a13", "b9", "b11", "b13"]


#Holds the note information for each layout on the Launchpad grid

# (GridInstrument) PAD_MODES["chord"]["default"] =  PadLayout(CHORD_LAYOUT["default"], "chord")
# (GridInstrument) self._active_mode = PAD_MODES["chord"]
# (GridInstrument) self._active_layout = self._active_mode["default"]

# Benefits:
# Can get the given note interval by:    self._active_layout( (x,y) )

class PadLayout:

	info = [[]] * 64

	def __init__(self, layout, kind, scale, direction="column"):
		self.layout = layout
		self.kind = kind
		self.scale = scale
		self.direction = direction
		self._build()
	
	def update_scale(self, scale):
		self.scale = scale
		self._build()

	def _build(self):
		if self.kind == "chord":
			n = len(self.scale["span"])
			for i, s in enumerate(self.layout):

				if	s[0] == "scale":
					octave = 12*s[2]
					for j in range(8):
						triad_type = "root" if j%n == 0 else get_triad_type(self.scale["triad"][j%n])
						note_color = SCALE_TRIAD_COLORS[triad_type]
						deg_index = (s[1] + j)%n
						self.info[8*i + j] = Pad("note", [self.scale["span"][deg_index] + octave + 12*( (s[1] + j)//n )], (i+1,j+1), note_color)
						
				elif	s[0] == "chord":
					for j in range(8):
						#TODO: make chord based on roman numeral notation. right now just gets corresponding scale triad
						chord = CHORD((j+s[1])%n, chordie=True)
						adj_chord = [note + 12*((j+s[1])//n) for note in chord]
						self.info[8*i + j] = Pad("chord", adj_chord, (i+1,j+1), Color.ORANGE)
				elif	s[0] == "roman":
					for j in range(8):
						chord_by_numeral = [ t + 12*(j//n) for t in self.scale["triad"][self.scale["roman"].index(s[1][j%n])] ]
						self.info[8*i + j] = Pad("chord", chord_by_numeral, (i+1,j+1), Color.ORANGE)
				elif	s[0] == "ext":
					x,y = s[1]
					i,j = (x-1, y-1)
					self.info[8*i + j] = Pad("ext",     s[2], (x,y), Color.YELLOW)
                
				elif	s[0] == "inv":
					x,y = s[1]
					i,j = (x-1, y-1)
					self.info[8*i + j] = Pad("inv",     s[2], (x,y), Color.BLUE)

				elif	s[0] == "lock":
					x,y = s[1]
					i,j = (x-1, y-1)
					self.info[8*i + j] = Pad("lock",    s[2], (x,y), Color.add(Color.PINK, -0X1F))

				elif	s[0] == "sustain":
					x,y = s[1]
					i,j = (x-1, y-1)
					self.info[8*i + j] = Pad("sustain", s[2], (x,y), Color.GREEN)

				elif	s[0] == "user":
					for (x,y) in s[1]:
						i,j = (x-1, y-1)
						self.info[8*i + j] = Pad("user", [], (x,y), Color.add(Color.WHITE, -0X17))
		else:
			pass

		if self.direction == "row":
			self.info = [ self.info[8*j + i] for i,j in product(range(8),range(8)) ]

		#print([str(pad) for pad in self.info])

	def get_pad(self, x, y):
		return self.info[8*(x-1) + (y-1)]
	
	def get_pads_by_type(self, type):
		return list(filter(lambda pad: pad.type == type, self.info))
	
	def get_pads_by_note(self, note):
		note_pads = self.get_pads_by_type("note")
		return list(filter(lambda pad: pad.data[0] == note, note_pads))
	
	def get_pressed_pads(self, type="all", ignore=[]):

		if type == "all":
			pads = self.info
		else:
			pads = self.get_pads_by_type(type)

		return list(filter(lambda pad: pad.pressed and pad.type not in ignore, pads))

	def get_notes_for_pressed_pads(self):
		pressed_pads = self.get_pressed_pads(ignore=["ext", "inv",  "lock", "sustain"])
		return [*set([note for pad in pressed_pads for note in pad.data])]
	
	def get_active_pads(self):
		pressed_pads_notes = self.get_notes_for_pressed_pads()
	#	[*set([pad. for note in pressed_pads_notes for pad in self.get_pads_by_note(note))]
	
	#def is_pad_active(self, pad):
	#	return ( pad in self.get_pads_by_note( ) ) or ( pad.data and isinstance(pad.data, bool) )



class Pad:
	def __init__(self, type, data, xy, color):
		self.type = type
		self.data = data
		self.xy = xy
		self.color = color
		self.pressed = False

	def __str__(self):
		return "(" + str(self.type) + ", " + str(self.data) + ", " + str(self.color) + ")"
	
	def get_color(self, is_active=False, is_root=False):
		color = self.color

		if isinstance(self.data, bool):
			color = Color.invert(self.color) if self.data else self.color
		elif self.type == "note" and is_active:
			color = Color.add(Color.RED, -0X07)	
		if self.pressed or (is_active and is_root):
			color = Color.add(Color.YELLOW, -0X07)	
		
		return color
	
	def toggle(self):
		if isinstance(self.data, bool):
			self.data = not self.data