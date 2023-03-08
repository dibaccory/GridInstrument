import collections
from enum import Enum

SCALE = collections.OrderedDict([
	('Major',		[0, 2, 4, 5, 7, 9, 11]),

	#modes
	('Aeolian',		[0, 2, 3, 5, 7, 8, 10]),
	('Dorian',		[0, 2, 3, 5, 7, 9, 10]),
	('Mixolydian', 	[0, 2, 4, 5, 7, 9, 10]),
	('Lydian', 		[0, 2, 4, 6, 7, 9, 11]),
	('Phrygian', 	[0, 1, 3, 5, 7, 8, 10]),
	('Locrian', 	[0, 1, 3, 5, 6, 8, 10]),

	('Diminished', 	[0, 1, 3, 4, 6, 7, 9, 10]),
	('Whole-half', 	[0, 2, 3, 5, 6, 8, 9, 11]),
	('Whole Tone', 	[0, 2, 4, 6, 8, 10]),
	('Minor Blues',	[0, 3, 5, 6, 7, 10]),
	('Minor Pentatonic', 	[0, 3, 5, 7, 10]),
	('Major Pentatonic', 	[0, 2, 4, 7, 9]),
	('Harmonic Minor', 		[0, 2, 3, 5, 7, 8, 11]),
	('Melodic Minor', 		[0, 2, 3, 5, 7, 9, 11]),

	('Super Locrian', 		[0, 1, 3, 4, 6, 8, 10]),
	('Bhairav', 			[0, 1, 4, 5, 7, 8, 11]),
	('Hungarian Minor', 	[0, 2, 3, 6, 7, 8, 11]),
	('Minor Gypsy', 		[0, 1, 4, 5, 7, 8, 10]),
	('Hirojoshi', 			[0, 2, 3, 7, 8]),
	('In-Sen', 				[0, 1, 5, 7, 10]),
	('Iwato', 				[0, 1, 5, 6, 10]),
	('Kumoi', 				[0, 2, 3, 7, 9]),
	('Pelog', 				[0, 1, 3, 4, 7, 8]),
	('Spanish', 			[0, 1, 3, 4, 5, 6, 8, 10]),
	('IonEol', 				[0, 2, 3, 4, 5, 7, 8, 9, 10, 11])
])

SCALE_NAMES = list(SCALE.keys())

MODE_NAMES = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]

#NOTE: triads on the / diagonal are all naturally diminished. This will be added in the class Chord
MODAL_TRIADS = collections.OrderedDict([
	("Ionian",		["I", 	"ii", 	"iii", 	"IV", 	"V", 	"vi", 	"vii"]),
    ("Dorian",		["i", 	"ii", 	"bIII", "IV", 	"v", 	"vi", 	"bVII"]),
    ("Phrygian",	["i", 	"bII", 	"bIII", "iv", 	"v", 	"bVI", 	"bvii"]),
    ("Lydian",		["I", 	"II", 	"iii", 	"iv",	"V", 	"vi", 	"vii"]),
    ("Mixolydian",	["I", 	"ii", 	"iii",	"IV", 	"v", 	"vi", 	"bVII"]),
    ("Aeolian",		["i", 	"ii",	"bIII", "IV", 	"v", 	"bVI", 	"bVII"]),
    ("Locrian",		["i", 	"bII", 	"biii", "iv",	"bV", 	"bVI", 	"bvii"]),
])

SCALE_CHORDS = {
    "I": []
}