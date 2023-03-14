import collections
from enum import Enum

SCALE = collections.OrderedDict([
    #first two rows: major on top, minor on bottoms

	#Top left
	('Major',				[0, 2, 4, 5, 7, 9, 11]), # W W H [W] W W H - parallel
    #III -> 0 1 3 5 7 8 10
    ('Harmonic Major',		[0, 2, 4, 5, 7, 8, 11]), # W W H [W] H b3 H  - asymmetric
    #III -> 0 1 3 4 7 8 10	flat 4th
    ('Melodic Major', 		[0, 2, 4, 5, 7, 8, 10]), # W W H [W] H W W - symmetric... Lydian of Melodic Minor??
    #III -> 0 1 3 4 6 8 10 	flat 4th, 5th
    ('Neopolitan Major', 	[0, 1, 3, 5, 7, 9, 11]), # H W W [W] W W H - symmetric
    #III -> 0 2 4 6 8 9 10
    
	#top right DERIVED SCALES
	('Major Blues',			[0, 2, 3, 4, 7, 9]),
	('Major Pentatonic', 	[0, 2, 4, 7, 9]),
	('Minor Blues',			[0, 3, 5, 6, 7, 10]), #Phy (start on bIII): 0 2 5 7 8 9, Lyd: 0 3 5 8 10 11
	('Minor Pentatonic', 	[0, 3, 5, 7, 10]),

	#mid left
	('Minor', 				[0, 2, 3, 5, 7, 8, 10]), #W H W [W] H b3 H
	('Harmonic Minor', 		[0, 2, 3, 5, 7, 8, 11]), #W H W [W] H b3 H
    ('Melodic Minor', 		[0, 2, 3, 5, 7, 9, 11]), #W H W [W] W W H
    ('Neopolitan Minor', 	[0, 1, 3, 5, 7, 8, 11]), #H W W [W] H b3 H
     
	('Whole Tone', 			[0, 2, 4, 6, 8, 10]),
	('Diminished', 			[0, 1, 3, 4, 6, 7, 9, 10]),
    ('Whole-half', 			[0, 2, 3, 5, 6, 8, 9, 11]),
    ('m7b5 Dim. Scale', 	[0, 2, 4, 5, 6, 8, 10, 11]),

	('9 Harmonic Major Blues',		[0, 2, 3, 5, 6, 7, 9, 10, 11]), #Based on Harmonic Major (Lydian, add b3, b7)
    #3 -> 0 2 3 4 6 7 8 9 10 
    ('9 Melodic Major Blues',		[0, 2, 3, 4, 5, 7, 9, 10, 11]), # I ii bIII iii
    
	('Bebop Major', 		[0, 2, 4, 5, 7, 8, 9, 11]),
    ('Bebop Dominant', 		[0, 2, 4, 5, 7, 9, 10, 11]),
    ('Bebop Mel. Minor', 	[0, 2, 3, 5, 7, 8, 9, 11]),

	('Hungarian Minor', 	[0, 2, 3, 6, 7, 8, 11]), #b5
    ('Super Locrian', 		[0, 1, 3, 4, 6, 8, 10]),
	('Bhairav', 			[0, 1, 4, 5, 7, 8, 11]),
	('Minor Gypsy', 		[0, 1, 4, 5, 7, 8, 10]),
])

SCALE_NAMES = list(SCALE.keys())


#NOTE: These Modes are ONLY for Diatonic scales...
#TODO: Leading Triads for applied scales
#NOTE: Derived scale: Major Pentatonic, Applied scale: Major (rem 4th deg, 7th deg)

#NOTE: Derived scale: Nine-note Blues, applied: Major (add b3, b7)
#-> Degree:		1		2		b3	
#->	Intervals:	0 		2 		3	 		5 		*6* 		7 		9 		*10* 			11
#-> Chords:		im7		II7		bIIIM7		IV7		viio7/V		vm7		vim7	VM7/bIII	viiM7b5
#->	Intervals:	0 		2 		*3*	 		4 		5 			7 		9 		*10* 			11
#-> Chords:		IM7		iim7	bIIIM7		iiiM7	IVM7		Vm7		vim7	bVIIM7		viiM7b5
MODE_NAMES = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]

#NOTE: triads on the / diagonal are all naturally diminished. This will be added in the class Chord
#in chromatic: Leading triads always dim, but for 7ths: Maj -> min OR min -> dim = dim maj7, min -> min = o7, Maj -> Maj = m7b5

