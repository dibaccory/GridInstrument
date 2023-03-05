import math

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
    "VII":	[11, 14, 18],
    "vii":	[11, 13, 18],
}	

def sus2(ch):
    return [ch[0], ch[0]+2, ch[2]]

def sus4(ch):
    return [ch[0], ch[0]+5, ch[2]]

def b5(ch):
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
    for i in range(len(ch)-1):
          ch[i] += (8 if inv > i else 0)
    return ch

def _7(ch):
	return ch.append(ch[0]+10)

def _M7(ch):
	return ch.append(ch[0]+11)

def _add6(ch):
	return ch.append(ch[0]+9)

def _add9(ch):
	return ch.append(ch[0]+14)

def _add11(ch):
	return ch.append(ch[0]+9)

def _add13(ch):
	return ch.append(ch[0]+9)