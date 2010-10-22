#import twitter
import threading
import driver
from time import gmtime, strftime, sleep, strptime
from datetime import datetime, timedelta
from urllib2 import URLError
from httplib import HTTPException 
import unicodedata
import re
from htmlentitydefs import name2codepoint
import pickle
import oauthtwitter

class TwitDriver(driver.Driver):
  #paramters:
  # login: twitter username
  # password: twitter password
  # since_id: only get tweets newer than the one with this ID
  def __init__( self, consumer_key, consumer_secret, access_token, since_id='' ):
    driver.Driver.__init__( self )
    
    self.api = oauthtwitter.OAuthApi( consumer_key, consumer_secret , access_token)
    print self.api
    self.twuser = self.api.GetUserInfo().screen_name
    print self.twuser
    self.twtlock = threading.Lock()
    print self.twtlock
    self.since_id = since_id
    print self.since_id


  #watch for tweets from server
  def run( self ):
  
    while 1:
      try:
        self.twtlock.acquire()
        newreplies = self.api.GetReplies(since_id=self.since_id)
        newtweets = self.api.GetFriendsTimeline(since_id=self.since_id, count=200)
        self.twtlock.release()
        #tweets are listed newest to oldest, but we want the most recent tweets
        #printed first, so we reverse the list.
        newtweets.reverse()
        newreplies.reverse()
        #remove duplicate replies
        for t in newtweets:
          for r in newreplies:
            if t.id == r.id:
              newreplies.remove(r)
        #merge the lists of replies and other tweets
        #basically it's the merge out of merge sort
        i, j = 0,0
        result = []
        while ( i < len( newtweets ) and j < len ( newreplies ) ):
          if ( newtweets[i].id <= newreplies[j].id ):
            result.append( newtweets[i] )
            i = i + 1
          else:
            result.append( newreplies[j] )
            j = j + 1
        result += newtweets[i:]
        result += newreplies[j:]
                            
        print ''.join([str(len(newtweets)), ' new tweets, ', str(len( newreplies ) ) , " new replies." ])
        #next time we update, only get new tweets since last one in the list
        if len(result) > 0:
          self.since_id = result[-1].id
        for tweet in result:
          fr = tweet.user.screen_name
          if fr == self.twuser:
            print "Tweet from my own user, not forwarding"
            continue
          body = remove_accents( ''.join( [ '(', tweet.created_at, ') ', fr, ': ', tweet.text] ) )
          self.notify( body )
          
      #exception code from http://www.voidspace.org.uk/python/articles/urllib2.shtml#httperror
      except URLError, e:
        if hasattr(e, 'reason'):
          print 'We failed to reach a server.'
          print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
          print 'The server couldn\'t fulfill the request.'
          print 'Error code: ', e.code
      except HTTPException, e:
        print 'HTTP Exception:'
        print 'Cause: ', str(e)
      except ValueError, e:
        print 'Badly formed data!'
        print 'Cause: ', str(e)
      except Exception, e:
        print 'Unexpected Exception in twitdriver!'
        print 'Cause: ', str(e)
      finally:
        if self.twtlock.locked():
          self.twtlock.release()
      #sleep outside the finally block so any uncaught exceptions get
      #rethrown right away
      sleep(10)


  #send out a message via twitter
  def receive( self, message ):
    try:
      self.twtlock.acquire()
      self.api.PostUpdate(message)
      self.twtlock.release()
    #exception code from http://www.voidspace.org.uk/python/articles/urllib2.shtml#httperror
    except URLError, e:
      if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
      elif hasattr(e, 'code'):
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    except Exception, e:
      print 'Unexpected exception in twitdriver.receive!'
      print 'Cause: ', str( e )
    finally:
      if self.twtlock.locked():
        self.twtlock.release()

#utility function to unescape html entities, strip unicode characters and convert to latin where possible
# from http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

def remove_accents(str):
  str = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), str)
  nkfd_form = unicodedata.normalize('NFKD', unicode(str))
  only_ascii = nkfd_form.encode('ASCII', 'ignore')
  return only_ascii
