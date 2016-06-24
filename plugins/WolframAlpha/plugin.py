###
# Copyright (c) 2016, Aki Rossi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('WolframAlpha')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


import random
import urllib.request, urllib.parse

from xml.etree import ElementTree

def get_notfound_text():
    notfound = [
        "Nothing.",
        "Nada.",
        "Zilch.",
        "No dice.",
        "Nice try but no cigar."
    ]
    return random.choice(notfound)

def get_pod_text(pod):
    def _cleaned_texts(pod):
        for plaintext in pod.findall(".//plaintext"):
            if not plaintext.text:
                continue
            text = plaintext.text
            text = text.replace(" | ", ": ")
            text = text.replace("\n", "; ")
            yield text
    return ", ".join(_cleaned_texts(pod))

def get_input_text(tree, query_text=None):
    try:
        return get_pod_text(tree.find(".//pod[@id='Input']"))
    except:
        return query_text

class WolframAlpha(callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        self.__parent = super(WolframAlpha, self)
        self.__parent.__init__(irc)
        self.pods_iter = None
        self.input_text = None

    def _format_result(self, pod):
        title = pod.attrib["title"]
        result_text = get_pod_text(pod)

        if not result_text:
            return None

        return "[{}] {}: {}".format(self.input_text, title, result_text)

    def _print_next_result(self, irc):
        assert(self.pods_iter and self.input_text)

        for result in (self._format_result(pod) for pod in self.pods_iter):
            if result:
                irc.reply(result)
                break
        else:
            irc.reply("No more results.")

    def query(self, irc, msg, args, query_text):
        """<text>

        Starts a new Wolfram Alpha query.
        """
        apikey = self.registryValue('apikey')
        if not apikey:
            irc.error("No API key set.")
            return

        # Make the API call

        apiurl = "http://api.wolframalpha.com/v2/query"

        query = urllib.parse.urlencode({
            "input": query_text,
            "appid": apikey,
            "format": "plaintext",
            "parsetimeout": "10",
            "scantimeout": "15",
            "location": "Helsinki, Finland",
            "units": "metric"
        }).encode("ascii")

        with urllib.request.urlopen(apiurl, query, timeout=30) as request:
            result_data = request.read().decode("utf-8")

        # Process results

        tree = ElementTree.fromstring(result_data)

        if tree.attrib["success"] == "true":
            pods = (pod for pod in tree.iterfind(".//pod") if pod.attrib["id"] != "Input")

            self.input_text = get_input_text(tree, query_text)
            self.pods_iter = pods

            self._print_next_result(irc)
        elif tree.attrib["error"] == "true":
            for err in tree.findall(".//error//msg"):
                irc.reply("Error: " + err.text)
        else:
            notfound = get_notfound_text()
            dym = tree.find(".//didyoumean")
            if dym:
                irc.reply("{} Did you mean: {}".format(notfound, str(dym.text)))
            else:
                irc.reply(notfound)
    query = wrap(query, ["text"])

    def next(self, irc, msg, args):
        """takes no arguments

        Shows the next result from the latest Wolfram Alpha query.
        """
        if self.pods_iter:
            self._print_next_result(irc)
        else:
            irc.error("No active query.")
    next = wrap(next)


Class = WolframAlpha


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
