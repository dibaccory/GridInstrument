import math
from .scales import *

#How to instantiate chords in a mode?
#If we instantiate by the current musical mode, we should find chords by scale note?
#chord = Chord(MODES["Major"])
#chord(1, self.seveth (BOOL), ext="", mod=0, sec=0, inv=0)
#chord(1) -> I					chord(posInScale+1) -> if posInScale = 0, I
#chord(1, ["maj7"]) -> Imaj7
#chord(2, "7") -> ii7
#chord(1, ["add9"]) -> Iadd9
#chord(1, [add9"]) with jazzy = True -> Imaj7add9
#chord(1, "9") -> I9 -> Imaj7add9
#chord(1, "6") -> I 1st inversion -> chord(1, inv=1)
#chord(1, ["6/9"]) -> I6/9 -> I6add9 
#chord(1, "7", mod=4) -> Modal interchange of I using mode index 4 (Mixolydian) -> I7
#chord(2, "7", sec="1") -> Dominant chord of 2, add 7th -> V7/ii
#chord(2, "7", sec="2") -> Leading chord of 2, add 7th -> vii7b5/ii
#chord.update(MODES["something_else"])

TRIAD = {
	#tonic: 0, subdom: 5, dom: 7
	#No inversions, so chords may have intervals past 12
	"I":	[0, 4, 7],
	"i":	[0, 3, 7],
	"II":	[2, 6, 9],
	"ii":	[2, 5, 9],
    "III":	[4, 8, 11],
	"iii":	[4, 7, 11],
    "IV":	[5, 9, 12],
    "iv":	[5, 8, 12],
    "V":	[7, 11, 14],
	"v":	[7, 10, 14],
    "VI":	[9, 13, 16],
    "vi":	[9, 12, 16],
    "VII":	[11, 15, 18],
    "vii":	[11, 14, 18],
}	


def sus2(ch):
    return [ch[0], ch[0]+2, ch[2]]

def sus4(ch):
    return [ch[0], ch[0]+5, ch[2]]

def _b5(ch):
	return [ch[0], ch[1], ch[2]-1]

def dim(ch):
    return [ch[0], ch[1]-1, ch[2]-1]

def aug(ch):
    return [ch[0], ch[1], ch[2]+1]

def flat(ch):
	return [ch[0]-1, ch[1]-1, ch[2]-1]

def sharp(ch):
	return [ch[0]+1, ch[1]+1, ch[2]+1]

def invert(ch, inv):
    n = len(ch)
    inv %= n
    for i in range(n-1):
          ch[i] += (12 if inv > i else 0)
    return ch



def _7(ch):
	return ch.append(ch[0]+10)

def _M7(ch):
	return ch.append(ch[0]+11)

def _add6(ch):
	return ch.append(ch[0]+9)

def _add9(ch):
	return ch.append(ch[0]+14)

def _b9(ch):
	return ch.append(ch[0]+13)

def _add11(ch):
	return ch.append(ch[0]+17)

def _b11(ch):
	return ch.append(ch[0]+17)

def _add13(ch):
	return ch.append(ch[0]+21)

def _b13(ch):
	return ch.append(ch[0]+21)

