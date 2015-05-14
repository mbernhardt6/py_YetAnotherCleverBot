#!/usr/local/bin/python2.7
#title           :YetAnotherCleverBot.py
#description     :Grab questions from Reddit comments and reply with CleverBot Response.
#author          :Yelly Von Hollerlots
#date            :20140603
#version         :0.6
#usage           :python YetAnotherCleverBot.py
#notes           :
#python_version  :2.7
#==============================================================================


#Import modules
import time
#import re
import praw
from cleverbot import Cleverbot
import logger
import filer

#Variables and Such
arrTouched = []
basepath = '/home/user/praw/'
fileTouched = basepath + 'snarkTouched.txt'
#Number of lines to keep in Touched file
lengthTouched = 1000
fileLog = basepath + 'yacb.log'
numPosts = 10
timeDelay = 60
colSubreddits = ['subreddit1','subreddit2','subreddit3']
cb = Cleverbot()

r = praw.Reddit('Yet Another Lame CleverBot Bot - v0.5')
r.login('username','password')

#Functions
def ValidComment(myComment):
  bolValidComment = True
  #Check for Valid Characters
  #if not(re.match("^[A-Za-z0-9_-]*$", myComment)):
  # bolValidComment = False
  #Check for Question
  if (myComment[-1] != '.'):
    bolValidComment = False
  #Check for Length
  if (len(myComment) > 50):
    bolValidComment = False
  return bolValidComment

def ValidReply(myComment):
  bolValidReply = True
  #Check for 'CleverBot' in Reply
  if ('CleverBot' in myComment):
    bolValidReply = False
  if ('clever' in myComment):
    bolValidReply = False
  return bolValidReply

def ReadTouched():
  myFile = open(fileTouched, 'r')
  for line in myFile:
    arrTouched.append(line.rstrip('\n'))
  myFile.close()

def WriteTouched():
  myFile = open(fileTouched, 'wb')
  for line in arrTouched:
    myFile.write(line + '\n')
  myFile.close()
  filer.tailFile(fileTouched, lengthTouched)
#/Functions

#Main
if __name__ == "__main__":
  logger.logMessage(fileLog, 'Reading state...')
  try:
    ReadTouched()
  except:
    logger.logMessage(fileLog, '  Oops! Unable to read file.')
  for Subreddit in colSubreddits:
    logger.logMessage(fileLog, 'Entering %s...' % Subreddit)
    thisSub = r.get_subreddit(Subreddit)
    hot = thisSub.get_hot(limit=numPosts)
    for thing in hot:
      if not(thing.id in arrTouched):
        logger.logMessage(fileLog, 'Post: %s' % thing.title)
        try:
          for redComment in thing.comments:
            try:
              strComment = redComment.body
              strComment = strComment.strip()
              logger.logMessage(fileLog, ' Question: %s' % strComment)
              if (ValidComment(strComment)):
                strAnswer = cb.ask(strComment)
                logger.logMessage(fileLog, ' Answer:   %s' % strAnswer)
                if (ValidReply(strAnswer)):
                  logger.logMessage(fileLog, '  Valid answer. Waiting %s seconds before posting.' % timeDelay)
                  time.sleep(timeDelay)
                  try:
                    redComment.reply(strAnswer)
                    arrTouched.append(thing.id)
                    logger.logMessage(fileLog, '  Success! Happy trolling!')
                  except:
                    logger.logMessage(fileLog, '  Oops! There was a problem posting the reply.')
                    break
                  break
                else:
                  logger.logMessage(fileLog, '  Not a valid answer.')
              else:
                logger.logMessage(fileLog, '  Not a valid comment.')
            except:
              logger.logMessage(fileLog, '  Oops! There was a problem with a comment.')
        except:
          logger.logMessage(fileLog, '  Oops! No comments found.')
  logger.logMessage(fileLog, 'Writing state...')
  WriteTouched()
