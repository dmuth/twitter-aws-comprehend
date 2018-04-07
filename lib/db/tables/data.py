#
# This module is used for wrapping access to the "data" table.
#


import json
import sqlite3


class data():

	#
	# The table we're working with
	#
	table = "data"

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

		#
		# If the table is found, stop.  Otherwise, create it.
		#
		query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.table
		results = self.db.execute(query)
		for row in results:
			return(None)

		query = "CREATE TABLE %s (key TEXT NOT NULL, value TEXT NOT NULL)" % self.table
		self.db.execute(query)



	#
	# Fetch the first (and only!) row for a specific key.
	#
	def get(self, key):

		query = "SELECT rowid, * FROM %s WHERE key=?" % self.table
		results = self.db.execute(query, [key])

		for row in results:

			try:
				value = json.loads(row["value"])

			except Exception as e:
				value = row["value"]

			retval = {
				"rowid": row["rowid"],
				"key": row["key"],
				"value": value,
				}

			retval = value
			retval["rowid"] = row["rowid"]
			retval["key"] = row["key"]

			return(retval)


	#
	# Insert a value for a specific key.
	#
	def put(self, key, value):
		query = "INSERT OR REPLACE INTO %s (key, value) VALUES (?, ?)" % self.table
		value = json.dumps(value)
		self.db.execute(query, (key, value))


