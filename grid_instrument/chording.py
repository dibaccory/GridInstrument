import math
from .scales import *
#from grid_instrument import *

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

	scale = {}
	#scale_mode = "Ionian"
	jazzy = False
	chord = None


	def __init__(self, scale, jazzy=True):
		self.update_scale(scale)
		#self.scale_mode = scale if scale in MODE_NAMES else "Ionian"
		self.jazzy = jazzy

	#degree = notePositionInScale
	def __call__(self, degree, ext=[], mod=0, sec=0, inv=0, in_scale=True):
		scale_length = len(self.scale["span"])
		chord = []
		#if scale_length != 7:
		#	print("Scale length is weird...switch to Major")
		#	self.update_scale("Major")
		#	scale_length = len(self.scale["span"])

		#NOTE: Jazz:		im7 II7 bIIImaj7 IV7 [viio7/V OR bVIIb9/V] vm7 vim7 (bVIImaj7 === Vmaj7/bIII) [viio7 or (viimaj7b5 === bVIIb9) ]  

		#Get triad from scale
		#NOTE: Getting triad by the scale degree only works of the scale is heptatonic (7 notes)
		_7th_notation = ""
		if in_scale:
			chord.extend(self.scale["triad"][degree])
			if "maj7" in ext or "7" in ext or self.jazzy:
				_7th_notation = self._get_7th(degree, chord, ext)

				#add tones to the chord	
			for tone in ext:
				self.add_tone(chord, tone)

			chord_notation	= self.scale["roman"][degree] + self._get_dim_notation(chord, _7th_notation) + "".join(ext)
		else:
			chord, chord_notation = self.get_leading_chord(degree)
			#remove 7th if not in 7th mode

		
		print("Playing: ", chord_notation)

		return chord
	
	def update_scale(self, scale):
		self.scale = scale
		self._create_triads()
		

	def _create_triads(self):
		scale_length = len(self.scale["span"])
		triads = []
		numerals = []

		for note_inv in self.scale["span"]:
			#check if there is a P5 interval, else it will be diminished. Forced m3
			note_inv_has_P5 = 0 if ( (note_inv+7) % 12 in self.scale["span"] ) else -1
			note_inv_has_M3 = 0 if ( (note_inv+4) % 12 in self.scale["span"] and note_inv_has_P5 == 0 ) else -1

			_5th_interval 	= ( note_inv+7 + note_inv_has_P5 ) 
			_3rd_interval 	= ( note_inv+4 + note_inv_has_M3 ) 
			#_5th_degree = self.scale["span"].index( _5th_interval % scale_length )

			triad = [note_inv, _3rd_interval, _5th_interval] 
			triads.append(triad)

			#is_inv_flat = True if abs(self.scale["span"][(i+1)%scale_length] - note_inv + 1)%12 - 1 == 1 else False
			numerals.append(self._get_triad_numerals(triad, note_inv) )

		self.scale["triad"] = triads
		self.scale["roman"] = numerals
		print("triads: ", triads)
		print("numerals: ", numerals)


	def _get_triad_numerals(self, triad, deg):
		#Start with major, lower if not
		has_flat = "b" if (deg in [1, 3, 6, 8, 10]) else ""
		numeral  = has_flat + MAJOR_MODES[deg]

		if 	 self._is_major(triad):
			return numeral
		elif self._is_aug(triad):
			return numeral + "+"
		elif self._is_minor(triad) or self._is_dim(triad):
			return numeral.lower()
	
	def make_triad(self, degree):
		#may need to construct based off of numeral triads instead of by index...
		scale_length = len(self.scale["span"])

		_3rd_degree = (degree+2)%scale_length
		_5th_degree = (degree+4)%scale_length

		return [ 
			self.scale["span"][degree],
			self.scale["span"][_3rd_degree] + (12 if degree+2 >= scale_length else 0),
			self.scale["span"][_5th_degree] + (12 if degree+4 >= scale_length else 0)
	   	]
	
	def _get_7th(self, degree, chord, ext=[]):
		scale_length = len(self.scale["span"])
		_7th_degree = (degree+6)%scale_length
		nat_7th_note 	= self.scale["span"][_7th_degree] + (12 if degree > 0 else 0)
		nat_7th_ivl 	= abs( self.scale["span"][degree] - nat_7th_note )
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

	def add_tone(self, chord, tone):
		pass
		#chord.append(self.EXT_TONES[tone] + 12)

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
		left_note  = next(note for note in reversed(list(enumerate(self.scale["span"]))) if note[1] < pressed_note)
		right_note = next(note for note in enumerate(self.scale["span"]) if note[1] > pressed_note)

		#if current scale isn't diatonic, we need to check which modal triad is missing
		#if abs(left_note[1] - right_note[1])%3 == 0 and (left_note[1], right_note[0]) not in [(1,4), (6,9), (8,11)]:

		#Maj -> min = maj7b5
		left_triad  = self.scale["roman"][left_note[0]]	
		right_triad = self.scale["roman"][right_note[0]]	
		leading_chord.extend(self.scale["triad"][left_note[0]])
		resolving_chord = self.scale["triad"][right_note[0]]	
		# left is b_ and abs(left_note - pressed_note) == 1, then chord_notation = left_triad[1:] else "b" + right_triad
		if left_triad[0] == "b" and abs(left_note[1] - pressed_note) == 1:
			chord_notation = (left_triad[1:]).lower()
		else:
			chord_notation = "b" + right_triad.lower()

		if 	(left_triad in MAJOR_MODES and right_triad in MINOR_MODES) or \
			(left_triad in MINOR_MODES and right_triad in MAJOR_MODES):
			#maj7b5
			leading_chord.append(leading_chord[0]+12)
			leading_chord[0] += 1
			chord_notation += "maj7b5"

		elif left_triad in MINOR_MODES and right_triad in MINOR_MODES:	
			if	self._is_dim(resolving_chord): # maj7b5
				leading_chord.append(leading_chord[0]+12)
				leading_chord[0] += 1
				leading_chord[1] += 1
				chord_notation += "maj7b5"
			else:	#dim7 ... if ii -> iii, could do iim7, v7/iii, iiim7
				leading_chord.append(leading_chord[0]+10)
				leading_chord[1] += 1
				chord_notation += "o7"
		else: #left_triad in MAJOR_MODES and right_triad in MAJOR_MODES:	
			#dim7
			leading_chord.append(leading_chord[0]+10)
			chord_notation += "o7"


		return leading_chord, chord_notation
		#If the scale doesn't have [(0,), (1, 2), (3, 4), (5,), (6, 7), (8, 9), (10, 11)]
		# 0 == abs(left_note-right_note)%3 and (left_note, right_note) not in [(1,4), (6,9), (8,11)]
		
	def _is_major(self, chord):
		#intervals are M3 and m3
		return (chord[1]-chord[0] == 4 and chord[2]-chord[1] == 3)
	
	def _is_minor(self, chord):
		#intervals are m3 and M3
		return (chord[1]-chord[0] == 3 and chord[2]-chord[1] == 4)
	
	def _is_dim(self, chord):
		#intervals in triad are both m3
		return (chord[1]-chord[0] == chord[2]-chord[1] == 3)

	def _is_aug(self, chord):
		#intervals in triad are both m3
		return (chord[1]-chord[0] == chord[2]-chord[1] == 4)

	def _get_dim_notation(self, chord, _7th):
		notation = _7th
		if self._is_dim(chord):
			if _7th != "":
				notation = ("o" + _7th) if (chord[3]-chord[2] == 3) else (_7th +"b5")
		else:
			pass#not even diminished
		return notation
		
