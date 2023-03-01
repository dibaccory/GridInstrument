import sys
import array
from pygame import midi
from pygame import time

from .pro import LaunchpadPro

########################################################################################
### CLASS LaunchpadPROMk3
###
### For 3-color Pro Mk3 Launchpads
########################################################################################
class LaunchpadProMk3( LaunchpadPro ):
	#
	# LED AND BUTTON NUMBERS IN RAW MODE
	#
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 90|  | 91|   |   |   |   |   |   | 98|  | 99|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	#         
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 80|  | 81|   |   |   |   |   |   |   |  | 89|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 70|  |   |   |   |   |   |   |   |   |  | 79|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 60|  |   |   |   |   |   |   | 67|   |  | 69|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 50|  |   |   |   |   |   |   |   |   |  | 59|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 40|  |   |   |   |   |   |   |   |   |  | 49|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 30|  |   |   |   |   |   |   |   |   |  | 39|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 20|  |   |   | 23|   |   |   |   |   |  | 29|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# | 10|  |   |   |   |   |   |   |   |   |  | 19|
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	#       
	#        +---+---+---+---+---+---+---+---+ 
	#        |101|102|   |   |   |   |   |108|
	#        +---+---+---+---+---+---+---+---+ 
	#        |  1|  2|   |   |   |   |   |  8|
	#        +---+---+---+---+---+---+---+---+ 
	#
	#
	# LED AND BUTTON NUMBERS IN XY CLASSIC MODE (X/Y)
	#
	#   9      0   1   2   3   4   5   6   7      8   
	#        +---+---+---+---+---+---+---+---+ 
	#        |0/0|   |2/0|   |   |   |   |   |         0
	#        +---+---+---+---+---+---+---+---+ 
	#         
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |0/1|   |   |   |   |   |   |   |  |   |  1
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |9/2|  |   |   |   |   |   |   |   |   |  |   |  2
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |5/3|   |   |  |   |  3
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |   |   |   |  |   |  4
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |   |   |   |  |   |  5
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |4/6|   |   |   |  |   |  6
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |   |   |   |  |   |  7
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |9/8|  |   |   |   |   |   |   |   |   |  |8/8|  8
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	#       
	#        +---+---+---+---+---+---+---+---+ 
	#        |   |1/9|   |   |   |   |   |   |         9
	#        +---+---+---+---+---+---+---+---+ 
	#        |/10|   |   |   |   |   |   |   |        10
	#        +---+---+---+---+---+---+---+---+ 
	#
	#
	# LED AND BUTTON NUMBERS IN XY PRO MODE (X/Y)
	#
	#   0      1   2   3   4   5   6   7   8      9
	#        +---+---+---+---+---+---+---+---+ 
	#        |1/0|   |3/0|   |   |   |   |   |         0
	#        +---+---+---+---+---+---+---+---+ 
	#         
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |1/1|   |   |   |   |   |   |   |  |   |  1
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |0/2|  |   |   |   |   |   |   |   |   |  |   |  2
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |6/3|   |   |  |   |  3
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |   |   |   |  |   |  4
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |   |   |   |  |   |  5
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |5/6|   |   |   |  |   |  6
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |   |  |   |   |   |   |   |   |   |   |  |   |  7
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	# |0/8|  |   |   |   |   |   |   |   |   |  |9/8|  8
	# +---+  +---+---+---+---+---+---+---+---+  +---+
	#       
	#        +---+---+---+---+---+---+---+---+ 
	#        |   |2/9|   |   |   |   |   |8/9|         9
	#        +---+---+---+---+---+---+---+---+ 
	#        |   |   |   |   |   |   |   |/10|        10
	#        +---+---+---+---+---+---+---+---+ 

	
	#-------------------------------------------------------------------------------------
	#-- Opens one of the attached Launchpad MIDI devices.
	#-- Uses search string "ProMK3", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadPro" method
	def Open( self, number = 0, name = "ProMk3" ):
		retval = super( LaunchpadProMk3, self ).Open( number = number, name = name )
		if retval == True:
			# enable Programmer's mode
			self.LedSetMode( 1 )
		return retval


	#-------------------------------------------------------------------------------------
	#-- Checks if a device exists, but does not open it.
	#-- Does not check whether a device is in use or other, strange things...
	#-- Uses search string "ProMk3", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadPro" method
	def Check( self, number = 0, name = "ProMk3" ):
		return super( LaunchpadProMk3, self ).Check( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- Selects the ProMk3's mode.
	#-- <mode> -> 0 -> "Ableton Live mode"  
	#--           1 -> "Programmer mode"	(what we need)
	#-------------------------------------------------------------------------------------
	def LedSetMode( self, mode ):
		if mode < 0 or mode > 1:
			return
			
		self.midi.RawWriteSysEx( [ 0, 32, 41, 2, 14, 14, mode ] )
		time.wait(100)


	#-------------------------------------------------------------------------------------
	#-- Controls a grid LED by its position <number> and a color, specified by
	#-- <red>, <green> and <blue> intensities, with can each be an integer between 0..63.
	#-- If <blue> is omitted, this methos runs in "Classic" compatibility mode and the
	#-- intensities, which were within 0..3 in that mode, are multiplied by 21 (0..63)
	#-- to emulate the old brightness feeling :)
	#-- Notice that each message requires 10 bytes to be sent. For a faster, but
	#-- unfortunately "not-RGB" method, see "LedCtrlRawByCode()"
	#-- ProMk3 color data extended to 7-bit but for compatibility we still using 6-bit values
	#-------------------------------------------------------------------------------------
	def LedCtrlRaw( self, number, red, green, blue = None ):

		if number < 0 or number > 99:
			return

		if blue is None:
			blue   = 0
			red   *= 21
			green *= 21
		
		limit = lambda n, mini, maxi: max(min(maxi, n), mini)
		
		red   = limit( red,   0, 63 ) << 1
		green = limit( green, 0, 63 ) << 1
		blue  = limit( blue,  0, 63 ) << 1
		
		self.midi.RawWriteSysEx( [ 0, 32, 41, 2, 14, 3, 3, number, red, green, blue ] )
	

	#-------------------------------------------------------------------------------------
	#-- Same as LedCtrlRawByCode, but with a pulsing LED.
	#-- Pulsing can be stoppped by another Note-On/Off or SysEx message.
	#-------------------------------------------------------------------------------------
	def LedCtrlPulseByCode( self, number, colorcode = None ):

		if number < 0 or number > 99:
			return

		if colorcode is None:
			colorcode = LaunchpadPro.COLORS['white']

		colorcode = min(127, max(0, colorcode))

		self.midi.RawWrite( 146, number, colorcode )


	#-------------------------------------------------------------------------------------
	#-- Same as LedCtrlPulseByCode, but with a dual color flashing LED.
	#-- The first color is the one that is already enabled, the second one is the
	#-- <colorcode> argument in this method.
	#-- Flashing can be stoppped by another Note-On/Off or SysEx message.
	#-------------------------------------------------------------------------------------
	def LedCtrlFlashByCode( self, number, colorcode = None ):

		if number < 0 or number > 99:
			return

		if colorcode is None:
			colorcode = LaunchpadPro.COLORS['white']

		colorcode = min(127, max(0, colorcode))

		self.midi.RawWrite( 145, number, colorcode )


	#-------------------------------------------------------------------------------------
	#-- Quickly sets all all LEDs to the same color, given by <colorcode>.
	#-- If <colorcode> is omitted, "white" is used.
	#-------------------------------------------------------------------------------------
	def LedAllOn( self, colorcode = None ):
		if colorcode is None:
			colorcode = LaunchpadPro.COLORS['white']
		
		colorcode = min(127, max(0, colorcode))

		# TODO: Maybe the SysEx was indeed a better idea :)
		#       Did some tests:
		#         MacOS:   doesn't matter;
		#         Windoze: SysEx much better;
		#         Linux:   completely freaks out
		for x in range(9):
			for y in range(9):
				# TODO
				self.midi.RawWrite(144, (x + 1) + ((y + 1) * 10), colorcode)


	#-------------------------------------------------------------------------------------
	#-- Returns the raw value of the last button change (pressed/unpressed) as a list
	#-- [ <x>, <y>, <value> ], in which <x> and <y> are the buttons coordinates and
	#-- <value> is the intensity from 0..127.
	#-- >0 = button pressed; 0 = button released
	#-- Notice that this is not (directly) compatible with the original ButtonStateRaw()
	#-- method in the "Classic" Launchpad, which only returned [ <button>, <True/False> ].
	#-- Compatibility would require checking via "== True" and not "is True".
	#-------------------------------------------------------------------------------------
	def ButtonStateXY( self, mode = "classic", returnPressure = False ):
		if self.midi.ReadCheck():
			a = self.midi.ReadRaw()

			# 8/2020: Try to mitigate too many pressure events that a bit (yep, seems to work fine!)
			# 9/2020: XY now also with pressure event functionality
			if returnPressure == False:
				while a[0][0][0] == 208:
					a = self.midi.ReadRaw()
					if a == []:
						return []

			if a[0][0][0] == 144 or a[0][0][0] == 176:
			
				if mode.lower() != "pro":
					x = (a[0][0][1] - 1) % 10
				else:
					x = a[0][0][1] % 10
				if a[0][0][1] > 99:
					y = 9
				elif a[0][0][1] < 10:
					y = 10
				else:
					y = ( 99 - a[0][0][1] ) // 10
			
				return [ x, y, a[0][0][2] ]
			else:
				# TOCHK: this should be safe without checking "returnPressure"
				if a[0][0][0] == 208:
					return [ 255, 255, a[0][0][1] ]
				else:
					return []
		else:
			return []


	#-------------------------------------------------------------------------------------
	#-- (fake to) reset the Launchpad
	#-- Turns off all LEDs
	#-------------------------------------------------------------------------------------
	def Reset( self ):
		self.LedAllOn( 0 )


	#-------------------------------------------------------------------------------------
	#-- Go back to custom modes before closing connection
	#-- Otherwise Launchpad will stuck in programmer mode
	#-------------------------------------------------------------------------------------
	def Close( self ):
		# re-enter Live mode
		if self.midi.devIn != None and self.midi.devOut != None:
			self.LedSetMode( 0 )
		# TODO: redundant (but needs fix for Py2 embedded anyway)
		# self.midi.CloseInput()
		# self.midi.CloseOutput()
