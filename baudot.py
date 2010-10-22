import serial
import subprocess
import string
import sys
import fcntl
import os

class baudot:

  # baudot letters. the baudot binary value is the index into this string.
  # eg. the letter E, baudot code 0x01, is the second character in the string.
  aLtrs = "\x00E\x0AA SIU\x0DDRJNFCKTZLWHYPQOBG\x0EMXV\x0F"
  # same but for figures
  aFigs = "\x003\x0A- \x0787\x0D$4',!:(5\")2#6019?&\x0E./;\x0F"
  FIGS = "\x1B"
  LTRS = "\x1F"
  txmode = LTRS
  rxmode = LTRS

  # Set up the serial port
  def __init__( self, port ):
    self.ser = serial.Serial(port=port, timeout=0.01)
    portDev = self.ser.portstr

    # Set a custom baud rate
    # This means that when we ask for the rate 38400 bps,
    # we actually get the rate 45 bps.
    # see man setserial for more info
    speedSuccess = subprocess.call( [ "setserial", portDev, "spd_cust", "divisor", "2560" ] )

    if( speedSuccess != 0 ):
      raise Exception( "Could not set serial port speed!" )

    self.ser.setBaudrate( 38400 )
    # No parity, 2 stop bits, 5 data bits
    # Baudot is *actually* 1.5 stopbits but this is
    # close enough for science
    self.ser.setParity( 'N' )
    self.ser.setStopbits( 2 )
    self.ser.setByteSize( 5 )

    self.ser.open()
    self.ser.write( self.txmode )

  # Take an ascii string and return Baudot equivalent.
  def a2b( self, aString ):
    result = []
    
    for ch in string.upper( aString ):
      # find out if the current character is a letter or a figure
      bl = self.aLtrs.find( ch )
      bf = self.aFigs.find( ch )
      # if we're in letter mode, and it's a letter, return the letter code
      # otherwise switch to figs and return the fig code
      if self.txmode == self.LTRS:
        if bl >= 0:
          result.append( chr( bl ) )
        elif bf >= 0:
          self.txmode = self.FIGS
          result.append( self.FIGS )
          result.append( chr( bf ) )
      # if we're in figs mode, do like above but backwards
      elif self.txmode == self.FIGS:
        if  bf >= 0:
          result.append( chr( bf ) )
        elif bl >= 0:
          self.txmode = self.LTRS
          result.append( self.LTRS )
          result.append ( chr( bl ) )
      
    return ( ''.join( result ) )

  # Take a baudot string and return the ASCII equivalent.
  def b2a( self, bString ):
    result = []

    for b in bString:
      if b == self.LTRS:
        self.rxmode = self.LTRS
      elif b == self.FIGS:
        self.rxmode = self.FIGS
      elif self.rxmode == self.LTRS:
        result.append( self.aLtrs[ ord( b ) ] )
      elif self.rxmode == self.FIGS:
        result.append( self.aFigs[ ord( b ) ] )


    return( ''.join( result ) )
  
  def read( self ):
    b = self.ser.read()
    if( b == '' ):
      return ''
    else:
      return( self.b2a( b ) ) 

  def write( self, string ):
    self.ser.write( self.a2b( string ) )

# If this module is called from the command line as a script,
# enter mini chat mode.
if __name__ == "__main__":

  #Nonportable code to make stdin nonblocking. only works on unix.
  fd = sys.stdin.fileno()
  fl = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)


  # Loop and read a byte from tty and send to screen, and vice verse
  b = baudot( 0 )
  while 1:
    bc = b.ser.read()
    if bc != '':
      sys.stdout.write( b.b2a( bc ) )
    try:
      ac = sys.stdin.read(1)
      if ac == "\n":
        b.ser.write( b.a2b( "\r" ) )
      b.ser.write( b.a2b( ac ) )
    except IOError:
      pass





