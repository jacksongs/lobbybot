import tweepy
import variables
import os
import os.path

if os.path.isfile('variables.py') == True:
	auth = tweepy.OAuthHandler(variables.CONSUMER_KEY, variables.CONSUMER_SECRET)
	auth.set_access_token(variables.ACCESS_KEY, variables.ACCESS_SECRET)
else:
	ck = os.environ['CONSUMER_KEY']
	cs = os.environ['CONSUMER_SECRET']
	ak = os.environ['ACCESS_KEY']
	ase = os.environ['ACCESS_SECRET']
	auth = tweepy.OAuthHandler(ck, cs)
	auth.set_access_token(ak, ase)

def this(x):
	api = tweepy.API(auth)
	try:
		api.update_status(x)
	except:
		api.update_status(x[:140])
