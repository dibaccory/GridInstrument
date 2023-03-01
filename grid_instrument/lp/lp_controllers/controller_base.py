from ..charset import *
from ..midi_handler import *
from pygame import midi
from pygame import time

########################################################################################
### CLASS controller_base - Launchpad base controller
###
########################################################################################
class controller_base( object ):

	def __init__( self ):
		try:
			self.midi   = Midi() # midi interface instance (singleton)
		except ImportError:
			sys.exit("error loading launchpad.py")
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

