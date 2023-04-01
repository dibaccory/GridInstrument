class Color:
	RED =		[0X3F, 0X00, 0X00]
	ORANGE =	[0X3F, 0X1F, 0X00]
	YELLOW =	[0X3F, 0X3F, 0X00]
	GREEN =		[0X00, 0X3F, 0X00]
	BLUE =		[0X00, 0X00, 0X3F]
	PURPLE =	[0X1F, 0X00, 0X3F]
	PINK =		[0X3F, 0X00, 0X3F]
	WHITE =		[0X3F, 0X3F, 0X3F]

	@staticmethod
	def add(RGB, val):
		return [max(0, min(0x3F, color+val)) for color in RGB]

	def adj_brightness(RGB, val):
		max_LED = max(RGB)
		ratios = [v / max_LED for v in RGB]
		adjusted = [max(0X00, min( 0X3F, int( (v + val*r) / (1 + r) ) )) for v, r in zip(RGB, ratios)]
		return adjusted

	def invert(RGB):
		return [(0X3F - v) for v in RGB]


NOTE_COLORS = {
	"note": {
            "on": 			[0X3F, 0X3F, 0X00],
	        "root": 		[0X20, 0X00, 0X3F],
            "tonic": 		[0X3F, 0X25, 0X00],
            "in_scale": 	[0X03, 0X01, 0X10],
            "out_scale": 	[0X00, 0X00, 0X00]
        },
	"settings": {
        "key_selected": 	[0X3F, 0X00, 0X00],
		"key": 				[0X05, 0X00, 0X00],
        "layout_selected": 	[0X00, 0X00, 0X3F],
		"layout":	 		[0x00, 0X00, 0X05],
        "scale_selected": 	[0X00, 0X3F, 0X00],
		"scale": {
			"base_major": 	[0X35, 0X20, 0X20],
			"major": 		[0X3F, 0X10, 0X10],
			"jazz_major": 	[0X3F, 0X10, 0X3F],
			"base_minor": 	[0X20, 0X20, 0X35],
			"minor": 		[0X10, 0X10, 0X3F],
			"jazz_minor": 	[0X10, 0X3F, 0X30],
		},
		"mode":				[0X00, 0X00, 0X3F],
		"mode_selected":	[0X3F, 0X30, 0X3F],
		"mode_inc":			[0X20, 0X20, 0X20]
	}
}

SCALE_TRIAD_COLORS = {
    "root":     [0X20, 0X05, 0X3F],
    "major":    [0X10, 0X30, 0X10],
    "minor":    [0X10, 0X10, 0X30],
    "dim":      [0X20, 0X00, 0X38],
    "aug":      [0X28, 0X10, 0X05],
}

PAD_COLORS = {
	"chord": {
#		"off": 	Color.adj_brightness(Color.ORANGE, -0X10),
#		"on":	Color.
	}
}