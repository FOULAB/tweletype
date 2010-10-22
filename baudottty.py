import serial
import textwrap
import driver
import threading
from curses.ascii import isprint
import time
import baudot

class BaudotTTY( driver.Driver ):
  def __init__( self, _port=0, columns=60, maxbuf = 140 ):
    self._maxbuf = maxbuf
    self._columns = columns
    #open tty in nonblocking mode because other threads need access to it too
    self.tty=baudot.baudot( _port )
    driver.Driver.__init__( self )
    self.ttylock = threading.Lock()
    self.clearbuffer()
    self.ttylock.acquire()
    self.tty.write('\r\n')
    self.ttylock.release()
    self.linepos = 0

  #receive a message from another class and print it to the tty.
  def receive( self, message ):
    #wrap text to 60 columns, add both CR and LF, and send to tty
    self.ttylock.acquire()
    self.tty.write( '\r\n'.join( textwrap.wrap( message, self._columns ) ) )
    self.tty.write('\r\n')
    self.ttylock.release()

  #listen for input on the terminal and send it when return is pressed.
  def run( self ):
    print ''.join(["Listening for input on ", self.tty.ser.port, " in new thread."])
    while(1):
      self.ttylock.acquire()
      #wait for a single character
      char = self.tty.read()
      #if no input, just wait
      if( char == '' ):
        pass
      # if user hit ctrl-c, erase buffer
      elif( char == '\x03'):
        self.clearbuffer()
        self.tty.write('\r\n')
        self.linepos = 0
      #if user hit enter, send message
      elif( char == '\r' ):
        self.tty.write('\r\n')
        self.notify( self.textbuffer )
        self.clearbuffer()
        self.linepos = 0
        
      #if buffer is full, beep
      elif( self._maxbuf > 0 and len( self.textbuffer ) >= self._maxbuf ):
        self.tty.write('\x07')
      #if character is printable and buffer not full, echo it and add to buffer
      elif( isprint( char ) ):
        self.textbuffer = ''.join( [ self.textbuffer, char ] )
        self.tty.write( char )
        self.linepos += 1
        # Wrap input lines if they are greater than
        # 60 columns. This wan't necessary on the TI-745
        # because it would wrap automatically
        if self.linepos > self._columns:
          self.tty.write( '\r\n' )
          self.linepos = 0

      self.ttylock.release()
      time.sleep(0.01)



  def clearbuffer( self ):
    self.textbuffer = ''
  


