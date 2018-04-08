#!/usr/bin/env python3


import argparse
import datetime
import json
import logging as logger
import logging.config
import sys
import time
import webbrowser

import dateutil.parser
import twython

sys.path.append("lib")
import db
import db.tables.data
import db.tables.tweets


#
# Set up the logger
#
logging.config.fileConfig("logging_config.ini", disable_existing_loggers = True)

#
# Parse our arguments
#
parser = argparse.ArgumentParser(description = "Analyze crawled text")
parser.add_argument("-u", "--username", type = str, help = "Username whose tweets we will be fetching", required = True)
parser.add_argument("-n", "--num", type = int, help = "How many tweets to fetch?", default = 5)
parser.add_argument("--re-auth", action = "store_true", help = "Re-authenticate against Twitter")
args = parser.parse_args()

#
# Create our data object for writing to the data table.
#
sql = db.db()
data = db.tables.data.data(sql)
data_tweets = db.tables.tweets.data(sql)

#
# Fetch our data from the database.  If we don't have any data, then
# go through the process of getting auth tokens, which is a somewhat involved
# process which also includes opening up a web browser window. (ugh)
#
twitter_data = data.get("twitter_data")

if (not twitter_data or args.re_auth):

	print("# ")

	print("# ")

	if not twitter_data:
		print("# No Twitter credentials found!")

	if args.re_auth:
		query = "DELETE FROM data WHERE key = 'twitter_data'"
		sql.execute(query)
		print("# Deleting and re-adding Twitter credentials...")

	print("# ")
	print("# The first thing we're going to need to do is get your API Key and Secret")
	print("# You will be taken to Twitter's Apps page, and create an app if you need to.")
	print("# The app will only need read-only permissions.")
	print("# ")
	print("# ")

	url = "https://apps.twitter.com/"
	input("Press [Enter] to open %s in your web browser! [Enter] " % url)
	webbrowser.open(url)

	app_key = input("Enter your App Key here: ")
	app_secret = input("Enter your App Secret here: ")

	twitter = twython.Twython(app_key, app_secret)
	auth = twitter.get_authentication_tokens()

	auth_url = auth["auth_url"]
	logger.debug("Auth URL: " + auth_url)

	print("# ")
	print("# For the next step, we're going to open an authentication page on Twitter,")
	print("# which will display a PIN.  Please enter that PIN below!")
	print("# ")

	input("Press [Enter] to open the auth page in your web browser! [Enter] ")

	webbrowser.open(auth_url)
	oauth_verifier = input("Enter Your PIN: ")

	oauth_token = auth['oauth_token']
	oauth_token_secret = auth['oauth_token_secret']
	logger.debug("OAUTH Token: " + oauth_token)
	logger.debug("OAUTH Token Secret: " + oauth_token_secret)

	twitter = twython.Twython(app_key, app_secret, oauth_token, oauth_token_secret)

	try:
		final_step = twitter.get_authorized_tokens(oauth_verifier)

	except twython.exceptions.TwythonError as e:
		print ("! ")
		print ("! Caught twython.exceptions.TwythonError:", e)
		print ("! ")
		print ("! Did you enter the right PIN code?")
		print ("! ")
		exit(1)

	final_oauth_token = final_step['oauth_token']
	final_oauth_token_secret = final_step['oauth_token_secret']
	logger.debug("Final OUATH token: " + final_oauth_token)
	logger.debug("Final OAUTH token secret: " + final_oauth_token_secret)

	twitter_data = {
		"app_key": app_key,
		"app_secret": app_secret,
		"final_oauth_token": final_oauth_token,
		"final_oauth_token_secret": final_oauth_token_secret,
		"created": int(time.time()),
		}

	data.put("twitter_data", twitter_data)


