#!/bin/bash
#
# Fetch all tweets for a user
#
# Recommended usage: ./fetch-all-tweets.sh user | ./csv-extract-tweets |pv -l > user.txt
#

# Errors are fatal
set -e

function printSyntax() {
	echo "! " >&2
	echo "! Syntax: $0 username" >&2
	echo "! " >&2
	exit
}

if test ! "$1"
then
	printSyntax
fi

TWITTER_USER=$1

echo "# " >&2
echo "# Fetching all recent tweets for user '$TWITTER_USER'..." >&2
echo "# " >&2

t timeline $TWITTER_USER --csv -n 5000

