#
# This module is used for wrapping access to the "twitter" table.
#


import json
import sqlite3


class data():

	#
	# The table we're working with
	#
	table = "tweets"

	#
	# Our database object
	#
	db = ""


	def __init__(self, db):
		self.db = db
		#
		# Set the database to return associative arrays
		#
		self.db.conn.row_factory = sqlite3.Row

		schema = ("username TEXT NOT NULL, date TEXT NOT NULL, time_t INTEGER, "
			+ "tweet_id INTEGER UNIQUE NOT NULL, tweet TEXT NOT NULL, profile_image TEXT NOT NULL, "
			+ "sentiment TEXT NOT NULL, score TEXT NOT NULL")
		self.db.createTable(self.table, schema)



	#
	# Fetch the first (and only!) row for a specific tweet_id
	#
	def get(self, tweet_id):

		query = "SELECT rowid, * FROM %s WHERE tweet_id=?" % self.table
		results = self.db.execute(query, [tweet_id])

		for row in results:

			try:
				value = json.loads(row["value"])

			except Exception as e:
				value = row["value"]

			retval = {
				"rowid": row["rowid"],
				"tweet_id": row["tweet_id"],
				"value": value,
				}

			retval = value
			retval["rowid"] = row["rowid"]
			retval["tweet_id"] = row["tweet_id"]

			return(retval)


	#
	# Insert a value for a specific key.
	#
	def put(self, username, date, time_t, tweet_id, tweet, profile_image):

		#
		# Got the idea for this query from https://stackoverflow.com/a/4330694/196073
		#
		query = ("INSERT OR REPLACE INTO %s (username, date, time_t, tweet_id, tweet, profile_image, sentiment, score) "
			"VALUES (?, ?, ?, ?, ?, ?, "
			"COALESCE( (SELECT sentiment FROM tweets WHERE tweet_id = ?), ''), "
			"COALESCE( (SELECT score FROM tweets WHERE tweet_id = ?), '') "
			")" % self.table)

		self.db.execute(query, (username, date, time_t, tweet_id, tweet, profile_image, tweet_id, tweet_id))




