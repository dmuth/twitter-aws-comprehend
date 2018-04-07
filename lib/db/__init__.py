#
# This class is used as our database wrapper.
#

import sqlite3


class db():

	conn = ""

	def __init__(self):
		self.conn = sqlite3.connect("posts.db")

		# Autocommit
		self.conn.isolation_level = None


	def execute(self, query, args = None):

		if (args):	
			retval = self.conn.execute(query, args)

		else:
			retval = self.conn.execute(query)

		return(retval)


	#
	# Wrapper to create a table if it does not exist
	#
	# @param string table The name of the table to create
	# @param string settings A string with the schema for the table.
	#
	def createTable(self, table, settings):

		#
		# Query to see if the table already exists.  If it does, stop.
		#
		query = "SELECT name from sqlite_master WHERE name = '%s'" % table
		results = self.conn.execute(query)
		for row in results:
			return True

		#
		# Table doesn't exist?  Go forth and create it!
		#
		query = ("CREATE TABLE %s (%s)" % (table, settings))
		self.conn.execute(query)



