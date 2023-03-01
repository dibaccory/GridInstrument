#!/usr/bin/env python
#
# A Novation Launchpad control suite for Python.
#
# https://github.com/FMMT666/launchpad.py
# 
# FMMT666(ASkr) 01/2013..09/2019..08/2020..05/2021
# www.askrprojects.net
#
#
#
#  >>>
#  >>> NOTICE FOR SPACE USERS:
#  >>>
#  >>>  Yep, this one uses tabs. Tabs everywhere.
#  >>>  Deal with it :-)
#  >>>
#

import string
import random
import sys
import array

from pygame import midi
from pygame import time


try:
	from .charset import *
except ImportError:
	try:
		from charset import *
	except ImportError:
		sys.exit("error loading Launchpad charset")

print("we in my world now bitch")


##########################################################################################
### CLASS Midi
### Midi singleton wrapper
##########################################################################################
class Midi:

	# instance created 
	instanceMidi = None

	#---------------------------------------------------------------------------------------
	#-- init
	#-- Allow only one instance to be created
	#---------------------------------------------------------------------------------------
	def __init__( self ):
		if Midi.instanceMidi is None:
			try:
				Midi.instanceMidi = Midi.__Midi()
			except:
				# TODO: maybe sth like sys.exit()?
				print("unable to initialize MIDI")
				Midi.instanceMidi = None

		self.devIn  = None
		self.devOut = None


	#---------------------------------------------------------------------------------------
	#-- getattr
	#-- Pass all unknown method calls to the inner Midi class __Midi()
	#---------------------------------------------------------------------------------------
	def __getattr__( self, name ):
		return getattr( self.instanceMidi, name )
	

	#-------------------------------------------------------------------------------------
	#--
	#-------------------------------------------------------------------------------------
	def OpenOutput( self, midi_id ):
		if self.devOut is None:
			try:
				# PyGame's default size of the buffer is 4096.
				# Removed code to tune that...
				self.devOut = midi.Output( midi_id, 0 )
			except:
				self.devOut = None
				return False
		return True


	#-------------------------------------------------------------------------------------
	#--
	#-------------------------------------------------------------------------------------
	def CloseOutput( self ):
		if self.devOut is not None:
			#self.devOut.close()
			del self.devOut
			self.devOut = None


	#-------------------------------------------------------------------------------------
	#--
	#-------------------------------------------------------------------------------------
	def OpenInput( self, midi_id, bufferSize = None ):
		if self.devIn is None:
			try:
				# PyGame's default size of the buffer is 4096.
				if bufferSize is None:
					self.devIn = midi.Input( midi_id )
				else:
					# for experiments...
					self.devIn = midi.Input( midi_id, bufferSize )
			except:
				self.devIn = None
				return False
		return True


	#-------------------------------------------------------------------------------------
	#--
	#-------------------------------------------------------------------------------------
	def CloseInput( self ):
		if self.devIn is not None:
			#self.devIn.close()
			del self.devIn
			self.devIn = None


	#-------------------------------------------------------------------------------------
	#--
	#-------------------------------------------------------------------------------------
	def ReadCheck( self ):
		return self.devIn.poll()

		
	#-------------------------------------------------------------------------------------
	#--
	#-------------------------------------------------------------------------------------
	def ReadRaw( self ):
		return self.devIn.read( 1 )


	#-------------------------------------------------------------------------------------
	#-- sends a single, short message
	#-------------------------------------------------------------------------------------
	def RawWrite( self, stat, dat1, dat2 ):
		self.devOut.write_short( stat, dat1, dat2 )

		
	#-------------------------------------------------------------------------------------
	#-- Sends a list of messages. If timestamp is 0, it is ignored.
	#-- Amount of <dat> bytes is arbitrary.
	#-- [ [ [stat, <dat1>, <dat2>, <dat3>], timestamp ],  [...], ... ]
	#-- <datN> fields are optional
	#-------------------------------------------------------------------------------------
	def RawWriteMulti( self, lstMessages ):
		self.devOut.write( lstMessages )

	
	#-------------------------------------------------------------------------------------
	#-- Sends a single system-exclusive message, given by list <lstMessage>
	#-- The start (0xF0) and end bytes (0xF7) are added automatically.
	#-- [ <dat1>, <dat2>, ..., <datN> ]
	#-- Timestamp is not supported and will be sent as '0' (for now)
	#-------------------------------------------------------------------------------------
	def RawWriteSysEx( self, lstMessage, timeStamp = 0 ):
		# There's a bug in PyGame's (Python 3) list-type message handling, so as a workaround,
		# we'll use the string-type message instead...
		#self.devOut.write_sys_ex( timeStamp, [0xf0] + lstMessage + [0xf7] ) # old Python 2

		# array.tostring() deprecated in 3.9; quickfix ahead
		try:
			self.devOut.write_sys_ex( timeStamp, array.array('B', [0xf0] + lstMessage + [0xf7] ).tostring() )
		except:
			self.devOut.write_sys_ex( timeStamp, array.array('B', [0xf0] + lstMessage + [0xf7] ).tobytes() )



	########################################################################################
	### CLASS __Midi
	### The rest of the Midi class, non Midi-device specific.
	########################################################################################
	class __Midi:

		#-------------------------------------------------------------------------------------
		#-- init
		#-------------------------------------------------------------------------------------
		def __init__( self ):
			# exception handling moved up to Midi()
			midi.init()
			# but I can't remember why I put this one in here...
			midi.get_count()

				
		#-------------------------------------------------------------------------------------
		#-- del
		#-- This will never be executed, because no one knows, how many Launchpad instances
		#-- exist(ed) until we start to count them...
		#-------------------------------------------------------------------------------------
		def __del__( self ):
			#midi.quit()
			pass


		#-------------------------------------------------------------------------------------
		#-- Returns a list of devices that matches the string 'name' and has in- or outputs.
		#-------------------------------------------------------------------------------------
		def SearchDevices( self, name, output = True, input = True, quiet = True ):
			ret = []

			for i in range( midi.get_count() ):
				md = midi.get_device_info( i )
				if name.lower() in str( md[1].lower() ):
					if quiet == False:
						print('%2d' % ( i ), md)
						sys.stdout.flush()
					if output == True and md[3] > 0:
						ret.append( i )
					if input == True and md[2] > 0:
						ret.append( i )

			return ret

			
		#-------------------------------------------------------------------------------------
		#-- Returns the first device that matches the string 'name'.
		#-- NEW2015/02: added number argument to pick from several devices (if available)
		#-------------------------------------------------------------------------------------
		def SearchDevice( self, name, output = True, input = True, number = 0 ):
			ret = self.SearchDevices( name, output, input )
			
			if number < 0 or number >= len( ret ):
				return None

			return ret[number]


		#-------------------------------------------------------------------------------------
		#-- Return MIDI time
		#-------------------------------------------------------------------------------------
		def GetTime( self ):
			return midi.time()
		

