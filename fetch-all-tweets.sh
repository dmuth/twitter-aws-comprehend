#!/bin/bash
#
# Fetch all tweets for a user
#
# Recommended usage: ./fetch-all-tweets.sh user | ./csv-extract-tweets |pv -l > user.txt
#

# Errors are fatal
set -e

function printSyntax() {
	echo "! "
	echo "! Syntax: $0 username"
	echo "! "
	exit
}

if test ! "$1"
then
	printSyntax
fi

TWITTER_USER=$1

echo "# "
echo "# Fetching all recent tweets for user '$TWITTER_USER'..."
echo "# "

t timeline $TWITTER_USER --csv -n 5000

