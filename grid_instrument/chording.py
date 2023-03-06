import math
from .scales import *

#How to instantiate chords in a mode?
#If we instantiate by the current musical mode, we should find chords by scale note?
#chord = Chord(MODES["Major"])
#chord(1, self.seveth (BOOL), ext="", mod=0, sec=0, inv=0)
#chord(1) -> I					chord(posInScale+1) -> if posInScale = 0, I
#chord(1, "7") -> Imaj7
#chord(2, "7") -> ii7
#chord(1, "add9") -> Iadd9
#chord(1, "7 add9") -> Imaj7add9
#chord(1, "9") -> I9 -> Imaj7add9
#chord(1, "6") -> I 1st inversion -> chord(1, inv=1)
#chord(1, "6/9") -> I6/9 -> I6add9 
#chord(1, "7", mod=4) -> Modal interchange of I using mode index 4 (Mixolydian) -> I7
#chord(2, "7", sec="1") -> Dominant chord of 2, add 7th -> V7/ii
#chord(2, "7", sec="2") -> Leading chord of 2, add 7th -> vii7b5/ii
#chord.update(MODES["something_else"])

CRD = {
	#tonic: 0, subdom: 5, dom: 7
	#No inversions, so chords may have intervals past 12
	"I":	[0, 4, 7],
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


	def __init__(self, scale, jazzy=False):
		self.scale = scale
		self.jazzy = jazzy

	def __call__(self, degree, jazzy, ext="", mod=0, sec=0, inv=0):
		scale_length = len(SCALE[self.scale])

		#Get triad from scale
		chord = [ 
			SCALE[self.scale][degree],
			SCALE[self.scale][(degree+2)%scale_length],
			SCALE[self.scale][(degree+4)%scale_length],
	   	]

		#Check triad type (major, minor, + (aug), o (dim))

		return chord