MSG = {
	"note_off": 0x80,
	"note_on":	0x90,
	"cc":		0xB0
}


########################################################################################
### CLASS LaunchpadBase
###
########################################################################################
class LaunchpadBase( object ):

	def __init__( self ):
		self.midi   = Midi() # midi interface instance (singleton)
		self.idOut  = None   # midi id for output
		self.idIn   = None   # midi id for input
		# scroll directions
		self.SCROLL_NONE  =  0
		self.SCROLL_LEFT  = -1
		self.SCROLL_RIGHT =  1
		self.CHANNEL = 0x0D #CHANNEL14 BY DEFAULT.... TODO: FIX!!!! LOL

	# LOL; That fixes a years old bug. Officially an idiot now :)
#	def __delete__( self ):
	def __del__( self ):
		self.Close()
		

	#-------------------------------------------------------------------------------------
	#-- Opens one of the attached Launchpad MIDI devices.
	#-------------------------------------------------------------------------------------
	def Open( self, number = 0, name = "Launchpad" ):
		self.idOut = self.midi.SearchDevice( name, True, False, number = number )
		self.idIn  = self.midi.SearchDevice( name, False, True, number = number )
		
		if self.idOut is None or self.idIn is None:
			return False

		if self.midi.OpenOutput( self.idOut ) == False:
			return False
		
		return self.midi.OpenInput( self.idIn )


	#-------------------------------------------------------------------------------------
	#-- Checks if a device exists, but does not open it.
	#-- Does not check whether a device is in use or other, strange things...
	#-------------------------------------------------------------------------------------
	def Check( self, number = 0, name = "Launchpad" ):
		self.idOut = self.midi.SearchDevice( name, True, False, number = number )
		self.idIn  = self.midi.SearchDevice( name, False, True, number = number )
		
		if self.idOut is None or self.idIn is None:
			return False
		
		return True


	#-------------------------------------------------------------------------------------
	#-- Closes this device
	#-------------------------------------------------------------------------------------
	def Close( self ):
		self.midi.CloseInput()
		self.midi.CloseOutput()
	

	#-------------------------------------------------------------------------------------
	#-- prints a list of all devices to the console (for debug)
	#-------------------------------------------------------------------------------------
	def ListAll( self, searchString = '' ):
		self.midi.SearchDevices( searchString, True, True, False )


	#-------------------------------------------------------------------------------------
	#-- Clears the button buffer (The Launchpads remember everything...)
	#-- Because of empty reads (timeouts), there's nothing more we can do here, but
	#-- repeat the polls and wait a little...
	#-------------------------------------------------------------------------------------
	def ButtonFlush( self ):
		doReads = 0
		# wait for that amount of consecutive read fails to exit
		while doReads < 3:
			if self.midi.ReadCheck():
				doReads = 0
				self.midi.ReadRaw()
			else:
				doReads += 1
				time.wait( 5 )


	#-------------------------------------------------------------------------------------
	#-- Returns a list of all MIDI events, empty list if nothing happened.
	#-- Useful for debugging or checking new devices.
	#-------------------------------------------------------------------------------------
	def EventRaw( self ):
		if self.midi.ReadCheck():
			return self.midi.ReadRaw()
		else:
			return []