#blues scale = minor pentatonic w leading 4 to 5. Lets say that lead is 7th, then blues scale starts in Mixolydian. 
#Triads:	i	II 	bIII 		IV 	[vii/v 	 OR bv]			v 	vi 	 (bVII		=== V/bIII) 	vii								0 2 3 5 6 7 9 10 11
#Jazz:		im7 II7 bIIImaj7 	IV7 [viio7/V OR bVIIb9/V] 	vm7 vim7 (bVIImaj7 	=== Vmaj7/bIII) [viio7 	OR (viimaj7b5 === bVIIb9) ]  
MODAL_TRIADS = collections.OrderedDict([
	("Ionian",		["I", 	"ii", 	"iii", 	"IV", 	"V", 	"vi", 	"vii"]),
    ("Dorian",		["i", 	"ii", 	"bIII", "IV", 	"v", 	"vi", 	"bVII"]),
    ("Phrygian",	["i", 	"bII", 	"bIII", "iv", 	"v", 	"bVI", 	"bvii"]),
    ("Lydian",		["I", 	"II", 	"iii", 	"#iv",	"V", 	"vi", 	"vii"]),
    ("Mixolydian",	["I", 	"ii", 	"iii",	"IV", 	"v", 	"vi", 	"bVII"]),
    ("Aeolian",		["i", 	"ii",	"bIII", "IV", 	"v", 	"bVI", 	"bVII"]),
    ("Locrian",		["i", 	"bII", 	"biii", "iv",	"bV", 	"bVI", 	"bvii"]),
])

MAJOR_MODES=["I", "bII", "II", "bIII", "III", "IV", "bV", "V", "bVI", "VI", "bVII", "VII"]

MINOR_MODES=["i", "bii", "ii", "biii", "iii", "iv", "bv", "v", "bvi", "vi", "bvii", "vii"]


numeral_intervals = [(0,), (1, 2), (3, 4), (5,), (6, 7), (8, 9), (10, 11)]
#removing Modes... we want to apply the mode as a function for each scale
#SCALE_TRIADS = collections.OrderedDict([ (, ) for k in numeral_intervals])

#Mode 1 (0):	i | II 	| bIII | IV  | bv | v | vi 	| bVII | vii  |	0 2 3 5 6 7 9 10 11
#Mode 2 (1):	I | bII	| bIII | III | iv |	v | bvi	| VI   | bvii |	0 1 3 4 5 7 8 9  10 

SCALE_TRIADS = collections.OrderedDict([
	('Major',				MODAL_TRIADS["Ionian"]),
    ('Harmonic Major',		["I", "ii", "iii", "iv", "V", "bVI", "vii"])
    #TODO... all of these numerals LOL
	#('Diminished', 	[0, 1, 3, 4, 6, 7, 9, 10]),
	#('Whole-half', 	[0, 2, 3, 5, 6, 8, 9, 11]),
	#('Whole Tone', 	[0, 2, 4, 6, 8, 10]),
	#('Minor Blues',	["i", "bIII", "IV", "vii/v", "v", "bVII"]), #Phy (start on bIII): 0 2 5 7 8 9, Lyd: 0 3 5 8 10 11
	#('Minor Pentatonic', 	[0, 3, 5, 7, 10]),
	#('Major Pentatonic', 	[0, 2, 4, 7, 9]),
	#('Harmonic Minor', 		[0, 2, 3, 5, 7, 8, 11]),
	#('Melodic Minor', 		[0, 2, 3, 5, 7, 9, 11]),
#
	#('Super Locrian', 		[0, 1, 3, 4, 6, 8, 10]),
	#('Bhairav', 			["I", "bII", "iii", "iv", "V?", "VI+", "??"][0, 1, 4, 5, 7, 8, 11]),
	#('Hungarian Minor', 	[0, 2, 3, 6, 7, 8, 11]),
	#('Minor Gypsy', 		[0, 1, 4, 5, 7, 8, 10]),
	#('Hirojoshi', 			[0, 2, 3, 7, 8]),
	#('In-Sen', 			[0, 1, 5, 7, 10]),
	#('Iwato', 				[0, 1, 5, 6, 10]),
	#('Kumoi', 				[0, 2, 3, 7, 9]),
	#('Pelog', 				[0, 1, 3, 4, 7, 8]),
	#('Spanish', 			[0, 1, 3, 4, 5, 6, 8, 10]),
	#('IonEol', 				[0, 2, 3, 4, 5, 7, 8, 9, 10, 11])
])