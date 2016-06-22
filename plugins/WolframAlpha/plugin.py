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

import random

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from .local.wolframalpha import api as wapi

server	= "http://api.wolframalpha.com/v1/query.jsp"
appid	= "VHTYEJ-U395QYPT8T"

notfound = ["Nothing.", "Nada.", "Zilch.", "No dice.", "Nice try but no cigar."]

class WolframAlpha(callbacks.Plugin):
	"""Add the help for "@plugin help WolframAlpha" here
	This should describe *how* to use this plugin."""
	threaded = True
	
	def __init__(self, irc):
		self.__parent = super(WolframAlpha, self)
		self.__parent.__init__(irc)
		self.pod_iter = None
	
	def _format_pod(self, pod):
		out_fmt = "[{0}] {1}"
		title = pod.title
		text = pod.plaintexts()[0].strip().replace('\n', ' // ')
		if not text and pod.images():
			text = "(contains image)"
		return out_fmt.format(title, text)
	
	def _first_pod(self, result):
		if result.success and result.numpods > 0:
			pod_iter = result.pods()
			for pod in pod_iter:
				if pod.id != "Input":
					self.pod_iter = pod_iter
					return self._format_pod(pod)
		return None
	
	def _next_pod(self):
		if self.pod_iter:
			for pod in self.pod_iter:
				return self._format_pod(pod)
			self.pod_iter = None
		return None
	
	def query(self, irc, msg, args, text):
		"""<text>
		
		Performs a query in Wolfram|Alpha and returns the first result pod.
		"""
		self.log.debug("Performing query '%s'." % (text))
		w = wapi.WolframAlpha(server, appid=appid)
		result = w.query(text, format="image,plaintext", async="true")
		out = ""
		if result.success:
			if result.numpods < 1:
				self.log.debug("Success but no pods; recalculating result.")
				result = result.recalculate()
			out = self._first_pod(result)
		elif result.errormessage:
			irc.error(result.errormessage.strip())
		elif result.error:
			irc.error("An error occurred and nobody would tell me what it was.")
		
		if out:
			irc.reply(out)
		else:
			irc.reply(random.choice(notfound))
	query = wrap(query, ["text"])
	
	def next(self, irc, msg, args):
		"""takes no arguments
			
		Shows the next result pod from the last Wolfram|Alpha query.
		"""
		if self.pod_iter:
			out = self._next_pod()
			if out:
				irc.reply(out)
			else:
				irc.reply("No more results.")
		else:
			irc.error("No active query found.")
	next = wrap(next)

Class = WolframAlpha