########################################################################################
### CLASS LaunchKey
###
### For 2-color LaunchKey Keyboards 
########################################################################################
class LaunchKeyMini( LaunchpadBase ):

	# LED, BUTTON, KEY AND POTENTIOMETER NUMBERS IN RAW MODE (DEC)
	# NOTICE THAT THE OCTAVE BUTTONS SHIFT THE KEYS UP OR DOWN BY 12.
	#
	# LAUNCHKEY MINI:
	# 
	#                   +---+---+---+---+---+---+---+---+
	#                   | 21| 22|...|   |   |   |   | 28|
	#     +---+---+---+ +---+---+---+---+---+---+---+---+ +---+  +---+
	#     |106|107|NOP| | 40| 41| 42| 43| 48| 49| 50| 51| |108|  |104| 
	#     +---+---+---+ +---+---+---+---+---+---+---+---+ +---+  +---+
	#     |NOP|NOP|     | 36| 37| 38| 39| 44| 45| 46| 47| |109|  |105| 
	#     +---+---+     +---+---+---+---+---+---+---+---+ +---+  +---+
	#
	#     +--+-+-+-+--+--+-+-+-+-+-+--+--+-+-+-+--+--+-+-+-+-+-+--+---+
	#     |  | | | |  |  | | | | | |  |  | | | |  |  | | | | | |  |   |
	#     |  |4| |5|  |  | | | | | |  |  |6| | |  |  | | | | |7|  |   |
	#     |  |9| |1|  |  | | | | | |  |  |1| | |  |  | | | | |0|  |   |
	#     |  +-+ +-+  |  +-+ +-+ +-+  |  +-+ +-+  |  +-+ +-+ +-+  |   |
	#     | 48| 50| 52|   |   |   |   | 60|   |   |   |   |   | 71| 72|
	#     |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
	#     | C | D | E |...|   |   |   | C2| D2|...|   |   |   |   | C3|
	#     +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#
	#
	# LAUNCHKEY 25/49/61:
	#
	#    SLIDERS:           41..48
	#    SLIDER (MASTER):   7
	#
	


	#-------------------------------------------------------------------------------------
	#-- Opens one of the attached LaunchKey devices.
	#-- Uses search string "LaunchKey", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadBase" method
	def Open( self, number = 0, name = "LaunchKey" ):
		retval = super( LaunchKeyMini, self ).Open( number = number, name = name )
		return retval


	#-------------------------------------------------------------------------------------
	#-- Checks if a device exists, but does not open it.
	#-- Does not check whether a device is in use or other, strange things...
	#-- Uses search string "LaunchKey", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadBase" method
	def Check( self, number = 0, name = "LaunchKey" ):
		return super( LaunchKeyMini, self ).Check( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- Returns the raw value of the last button, key or potentiometer change as a list:
	#-- potentiometers:   <pot.number>, <value>     , 0          ] 
	#-- buttons:          <but.number>, <True/False>, <velocity> ]
	#-- keys:             <but.number>, <True/False>, <velocity> ]
	#-- If a button does not provide an analog value, 0 or 127 are returned as velocity values.
	#-- Because of the octave settings cover the complete note range, the button and potentiometer
	#-- numbers collide with the note numbers in the lower octaves.
	#-------------------------------------------------------------------------------------
	def InputStateRaw( self ):
		if self.midi.ReadCheck():
			a = self.midi.ReadRaw()
			
			#--- pressed key
			if    a[0][0][0] == 144:
				return [ a[0][0][1], True, a[0][0][2] ] 
			#--- released key
			elif  a[0][0][0] == 128:
				return [ a[0][0][1], False, 0 ] 
			#--- pressed button
			elif  a[0][0][0] == 153:
				return [ a[0][0][1], True, a[0][0][2] ]
			#--- released button
			elif  a[0][0][0] == 137:
				return [ a[0][0][1], False, 0 ]
			#--- potentiometers and the four cursor buttons
			elif  a[0][0][0] == 176:
				# --- cursor, track and scene buttons
				if a[0][0][1] >= 104 and a[0][0][1] <= 109:
					if a[0][0][2] > 0:
						return [ a[0][0][1], True, 127 ]
					else:
						return [ a[0][0][1], False, 0 ]
				# --- potentiometers
				else:
					return [ a[0][0][1], a[0][0][2], 0 ]
			else:
				return []
		else:
			return []


	#-------------------------------------------------------------------------------------
	#-- Clears the input buffer (The Launchpads remember everything...)
	#-------------------------------------------------------------------------------------
	def InputFlush( self ):
		return self.ButtonFlush()


	#-------------------------------------------------------------------------------------
	#-- Returns True if an event occured.
	#-------------------------------------------------------------------------------------
	def InputChanged( self ):
		return self.midi.ReadCheck()


########################################################################################
### CLASS Dicer
###
### For that Dicer thingy...
########################################################################################
class Dicer( LaunchpadBase ):

	# LED, BUTTON, KEY AND POTENTIOMETER NUMBERS IN RAW MODE (DEC)
	# NOTICE THAT THE OCTAVE BUTTONS SHIFT THE KEYS UP OR DOWN BY 10.
	#
	# FOR SHIFT MODE (HOLD ONE OF THE 3 MODE BUTTONS): ADD "5".
	#     +-----+  +-----+  +-----+             +-----+  +-----+  +-----+
	#     |#    |  |#    |  |     |             |#   #|  |#   #|  |    #|
	#     |  #  |  |     |  |  #  |             |  #  |  |     |  |  #  |
	#     |    #|  |    #|  |     |             |#   #|  |#   #|  |#    |
	#     +-----+  +-----+  +-----+             +-----+  +-----+  +-----+
	# 
	#     +-----+            +---+               +----+           +-----+
	#     |#   #|            | +0|               |+120|           |    #|
	#     |     |            +---+               +----+           |     |
	#     |#   #|       +---+                         +----+      |#    |
	#     +-----+       |+10|                         |+110|      +-----+
	#                   +---+                         +----+
	#     +-----+  +---+                                  +----+  +-----+
	#     |#   #|  |+20|                                  |+100|  |     |
	#     |  #  |  +---+                                  +----+  |  #  |
	#     |#   #|                                                 |     |
	#     +-----+                                                 +-----+
	# 
	# 


	#-------------------------------------------------------------------------------------
	#-- Opens one of the attached Dicer devices.
	#-- Uses search string "dicer", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadBase" method
	def Open( self, number = 0, name = "Dicer" ):
		retval = super( Dicer, self ).Open( number = number, name = name )
		return retval


	#-------------------------------------------------------------------------------------
	#-- Checks if a device exists, but does not open it.
	#-- Does not check whether a device is in use or other, strange things...
	#-- Uses search string "dicer", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadBase" method
	def Check( self, number = 0, name = "Dicer" ):
		return super( Dicer, self ).Check( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- reset the Dicer
	#-- Turns off all LEDs, restores power-on state, but does not disable an active light show.
	#-------------------------------------------------------------------------------------
	def Reset( self ):
		self.midi.RawWrite( 186, 0, 0 )


	#-------------------------------------------------------------------------------------
	#-- All LEDs off
	#-- Turns off all LEDs, does not change or touch any other settings.
	#-------------------------------------------------------------------------------------
	def LedAllOff( self ):
		self.midi.RawWrite( 186, 0, 112 )


	#-------------------------------------------------------------------------------------
	#-- Returns (an already nicely mapped and not raw :) value of the last button change as a list:
	#-- buttons: <number>, <True/False>, <velocity> ]
	#-- If a button does not provide an analog value, 0 or 127 are returned as velocity values.
	#-- Small buttons select either 154, 155, 156 cmd for master or 157, 158, 159 for slave.
	#-- Button numbers (1 to 5): 60, 61 .. 64; always
	#-- Guess it's best to return: 1..5, 11..15, 21..25 for Master and 101..105, ... etc for slave
	#-- Actually, as you can see, it's not "raw", but I guess those decade modifiers really
	#-- make sense here (less brain calculations for you :)
	#-------------------------------------------------------------------------------------
	def ButtonStateRaw( self ):
		if self.midi.ReadCheck():
			a = self.midi.ReadRaw()
			
			#--- button on master
			if   a[0][0][0] >= 154 and a[0][0][0] <= 156:
				butNum = a[0][0][1]
				if butNum >= 60 and butNum <= 69:
					butNum -= 59
					butNum += 10 * ( a[0][0][0]-154 )
					if a[0][0][2] == 127:
						return [ butNum, True, 127 ]
					else:
						return [ butNum, False, 0  ]
				else:
					return []
			#--- button on master
			elif a[0][0][0] >= 157 and a[0][0][0] <= 159:
				butNum = a[0][0][1]
				if butNum >= 60 and butNum <= 69:
					butNum -= 59
					butNum += 100 + 10 * ( a[0][0][0]-157 )
					if a[0][0][2] == 127:
						return [ butNum, True, 127 ]
					else:
						return [ butNum, False, 0  ]
				else:
					return []
		else:
			return []

	#-------------------------------------------------------------------------------------
	#-- Enables or diabled the Dicer's built-in light show.
	#-- Device: 0 = Master, 1 = Slave; enable = True/False
	#-------------------------------------------------------------------------------------
	def LedSetLightshow( self, device, enable ):
		# Who needs error checks anyway?
		self.midi.RawWrite( 186 if device == 0 else 189, 0, 40 if enable == True else 41 )


	#-------------------------------------------------------------------------------------
	#-- Returns a Dicer compatible "color code byte"
	#-- NOTE: Copied from Launchpad, won't work. The Dicer actually uses:
	#-- Byte: 0b[0HHHIIII]; HHH: 3 bits hue (000=red up to 111=green) and 4 bits IIII as intensity.
	#-------------------------------------------------------------------------------------
#	def LedGetColor( self, red, green ):
#		led = 0
#		
#		red = min( int(red), 3 ) # make int and limit to <=3
#		red = max( red, 0 )      # no negative numbers
#
#		green = min( int(green), 3 ) # make int and limit to <=3
#		green = max( green, 0 )      # no negative numbers
#
#		led |= red
#		led |= green << 4 
#		
#		return led


	#-------------------------------------------------------------------------------------
	#-- Controls an LED by its raw <number>; with <hue> brightness: 0..7 (red to green)
	#-- and <intensity> 0..15
	#-- For LED numbers, see grid description on top of class.
	#-------------------------------------------------------------------------------------
	def LedCtrlRaw( self, number, hue, intensity ):
		
		if number < 0 or number > 130:
			return
		
		# check if that is a slave device number (>100)
		if number > 100:
			number -= 100
			cmd = 157
		else:
			cmd = 154
			
		# determine the "page", "hot cue", "loop" or "auto loop"
		page = number // 10
		if page > 2:
			return

		# correct the "page shifted" LED number
		number = number - ( page * 10 )
		if number > 10:
			return
		
		# limit the hue range
		hue = min( int(hue), 7 ) # make int and limit to <=7
		hue = max( hue, 0 )      # no negative numbers

		# limit the intensity
		intensity = min( int(intensity), 15 ) # make int and limit to <=15
		intensity = max( intensity, 0 )       # no negative numbers
		
		self.midi.RawWrite( cmd + page, number + 59, (hue << 4) | intensity )


	#-------------------------------------------------------------------------------------
	#-- Sets the Dicer <device> (0=master, 1=slave) to one of its six modes,
	#-- as specified by <mode>:
	#--  0 - "cue"
	#--  1 - "cue, shift lock"
	#--  2 - "loop"
	#--  3 - "loop, shift lock"
	#--  4 - "auto loop"
	#--  5 - "auto loop, shift lock"
	#--  6 - "one page"
	#-------------------------------------------------------------------------------------
	def ModeSet( self, device, mode ):

		if device < 0 or device > 1:
			return

		if mode < 0 or mode > 6:
			return

		self.midi.RawWrite( 186 if device == 0 else 189, 17, mode )



########################################################################################
### CLASS MidiFighter64
###
### For Midi Fighter 64 Gedöns
########################################################################################
class MidiFighter64( LaunchpadBase ):

	#         
	# LED AND BUTTON NUMBERS IN RAW MODE
	#         
	#        +---+---+---+---+---+---+---+---+
	#        | 64|   |   | 67| 96|   |   | 99|
	#        +---+---+---+---+---+---+---+---+
	#        | 60|   |   | 63| 92|   |   | 95|
	#        +---+---+---+---+---+---+---+---+
	#        | 56|   |   | 59| 88|   |   | 91|
	#        +---+---+---+---+---+---+---+---+
	#        | 52|   |   | 55| 84|   |   | 87|
	#        +---+---+---+---+---+---+---+---+
	#        | 48|   |   | 51| 80|   |   | 83|
	#        +---+---+---+---+---+---+---+---+
	#        | 44|   |   | 47| 76|   |   | 79|
	#        +---+---+---+---+---+---+---+---+
	#        | 40|   |   | 43| 72|   |   | 75|
	#        +---+---+---+---+---+---+---+---+
	#        | 36|   |   | 39| 68|   |   | 71|
	#        +---+---+---+---+---+---+---+---+
	#
	#
	# LED AND BUTTON NUMBERS IN XY MODE (X/Y)
	#
	#          0   1   2   3   4   5   6   7
	#        +---+---+---+---+---+---+---+---+
	#        |0/0|   |   |   |   |   |   |   | 0
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |   |   |   |   | 1
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |   |5/2|   |   | 2
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |   |   |   |   | 3
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |   |   |   |   | 4
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |4/5|   |   |   | 5
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |   |   |   |   | 6
	#        +---+---+---+---+---+---+---+---+
	#        |   |   |   |   |   |   |   |   | 7
	#        +---+---+---+---+---+---+---+---+
	#


	#-------------------------------------------------------------------------------------
	#-- Add some LED mode "constants" for better usability.
	#-------------------------------------------------------------------------------------
	def __init__( self ):

		self.MODE_BRIGHT        = [ i+18 for i in range(16) ]
		self.MODE_TOGGLE        = [ i+34 for i in range(8) ]
		self.MODE_PULSE         = [ i+42 for i in range(8) ]
		self.MODE_ANIM_SQUARE   = 50
		self.MODE_ANIM_CIRCLE   = 51
		self.MODE_ANIM_STAR     = 52
		self.MODE_ANIM_TRIANGLE = 53

		super( MidiFighter64, self ).__init__( )



	#-------------------------------------------------------------------------------------
	#-- Opens one of the attached Launchpad MIDI devices.
	#-- Uses search string "Fighter 64", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadBase" method
	def Open( self, number = 0, name = "Fighter 64" ):
		return super( MidiFighter64, self ).Open( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- Checks if a device exists, but does not open it.
	#-- Does not check whether a device is in use or other, strange things...
	#-- Uses search string "Fighter 64", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "LaunchpadBase" method
	def Check( self, number = 0, name = "Fighter 64" ):
		return super( MidiFighter64, self ).Check( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- Controls a grid LED by its <number> and a <color>.
	#--  <number> 36..99
	#--  <color>   0..127 from color table
	#--  <mode>   18..53  for brightness, toggling and animation 
	#-------------------------------------------------------------------------------------
	def LedCtrlRaw( self, number, color, mode = None ):

		if number < 36 or number > 99:
			return
		if color  < 0  or color  > 127:
			return

		self.midi.RawWrite( 146, number, color )

		# faster than calling LedCtrlRawMode()
		if mode is not None and mode > 17 and mode < 54:
			self.midi.RawWrite( 147, number - 3*12, mode )


	#-------------------------------------------------------------------------------------
	#-- Controls a the mode of a grid LED by its <number> and the mode <mode> of the LED.
	#--  <number> 36..99
	#--  <mode>   18..53 for brightness, toggling and animation
	#-- Internal LED numbers are 3 octaves lower than the color numbers.
	#-- The mode must be sent over channel 4
	#-------------------------------------------------------------------------------------
	def LedCtrlRawMode( self, number, mode ):

		# uses the original button numbers for usability
		if number < 36 or number > 99:
			return
		if mode < 18 or mode > 53:
			return

		self.midi.RawWrite( 147, number - 3*12, mode )


	#-------------------------------------------------------------------------------------
	#-- Controls a grid LED by its <x>/<y> coordinates and a <color>.
	#--  <x>/<y>  0..7
	#--  <color>  0..127 from color table
	#-------------------------------------------------------------------------------------
	def LedCtrlXY( self, x, y, color, mode = None ):

		if x < 0 or x > 7:
			return
		if y < 0 or y > 7:
			return
		if color  < 0  or color  > 127:
			return

		if x < 4:
			number = 36 + x % 4
		else:
			number = 68 + x % 4
		
		number += (7-y) * 4

		self.midi.RawWrite( 146, number, color )
		# set the mode if required; faster than calling LedCtrlRawMode()
		if mode is not None and mode > 17 and mode < 54:
			self.midi.RawWrite( 147, number - 3*12, mode )


	#-------------------------------------------------------------------------------------
	#-- Displays the character <char> with color of <colorcode> and lateral offset
	#-- <offsx> (-8..8) on the Midi Fighter. <offsy> does not have yet any function.
	#-- <coloroff> specifies the background color.
	#-- Notice that the call to this method is not compatible to the Launchpad variants,
	#-- because the Midi Fighter lacks support for RGB.
	#-------------------------------------------------------------------------------------
	def LedCtrlChar( self, char, colorcode, offsx = 0, offsy = 0, coloroff = 0 ):
		char = ord( char )
		char = min( char, 255)
		char = max( char, 0) * 8

		if colorcode < 0 or colorcode > 127:
			return

		for y in range( 64, 35, -4 ):
			for x in range(8):
				number = y + x + offsx
				if x + offsx > 3:
					number += 28  # +32-4

				if x + offsx < 8 and x + offsx >= 0:
					if CHARTAB[char]  &  0x80 >> x:
						self.LedCtrlRaw( number, colorcode )
					else:
						# lol, shit; there is no color code for "off"
						self.LedCtrlRaw( number, coloroff )
			char += 1


	#-------------------------------------------------------------------------------------
	#-- Scroll <text>, with color specified by <colorcode>, as fast as we can.
	#-- <direction> specifies: -1 to left, 0 no scroll, 1 to right
	#-- Notice that the call to this method is not compatible to the Launchpad variants,
	#-- because the Midi Fighter lacks support for RGB.
	#-------------------------------------------------------------------------------------
	def LedCtrlString( self, text, colorcode, coloroff=0, direction = None, waitms = 150 ):

		limit = lambda n, mini, maxi: max(min(maxi, n), mini)

		if direction == self.SCROLL_LEFT:
			text += " " # just to avoid artifacts on full width characters
			for n in range( (len(text) + 1) * 8 ):
				if n <= len(text)*8:
					self.LedCtrlChar( text[ limit( (  n   //16)*2     , 0, len(text)-1 ) ], colorcode, 8- n   %16, coloroff = coloroff )
				if n > 7:
					self.LedCtrlChar( text[ limit( (((n-8)//16)*2) + 1, 0, len(text)-1 ) ], colorcode, 8-(n-8)%16, coloroff = coloroff )
				time.wait(waitms)
		elif direction == self.SCROLL_RIGHT:
			# TODO: Just a quick hack (screen is erased before scrolling begins).
			#       Characters at odd positions from the right (1, 3, 5), with pixels at the left,
			#       e.g. 'C' will have artifacts at the left (pixel repeated).
			text = " " + text + " " # just to avoid artifacts on full width characters
#			for n in range( (len(text) + 1) * 8 - 1, 0, -1 ):
			for n in range( (len(text) + 1) * 8 - 7, 0, -1 ):
				if n <= len(text)*8:
					self.LedCtrlChar( text[ limit( (  n   //16)*2     , 0, len(text)-1 ) ], colorcode, 8- n   %16, coloroff = coloroff )
				if n > 7:
					self.LedCtrlChar( text[ limit( (((n-8)//16)*2) + 1, 0, len(text)-1 ) ], colorcode, 8-(n-8)%16, coloroff = coloroff )
				time.wait(waitms)
		else:
			for i in text:
				for n in range(4):  # pseudo repetitions to compensate the timing a bit
					self.LedCtrlChar(i, colorcode, coloroff = coloroff)
					time.wait(waitms)


	#-------------------------------------------------------------------------------------
	#-- Sets all LEDs to the same color, specified by <color>.
	#-- If color is omitted, the LEDs are set to white (code 3)
	#-------------------------------------------------------------------------------------
	def LedAllOn( self, color = 3, mode = None ):
		for i in range(64):
			self.LedCtrlRaw( i+36, color, mode )


	#-------------------------------------------------------------------------------------
	#-- Returns the raw value of the last button change (pressed/unpressed) as a list
	#-- [ <button>, <velocity> ], in which <button> is the raw number of the button and
	#-- <velocity> the button state.
	#--   >0 = button pressed; 0 = button released
	#-------------------------------------------------------------------------------------
	def ButtonStateRaw( self ):
		if self.midi.ReadCheck():
			a = self.midi.ReadRaw()

			# The Midi Fighter 64 does not support velocities. For 500 bucks. Lol :'-)
			# What we see here are either channel 3 or 2 NoteOn/NoteOff commands,
			# the factory settings, depending on the "bank selection".
			#   Channel 3 -> hold upper left  button for longer than 2s
			#   Channel 2 -> hold upper right button for longer than 2s
			#
			#    [[[146, 81, 127, 0], 47365]]
			#    [[[130, 81, 127, 0], 47443]]
			#    [[[146, 82, 127, 0], 47610]]
			#
			#    [[[ <NoteOn/Off>, <button>, 127, 0], 47610]]
			#
			#    146/145 -> NoteOn
			#    130/129 -> NoteOff
			#    127     -> fixed velocity (as set by the Midi Fighter utility )

			# Mhh, I guess it's about time to think about adding MIDI channels, isn't it?
			# But for now, we just check ch 2 and 3:
			if a[0][0][0] == 145 or a[0][0][0] == 146:
				return [ a[0][0][1], a[0][0][2] ]
			else:
				if a[0][0][0] == 130 or a[0][0][0] == 129:
					return [ a[0][0][1], 0 ]
				else:
					return []
		else:
			return []


	#-------------------------------------------------------------------------------------
	#-- Returns the raw value of the last button change (pressed/unpressed) as a list
	#-- [ <x>, <y>, <velocity> ], in which <x>/<y> are the coordinates of the grid and
	#-- <velocity> the state of the button.
	#--   >0 = button pressed; 0 = button released
	#-------------------------------------------------------------------------------------
	def ButtonStateXY( self ):
		if self.midi.ReadCheck():
			a = self.midi.ReadRaw()

			# whatever that is, does not belong here...
			if a[0][0][1] < 36 or a[0][0][1] > 99:
				return []

			x = (a[0][0][1] - 36) % 4
			if a[0][0][1] >= 68:
				x += 4
			y = 7 - ( (a[0][0][1] - 36) % 32 ) // 4

			if a[0][0][0] == 145 or a[0][0][0] == 146:
				return [ x, y, a[0][0][2] ]
			else:
				if a[0][0][0] == 130 or a[0][0][0] == 129:
					return [ x, y, 0 ]
				else:
					return []
		else:
			return []


	#-------------------------------------------------------------------------------------
	#-- Reset the Midi Fighter
	#-- Well, at least turn off all its LEDs
	#-------------------------------------------------------------------------------------
	def Reset( self ):
		# TODO
		# self.LedAllOn( 0 ) 
		pass



########################################################################################
### CLASS MidiFighter3D
###
### For Midi Fighter 3D Gedöns
########################################################################################
class MidiFighter3D( MidiFighter64 ):

	#         
	# LED AND BUTTON NUMBERS IN RAW MODE
	#
	#   Button codes depend on the selected bank,
	#   the bottom row with the small buttons.
	#
	#         +---+---+---+---+              +---+---+---+---+      
	#         | 39|   |   | 36|              | 55|   |   | 52|      
	#   +---+ +---+---+---+---+ +---+  +---+ +---+---+---+---+ +---+
	#   |   | | 43|   |   | 40| |   |  |   | | 59|   |   | 56| |   |
	#   |   | +---+---+---+---+ |   |  |   | +---+---+---+---+ |   |
	#   |   | | 47|   |   | 44| |   |  |   | | 63|   |   | 60| |   |
	#   +---+ +---+---+---+---+ +---+  +---+ +---+---+---+---+ +---+
	#         | 51|   |   | 48|              | 67|   |   | 64|      
	#         +---+---+---+---+              +---+---+---+---+      
	#         +---+---+---+---+              +---+---+---+---+      
	#         |   |   |   |###|              |   |   |###|   |      
	#         +---+---+---+---+              +---+---+---+---+      
	#
	#         +---+---+---+---+              +---+---+---+---+      
	#         | 71|   |   | 68|              | 87|   |   | 84|      
	#   +---+ +---+---+---+---+ +---+  +---+ +---+---+---+---+ +---+
	#   |   | | 75|   |   | 72| |   |  |   | | 91|   |   | 88| |   |
	#   |   | +---+---+---+---+ |   |  |   | +---+---+---+---+ |   |
	#   |   | | 79|   |   | 76| |   |  |   | | 95|   |   | 92| |   |
	#   +---+ +---+---+---+---+ +---+  +---+ +---+---+---+---+ +---+
	#         | 83|   |   | 80|              | 99|   |   | 96|      
	#         +---+---+---+---+              +---+---+---+---+      
	#         +---+---+---+---+              +---+---+---+---+      
	#         |   |###|   |   |              |###|   |   |   |      
	#         +---+---+---+---+              +---+---+---+---+      
	#
	#
	# LED AND BUTTON NUMBERS IN XY MODE (X/Y)
	#
	#              0   1   2   3
	#            +---+---+---+---+ 
	#   0        |   |1/0|   |   | 
	#      +---+ +---+---+---+---+ +---+
	#   1  |   | |   |   |   |   | |   |
	#      |   | +---+---+---+---+ |   |
	#   2  |   | |   |   |   |3/2 | |   |
	#      +---+ +---+---+---+---+ +---+
	#   3        |0/3|   |   |   | 
	#            +---+---+---+---+ 
	#            +---+---+---+---+ 
	#            |   |   |   |   | 
	#            +---+---+---+---+ 


	#-------------------------------------------------------------------------------------
	#-- Opens one of the attached Launchpad MIDI devices.
	#-- Uses search string "Fighter 3D", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "MidiFighter64" method
	def Open( self, number = 0, name = "Fighter 3D" ):
		return super( MidiFighter3D, self ).Open( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- Checks if a device exists, but does not open it.
	#-- Does not check whether a device is in use or other, strange things...
	#-- Uses search string "Fighter 3D", by default.
	#-------------------------------------------------------------------------------------
	# Overrides "MidiFighter64" method
	def Check( self, number = 0, name = "Fighter 3D" ):
		return super( MidiFighter3D, self ).Check( number = number, name = name )


	#-------------------------------------------------------------------------------------
	#-- Returns the raw value of the last button change (pressed/unpressed) as a list
	#-- [ <button>, <velocity> ], in which <button> is the raw number of the button and
	#-- <velocity> the button state.
	#--   >0 = button pressed; 0 = button released
	#-------------------------------------------------------------------------------------
	# Overrides "MidiFighter64" method
	def ButtonStateRaw( self ):
		if self.midi.ReadCheck():
			a = self.midi.ReadRaw()

			#    [[[ <NoteOn/Off>, <button>, 127, 0], 47610]]
			#
			#    146/147 -> NoteOn
			#    130/131 -> NoteOff
			#    127     -> fixed velocity (as set by the Midi Fighter utility )
			#
			#    Top arcade buttons on channel 3    -> 146 ON, 130 OFF
			#    Side and bank buttons on channel 4 -> 147 ON, 131 OFF

			if a[0][0][0] == 146 or a[0][0][0] == 147:
				return [ a[0][0][1], a[0][0][2] ]
			else:
				if a[0][0][0] == 130 or a[0][0][0] == 131:
					return [ a[0][0][1], 0 ]
				else:
					return []
		else:
			return []


	#-------------------------------------------------------------------------------------
	#-- Controls a grid LED by its <x>/<y> coordinates and a <color>.
	#--  <x>/<y>  0..3
	#--  <color>  0..127 from color table
	#-------------------------------------------------------------------------------------
	# overrides "MidiFighter64" method
	def LedCtrlXY( self, x, y, color, mode = None ):

		if x < 0 or x > 3:
			return
		if y < 0 or y > 3:
			return
		if color  < 0  or color  > 127:
			return

		number = 39 - x    # 36 - 4 + x
		number += 4 * y

		self.midi.RawWrite( 146, number, color )
		# set the mode if required; faster than calling LedCtrlRawMode()
		if mode is not None and mode > 17 and mode < 54:
			self.midi.RawWrite( 147, number - 3*12, mode )


