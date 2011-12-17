#import serialtty
import baudottty
import sys
import twitdriver
from time import sleep
import ConfigParser
import signal
#import pickle
import twitter

def mp( message ):
  print ''.join([ message, ' (' , str( len( message )), ')' ])

def term(number, frame):
   raise KeyboardInterrupt

def main():
  try:
    #install signal handlers so we exit nicely in case we get killed
    signal.signal(signal.SIGTERM, term)
    #signal.signal(signal.SIGKILL, term)
    #load parameters from config file
    config = ConfigParser.SafeConfigParser()
    configfile = open( 'twtty.cfg', 'rb' )
    config.readfp( configfile )
    configfile.close()

    serialport = config.get( 'Serial', 'port' )

    #username = config.get( 'Twitter', 'username' )
    #password = config.get( 'Twitter', 'password' )

    #access_file = open( "access.pickle", "r" )

    #access_token = pickle.load( access_file )

    debug = config.getboolean( 'General', 'debug' )

    since_id = int(config.get( 'Twitter', 'since_id' ))

    consumer_key = config.get( 'Twitter', 'consumer_key' )

    consumer_secret = config.get( 'Twitter', 'consumer_secret' )

    access_key = config.get( 'Twitter', 'access_key' )

    access_secret = config.get( 'Twitter', 'access_secret')

    
    tw = twitdriver.TwitDriver( consumer_key, consumer_secret, access_key, access_secret, since_id )
    print "blah"

    print ''.join( ["Opening serial port ", serialport] )

    tty = baudottty.BaudotTTY( serialport )
    print "Opened serial port"
    if(debug):
      tty.addlistener(mp)
      tw.addlistener(mp)

    #make the tty print received tweets
    tw.addlistener( tty.receive )
    #make twitter send messages typed on tty
    tty.addlistener( tw.receive )

    print "whut4"

    tw.start()
    tty.start()
      
    while(1):
      sleep(1)

  except KeyboardInterrupt, e:
    if debug:
      print "KeyboardInterrupt in main()"
    quit()

  except Exception, e:
    print 'Unexpected exception in twtty.py'
    print 'Cause: ', str( e )

  finally:
    #update the id of the most recent tweet we got
    #so we only load newer ones next time
    print "Saving configuration!"
    #yay, let's break abstraction
    print ''.join([ "since_id is ", str( tw.since_id ) ])
    config.set( 'Twitter', 'since_id', str( tw.since_id ) )
    configfile = open( 'twtty.cfg', 'w' )
    config.write( configfile )
    configfile.close()



if __name__ == "__main__":
  main()