class Chord:

	scale = "Major" #[0, 2, 4, 5, 7, 9, 11]
	scale_mode = "Ionian"
	jazzy = False
	chord = None

	EXT_TONES = {
	"7": 		10,
	"maj7":		11,
	"add9":		SCALE[scale][1],
	"b9":		SCALE[scale][1]-1, 
	"add11":	SCALE[scale][3],
	"b11":		SCALE[scale][3]-1,
	"add13": 	SCALE[scale][5],
	"b13":		SCALE[scale][5]-1
	}

	def __init__(self, scale="Major", jazzy=True):
		self.scale = scale
		self.scale_mode = scale if scale in MODE_NAMES else "Ionian"
		self.jazzy = jazzy

	#degree = notePositionInScale
	def __call__(self, degree, ext=[], mod=0, sec=0, inv=0, in_scale=True):
		scale_length = len(SCALE[self.scale])

		#if scale_length != 7:
		#	print("Scale length is weird...switch to Major")
		#	self.update_scale("Major")
		#	scale_length = len(SCALE[self.scale])

		#NOTE: Jazz:		im7 II7 bIIImaj7 IV7 [viio7/V OR bVIIb9/V] vm7 vim7 (bVIImaj7 === Vmaj7/bIII) [viio7 or (viimaj7b5 === bVIIb9) ]  

		#Get triad from scale
		#NOTE: Getting triad by the scale degree only works of the scale is heptatonic (7 notes)
		_7th_notation = ""
		if in_scale:
			self.chord = self.make_triad(degree)
			if "maj7" in ext or "7" in ext or self.jazzy:
				_7th_notation = self._get_7th(degree, self.chord, ext)

				#add tones to the chord	
			for tone in ext:
				self.add_tone(self.chord, tone)

			nat_dim = "b5" if (degree == 6 - list(MODAL_TRIADS).index(self.scale_mode)) else ""
			chord_notation	= MODAL_TRIADS[self.scale_mode][degree] + _7th_notation + nat_dim + "".join(ext)
		else:
			self.chord, chord_notation = self.get_leading_chord(degree)
			#remove 7th if not in 7th mode

		
		print("Playing: ", chord_notation)

		return self.chord
	
	def make_triad(self, degree):
		scale_length = len(SCALE[self.scale])
		_3rd_degree = (degree+2)%scale_length
		_5th_degree = (degree+4)%scale_length

		return [ 
			SCALE[self.scale][degree],
			SCALE[self.scale][_3rd_degree] + (12 if degree+2 >= scale_length else 0),
			SCALE[self.scale][_5th_degree] + (12 if degree+4 >= scale_length else 0)
	   	]
	
	def _get_7th(self, degree, chord, ext=[]):
		scale_length = len(SCALE[self.scale])
		_7th_degree = (degree+6)%scale_length
		nat_7th_note 	= SCALE[self.scale][_7th_degree] + (12 if degree > 0 else 0)
		nat_7th_ivl 	= abs( SCALE[self.scale][degree] - nat_7th_note )
		nat_7th 		= "7" if nat_7th_ivl in [2,10] else "maj7"
		alt_7th 		= "7" if nat_7th == "maj7" else "maj7"
		alt_7th_note 	= nat_7th_note + (1 if nat_7th == "7" else -1) 
		_7th_notation = ""

		#Choose alternate 7th over natural 7th
		if alt_7th in ext:
			ext.remove(alt_7th)
			_7th_notation = alt_7th
			chord.append(alt_7th_note)

		elif self.jazzy or nat_7th in ext:
			try:
				ext.remove(nat_7th)
			except ValueError:
				pass
			_7th_notation = nat_7th
			chord.append(nat_7th_note)

		return _7th_notation
		
	def toggle_jazzy(self):
		self.jazzy = (not self.jazzy)

	def update_scale(self, scale):
		self.scale = scale
		self.scale_mode = scale if scale in MODE_NAMES else "Ionian"

	def add_tone(self, chord, tone):
		chord.append(self.EXT_TONES[tone] + 12)

	def rem_tone(self, chord, tone):
		chord.remove(tone)

	#TODO GET THIS TO A FUNCTIONAL STATE FOR CHROMATIC
	#If in_scale = False (parameter "degree" is not actually in current scale), find a good sounds leading chord
	#I guess this only happens in "Chromatic" mode... How bout that
	def get_leading_chord(self, pressed_note):
		leading_chord = []
		chord_notation = ""
		#in chromatic: Leading triads always dim, but for 7ths: 
		# (Imaj7 -> iim7 = biimaj7b5 )
		# min -> min = o7, 
		# Maj -> Maj = m7b5

		#Find the notes to the left and right of pressed_note_interval (left_note, right_note)
		left_note  = next(note for note in enumerate(reversed(SCALE[self.scale])) if note[1] < pressed_note)
		right_note = next(note for note in enumerate(SCALE[self.scale]) if note[1] > pressed_note)

		#if current scale isn't diatonic, we need to check which modal triad is missing
		#if abs(left_note[1] - right_note[1])%3 == 0 and (left_note[1], right_note[0]) not in [(1,4), (6,9), (8,11)]:

		#Maj -> min = maj7b5
		left_triad  = SCALE_TRIADS[self.scale][left_note[0]]
		right_triad = SCALE_TRIADS[self.scale][right_note[0]]
		leading_chord = self.make_triad(left_note[0])
		if 	(left_triad in MAJOR_MODES and right_triad in MINOR_MODES) or \
			(left_triad in MINOR_MODES and right_triad in MAJOR_MODES):
			#maj7b5
			leading_chord.append(leading_chord[0]+12)
			leading_chord[0] += 1

		elif left_triad in MINOR_MODES and right_triad in MINOR_MODES:	
			if	self._is_dim(right_note[0]): # maj7b5
				leading_chord.append(leading_chord[0]+12)
				leading_chord[0] += 1
				leading_chord[1] += 1
			else:	#dim7 ... if ii -> iii, could do iim7, v7/iii, iiim7
				leading_chord.append(leading_chord[0]+10)
				leading_chord[0] += 1
				leading_chord[1] += 1
		else: #left_triad in MAJOR_MODES and right_triad in MAJOR_MODES:	
			#m7b5
			leading_chord.append(leading_chord[0]+11)
			leading_chord[0] += 1


		return leading_chord, chord_notation
		#If the scale doesn't have [(0,), (1, 2), (3, 4), (5,), (6, 7), (8, 9), (10, 11)]
		# 0 == abs(left_note-right_note)%3 and (left_note, right_note) not in [(1,4), (6,9), (8,11)]
		
	def _is_dim(self, degree):
		return (degree == 6 - list(MODAL_TRIADS).index(self.scale_mode))





		
