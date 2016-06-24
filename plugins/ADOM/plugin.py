###
# Copyright (c) 2011, Aki Rossi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#	 this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#	 this list of conditions, and the following disclaimer in the
#	 documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#	 contributors to this software may be used to endorse or promote products
#	 derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import re, random, math, fractions

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from . import scrapers
from .scrapers import scrape
from . import randpc, genre, speare

class ADOM(callbacks.Plugin):
	"""Add the help for "@plugin help ADOM" here
	This should describe *how* to use this plugin."""
	threaded = True
	
	def joke(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Tells a bad joke (from Rinkworks).
		"""
		scrape(irc, scrapers.joke, plugin=self)
	joke = wrap(joke, [optional("text")])
	
	def schneier(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Tells a Bruce Schneier fact.
		"""
		scrape(irc, scrapers.schneier, plugin=self)
	schneier = wrap(schneier, [optional("text")])

	def spock(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Tells a Spock quote.
		"""
		def get_quote():
			with open("/home/seppo/supybot/plugins/ADOM/spockquote.txt") as f:
				return random.choice(f.readlines()).strip()
		irc.reply(get_quote())
	spock = wrap(spock, [optional("text")])
	
	def randpc(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Generates a random player character choice for ADOM.
		"""
		irc.reply(randpc.randpc())
	randpc = wrap(randpc, [optional("text")])
	
	def lepo(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Assigns the user a length of sleep time, and tells whether it's
		a prime.
		"""
		n = random.randint(0,65535)
		irc.reply("%s.sleep(%i)" % (msg.nick, n), notice=True, prefixNick=False)
		
		f = factor(n)
		if len(f) > 1:
			out = "Not a prime: %s = %i" % ("*".join([str(x) for x in f]), n)
			irc.reply(out, notice=True, prefixNick=False)
		else:
			irc.reply("%i is a prime." % (n), notice=True, prefixNick=False)
	lepo = wrap(lepo, [optional("text")])
	
	def arvo(self, irc, msg, args, items):
		"""<item1>[[,] <item2>[[,] <item3> ...]]
		
		Picks a random item out of a list. Items may contain spaces
		if the list is comma-separated.
		"""
		s = " ".join(items)
		if "," in s:
			self.log.debug("Resplitting item list.")
			items = s.split(",")
		irc.reply(random.choice(items).strip())
	arvo = wrap(arvo, [many("anything")])
	
	def genre(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Generates a random music genre.
		"""
		irc.reply(genre.make_genre())
	genre = wrap(genre, [optional("text")])
	
	def speare(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Generates a random shakespearian insult.
		"""
		irc.reply("Thou " + speare.get_insult() + "!")
	speare = wrap(speare, [optional("text")])

	def joik(self, irc, msg, args, text=""):
		"""takes no arguments
		
		Tells a bad joke (from Rinkworks).
		"""
		irc.reply(get_joik())
	joik = wrap(joik, [optional("text")])

Class = ADOM


def factor(n):
	if n < 2:
		return []
	for i in range(2, int(math.ceil(math.sqrt(n))+1)):
		if n % i == 0:
			return [i] + factor(n // i)
	return [n]

def get_joik(minlength=60, maxlength=80, charset="aeiouy"):
	out = ""
	while len(out) < minlength:
		out += random.choice(charset) * random.randint(1, min(10, maxlength-len(out)))
	return out