#
# Fetch a number of tweets from Twitter.
#
# @param object twitter - Our Twitter oject
# @param integer count - How many tweets to fetch?
# @param kwarg max_id - The maximum Id of tweets so we can go back in time
#
# @return A dictionary that includes tweets that aren't RTs, the count, the last ID,
#	and how many tweets were skipped.
#
def getTweets(twitter, username, count, **kwargs):

	#retval = {"tweets": [], "count": 0, "skipped": 0, "last_id": -1}
	retval = {"tweets": [], "count": 0, "skipped": 0}
	logger.info("getTweets(): username=%s, count=%d, last_id=%d" % (username, count, kwargs["last_id"]))
	
	#
	# If we have a last ID, decrement it by one and query Twitter accordingly,
	# otherwise we start at the top of the timeline.
	#
	if ("last_id" in kwargs and kwargs["last_id"]):
		max_id = kwargs["last_id"] - 1
		tweets = twitter.get_user_timeline(
			screen_name = username, exclude_replies = True, include_rts = False, 
			count = count, max_id = max_id)

	else: 
		tweets = twitter.get_user_timeline(
			screen_name = username, exclude_replies = True, include_rts = False, 
			count = count)

	last_id = None
	timezone = time.strftime('%Z%z')

	for row in tweets:

		tweet_id = row["id"]
		tweet = row["text"]
		user = row["user"]["screen_name"]
		timestamp = int(dateutil.parser.parse(row["created_at"]).timestamp())
		date = datetime.datetime.fromtimestamp(timestamp)
		date_formatted = date.strftime("%Y-%m-%d %H:%M:%S")
		#
		# Grab the 400x400 version of the profile image
		#
		profile_image = row["user"]["profile_image_url_https"]
		profile_image = profile_image.replace("_normal", "_400x400")

		tweet = {
			"username": user,
			"date": date_formatted,
			"time_t": timestamp,
			"id": tweet_id, 
			"text": tweet, 
			"profile_image": profile_image
			}

		retval["tweets"].append(tweet)
		retval["count"] += 1
		retval["last_id"] = tweet_id;
		
	return(retval)

#
# Verify our Twitter credentials
#
twitter = twython.Twython(twitter_data["app_key"], twitter_data["app_secret"], twitter_data["final_oauth_token"], twitter_data["final_oauth_token_secret"])

creds = twitter.verify_credentials()
rate_limit = twitter.get_lastfunction_header('x-rate-limit-remaining')
logger.info("Rate limit left for verifying credentials: " + rate_limit)

screen_name = creds["screen_name"]
logger.info("My screen name is: " + screen_name)


print("# ")
print("# Fetching %d tweets for user '%s'!" % (args.num, args.username))
print("# ")

tweets = []
num_tweets_left = args.num
num_tweets_written = 0
last_id = False

num_passes_zero_tweets = 5
num_passes_zero_tweets_left = num_passes_zero_tweets


#
# Fetch tweets in a loop until we hit our max.
#
while True:

	result = getTweets(twitter, args.username, num_tweets_left, last_id = last_id)
	num_tweets_left -= result["count"]

	if result["count"] == 0:

		num_passes_zero_tweets_left -= 1
		logger.info("We got zero tweets this pass! passes_left=%d (Are we at the end of the timeline?)" % 
			num_passes_zero_tweets_left)

		if num_passes_zero_tweets_left == 0:
			logger.info("Number of zero passes left == 0. Yep, we're at the end of the timeline!")
			break

		continue

	#
	# We got some tweets, reset our zero tweets counter
	#
	num_passes_zero_tweets_left = num_passes_zero_tweets

	#logger.info("Tweets fetched=%d, skipped=%d, last_id=%d" % (result["count"], result["skipped"], result["last_id"]))
	logger.info("Tweets fetched=%d, skipped=%d, last_id=%s" % (result["count"], result["skipped"], result.get("last_id", None)))
	logger.info("Tweets left to fetch: %d" % num_tweets_left)
	rate_limit = twitter.get_lastfunction_header('x-rate-limit-remaining')
	logger.info("Rate limit left: " + rate_limit)

	if "last_id" in result:
		last_id = result["last_id"]

	for row in result["tweets"]:
		data_tweets.put(row["username"], row["date"], row["time_t"], row["id"], row["text"], row["profile_image"], "")
		num_tweets_written += 1

	if (num_tweets_left <= 0):
		break

	

logger.info("Total tweets written: %d" % num_tweets_written)



