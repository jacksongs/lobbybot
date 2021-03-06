import tweepy
import os

try:
	import variables
	auth = tweepy.OAuthHandler(variables.CONSUMER_KEY, variables.CONSUMER_SECRET)
	auth.set_access_token(variables.ACCESS_KEY, variables.ACCESS_SECRET)
except:
	ck = os.environ['MORPH_TWCKEY']
	cs = os.environ['MORPH_TWCSEC']
	ak = os.environ['MORPH_TWAKEY']
	ase = os.environ['MORPH_TWASEC']
	auth = tweepy.OAuthHandler(ck, cs)
	auth.set_access_token(ak, ase)

def this(x):
	api = tweepy.API(auth)
	try:
		api.update_status(x)
	except:
		api.update_status(x[:140])
