import threading

class Driver( threading.Thread ):
  def __init__( self ):
    threading.Thread.__init__(self)
    self.listeners = []

  def addlistener( self, listener ):    #Accept a bound function to notify when a message arrives
    self.listeners.append( listener )
  
  def notify( self, message ):          #Notify all listeners of new message
    for l in self.listeners:
      l( message )

  def run( self ):                   #start listening for events
    pass                                #override in subclass to wait for and act on messages

  def receive( self, message ):         # receive a message from another Driver
    pass                                #override in subclass to output received messages
