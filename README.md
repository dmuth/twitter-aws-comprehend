
NOTE: If you like this, you'll also like <a href="https://github.com/dmuth/twitter-sentiment-analysis">my next project</a>, which performs sentiment analysis on Tweets by keyword!


# Twitter AWS Comprehend

I recently learned of <a href="https://aws.amazon.com/comprehend/">Amazon Comprehend</a> and wanted
to play around with its sentiment analysis.

So I built this app to download user timelines from Twitter, send them to AWS for analysis, and visualize them in Splunk.  The following metrics are reported:

- Start and end dates for tweets
- Number of tweets
- A graph of "Sentiment Over Time"
- Number of F-bombs used
- Net Happiness Index (percent of happy tweets minus precent of unhappy tweets)
- Top Positive and Negative tweets


## Screenshots

<a href="./img/splunk-twitter-sentiment-dashboard.png"><img src="./img/splunk-twitter-sentiment-dashboard.png" width="275" /></a> <a href="./img/obama-twitter-sentiment-dashboard.png"><img src="./img/obama-twitter-sentiment-dashboard.png" width="275" /></a>  <a href="./img/phillies-twitter-sentiment-dashboard.png"><img src="./img/phillies-twitter-sentiment-dashboard.png" width="275" /></a>

Additional screenshots <a href="img">are available in the img/ directory</a>.


## Requirements

- An AWS Account
- The <a href="https://docs.aws.amazon.com/cli/latest/userguide/installing.html">AWS Command Line Interface installed and configured</a>
- Python 3
- Run the command `pip install -r requirements.txt` to download all required packages
- A Twitter app created at <a href="https://apps.twitter.com/">https://apps.twitter.com/</a>.  Read-only access is fine.
- A running Splunk Instance.  A free copy of Splunk can be downlaoded from <a href="https://www.splunk.com/">Splunk.com</a>.


## Getting started

### Downloading Tweets

You'll want to start off by running the script **./0-fetch-tweets -u username -n num_tweets_to_download** to download Tweets via Twitter's API.
When you first run the script, it will notice the lack of credentials and send you over to Twitter's App page,
where you'll need to create an app.  Then grab the App Key and App Secret and enter them when the script prompts you.
Next, you'll be sent over to Twitter one more time and will receive a PIN to enter in the script.  Do so,
and you'll be authenticated to Twitter.  **This is a one-time process**, so once you do it, you should not need
to do it again.

The maximum number of tweets you can download from Twitter's API is **3200**, but the actual number you get will
be much lower as RTs are ignored and Twitter's API is really weird about giving you the actual number of tweets that you ask for.  I do not understand it.


### Analyizing Tweets

WARNING: **This costs money!**  Based on <a href="https://aws.amazon.com/comprehend/pricing/">AWS's pricing structure</a>, a tweet will be treated as 3 "units", which will cost you $.0003, or 3 hundredths of a cent to analyze.  So 100 tweets will cost 3 cents, while 1,000 tweets will cost 30 cents.

The syntax for the script to analyize sentment is **1-analyze-sentiment -u username -n num_tweets [ --fake ]**

I strongly encourage you to run the script with **--fake** on the first few tries so that you can fake calls to AWS and get comfortable running the script.


### Feeding the analyzed tweets to Splunk

The syntax for the script to feed the tweets into Splunk is: **2-ingest-into-splunk -u username [ --splunk-port port ] [ --splunk-host hostname ]**  Defaults are 9997 and localhost, respectively.

The data is sent to Splunk over a raw TCP connection, so you'll want to configure Splunk accordingly.  Here's a screenshot to help with that:

<img src="./img/splunk-tcp-port.png" />

You'll want to have this source saving to the **main** Index.


## Visualization 

This is the most interesting part.  So far, we are making the following assumptions about Splunk:
- Use of the **main** Index
- Use of the Sourcetype **twitter**
- Use of the Splunk app **Search**

Assuming those are the case, you're good to go!  Just copy the file **splunk/twitter_activity_sentiment.xml** into **$SPLUNK_HOME/etc/apps/search/local/data/ui/views**, restart Splunk, and you should be all set!  

Alternatively, a less convoluted way (which does not require restarting Splunk) would be to create a new dashboard, click **Edit**, click **Source**, and paste in the contents of **twitter_activity_sentiment.xml**.


## A Word on Idempotency

I am a HUGE fan <a href="https://en.wikipedia.org/wiki/Idempotence">of Idempotency</a>.  Especially because
AWS Comprehend costs money!  Once I analyze a tweet, I never want to analyze it again.  So I made a conscious
choice to build my code that way.  So, for example, if a tweet is analyzed and later the script **0-fetch-tweets** is 
run, that code will not overwrite the sentiement fields.  And once a tweet is analyzed by **1-analyze-sentiemtn**, it will never be analyzed again!

One place where this does break down is with Slplunk, since the data is fed in through raw TCP and Splunk does not seem to give any acknowledgement (don't know why...), running that script twice will result in duplicate events.  The way around that is to run a Splunk query like **index=main sourcetype=twitter username=dmuth | delete** before re-ingesting any data.  I'm not thrilled with this particular workflow, and am looking at some alternatives.  


## Future TODO Items

- ~~Make tweet ingestion idempotent~~
- ~~See about using Twitter's search API to get older tweets~~ Seriously, Twitter.  Let us get more than 3,200 Tweets through your API!
- Come up with a metric to measure profanity on an account, not just f-bombs
- Add "username" field to the database schema so we can analyze multiple users at once
- Dockerize this to download a user's tweets, analyzes them, exports them, then loads up a Splunk instance to ingest them


## Contact

I had fun writing this, and I hope you had enjoy using this.  If there are any issues, feel
free to file an issue against this project, <a href="http://twitter.com/dmuth">hit me up on Twitter</a>
<a href="http://facebook.com/dmuth">or Facebook</a>, or drop me a line: **dmuth AT dmuth DOT org**.




