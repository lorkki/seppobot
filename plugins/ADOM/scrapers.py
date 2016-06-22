
import re
import html.parser
import supybot.utils as utils

def joke(text):
	match = re.search("<td class='no'>.+?</h2>(.+?)</td>", text, re.I | re.S)
	if match:
		s = match.group(1)
		lines = re.split(r'<(?:p|li)>(.+?)</(?:p|li)>', s)
		
		for l in lines:
			l = re.sub(r'<.+?>', '', l).replace("\n", " ").strip()
			if l: 
				yield l
joke.url = "http://www.rinkworks.com/jokes/random.cgi"

def limerick(text):
	match = re.search("<div class=.quote_output.>(.+?)</div>", text, re.I | re.S)
	if match:
		s = match.group(1)
		
		lines = s.split('<br />')
		
		for l in lines:
			l = l.strip()
			if l:
				yield l
limerick.url = "http://limerickdb.com/?random2"

def schneier(text):
	match = re.search("<p class=.fact.>(.+?)</p>", text, re.I | re.S)
	if match:
		h = html.parser.HTMLParser()
		s = match.group(1).strip()
		yield h.unescape(s)
schneier.url = "http://www.schneierfacts.com/"

def lorkki(text):
	match = re.search("<p class=.fact.>(.+?)</p>", text, re.I | re.S)
	if match:
		h = html.parser.HTMLParser()
		s = match.group(1).strip().replace("Bruce Schneier", "Lorkki")
		yield h.unescape(s)
lorkki.url = "http://www.schneierfacts.com/"

def scrape(irc, op, url=None, plugin=None, prefixnick=False):
	"""Generic screen scraper.
	"""
	if not url: 
		url = op.url
	try:
		text = utils.web.getUrl(url).decode("utf-8")
		for line in op(text):
			irc.reply(line, prefixNick=prefixnick)
	except utils.web.Error as e:
		if plugin: plugin.log.info("Couldn't scrape url %u: %s.", url, e)
		irc.reply("The Internet is on fire.")
