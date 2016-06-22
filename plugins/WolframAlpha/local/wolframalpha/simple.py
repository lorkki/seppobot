#!/usr/bin/env python

'''A simple command-line interface to Wolfram Alpha'''

__author__ = 'aki.rossi@iki.fi'
__version__ = '1.1'

server	= "http://api.wolframalpha.com/v1/query.jsp"
appid	= "VHTYEJ-U395QYPT8T"

import logging
from functools import reduce
logging.basicConfig(filename="/home/aki/eggdrop/logs/wolframalpha.log", level=logging.DEBUG)

import wolframalpha.api as wapi
import random

notfound = ["Nothing.", "Nada.", "Zilch.", "No dice.", "Nice try but no cigar."]

def ask(text):
	wa = wapi.WolframAlpha(server, appid=appid)
	result = wa.query(text, format="plaintext", async="true")
	
	if result.success:
		print_result(result)
	elif result.errormessage:
		print("An error occurred:", result.errormessage.strip())
	elif result.error:
		print("An error occurred and nobody would tell me what it was.")
	else:
		print(random.choice(notfound))


def print_result(result):
	print(wrap(format_result(result), 400))

def format_result(result):
	out_tmp     = "[{0}] {1}"
	
	for pod in result.pods():
		if pod.id != "Input":
			title = pod.title
			text = pod.plaintexts()[0].strip().replace('\n', ' // ')
			return out_tmp.format(title.encode("utf8"), text.encode("utf8"))
	return ""

def wrap(text, width):
	"""
	A word-wrap function that preserves existing line breaks
	and most spaces in the text. Expects that existing line
	breaks are posix newlines (\n).
	"""
	return reduce(lambda line, word, width=width: '%s%s%s' %
				(line,
				' \n'[(len(line)-line.rfind('\n')-1
						+ len(word.split('\n',1)[0]
					) >= width)],
				word),
				text.split(' ')
				)

if __name__ == '__main__':
	import sys
	logging.debug("Command-line arguments: " + str(sys.argv))
	question = " ".join(sys.argv[1:])
	ask(question)
