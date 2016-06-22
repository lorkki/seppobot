
__author__ = 'aki.rossi@iki.fi'
__version__ = '1.0'

import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as etree
import logging

log = logging.getLogger("wolframalpha")

class WolframAlpha:
	def __init__(self, server='http://api.wolframalpha.com/v1/query.jsp', **attr):
		self.appid = attr.get("appid")
		self.server = server
		self.attr = attr
		
		log.debug("Engine created.")
		log.debug("Server URL: " + self.server)
		log.debug("Attributes: " + str(self.attr))
	
	def query(self, query, server=None, **userattr):
		log.debug("Starting a new query.")
		
		attr = {}
		attr.update(self.attr)
		attr.update(userattr)
		
		if not isinstance(query, Query):
			query = Query(query, **attr)
		
		log.debug("Query input: " + str(query.text))
		log.debug("Query attributes: " + str(query.attr))
		log.debug("Encoded query data: " + str(query.urlencode()))
		
		try:
			result = urllib.request.urlopen(self.server, query.urlencode())
			result = result.read()
		except urllib.error.URLError as err:
			log.error("URLError: " + str(err.reason))
			return None
		
		log.debug("XML data retrieved, building query result.")
		return QueryResult(result)

class Query:
	def __init__(self, text, **attr):
		self.text = text
		self.attr = attr
	
	def urlencode(self):
		params = {"input": self.text}
		for key, value in list(self.attr.items()):
			if isinstance(value, (list, tuple)):
				value = ",".join(value)
			params[key] = value
		return urllib.parse.urlencode(params).encode("ascii")
	
	def __str__(self):
		return self.urlencode()

class AsyncLoader:
	def __init__(self):
		self.cache = {}
	
	def load_xml(self, url):
		if url in self.cache:
			log.debug("Async: Returning cached copy of element: " + url)
			return self.cache.get(url)
		
		log.debug("Async: Loading element: " + url)
		
		result = urllib.request.urlopen(url)
		xmldata = result.read()
		self.cache[url] = xmldata
		
		return xmldata
	
	def load_element(self, url):
		element = etree.XML(self.load_xml(url))
		log.debug("Async: Successfully loaded an element of type '" + element.tag + "'.")
		
		return element

def _str_to_bool(text):
		text = text.strip().lower()
		if text in ["true", "1", "yes"]:
			return True
		elif text in ["false", "0", "no"]:
			return False
		else:
			return None

class QueryResult:
	def __init__(self, xmldata, async=False):
		self.xmldata = xmldata
		self.tree = etree.XML(xmldata)
		
		if self.tree.tag != "queryresult": raise AttributeError()
		
		self.asyncloader = AsyncLoader()
		
		self.version	= self.tree.get("version")
		self.success	= _str_to_bool(self.tree.get("success"))
		self.error	= _str_to_bool(self.tree.get("error"))
		self.timedout	= self.tree.get("timedout")
		self.numpods	= int(self.tree.get("numpods"))
		
		self.recalc_url = self.tree.get("recalculate")
		
		self.errormessage = self.tree.findtext("error")
		
		log.debug("Query result created.")
		log.debug("Attributes: " + str(self.tree.attrib))
	
	def recalculate(self):
		if self.recalc_url:
			xmldata = self.asyncloader.load_xml(self.recalc_url)
			return QueryResult(xmldata)
		return None
	
	def pods(self):
		for node in self.tree.findall("pod"):
			pod = Pod(node)
			if not pod.async:
				yield pod
			else:
				elem = self.asyncloader.load_element(pod.async)
				yield Pod(elem)
	
	def get(self, position):
		position = str(position)
		for pod in self.pods():
			if pod.position == position: 
				return pod
		return None
	
	def assumptions(self):
		assumptions = self.tree.find("assumptions")
		if assumptions:
			for node in assumptions.findall("assumption"):
				yield Assumption(node)

class Pod:
	"""A result pod for a Wolfram Alpha query.
	"""
	def __init__(self, element):
		self.element = element
		if self.element.tag != "pod": raise AttributeError()
		
		self.title	= self.element.get("title")
		self.id		= self.element.get("id")
		self.position	= self.element.get("position")
		self.numsubpods	= int(self.element.get("numsubpods"))
		self.async	= self.element.get("async")
		
		log.debug("Pod attributes: " + str(self.element.attrib))
	
	def subpods(self):
		for node in self.element.findall("subpod"):
			yield SubPod(node)
	
	def plaintexts(self):
		return [subpod.plaintext() for subpod in self.subpods()]
	
	def images(self):
		result = []
		for subpod in self.subpods(): 
			result += subpod.images()
		return result
	
	def __str__(self):
		return self.title

class SubPod:
	def __init__(self, element):
		self.element = element
		if self.element.tag != "subpod": raise AttributeError()
		self.title = self.element.get("title")
	
	def plaintext(self):
		return self.element.findtext("plaintext")
	
	def images(self):
		return self.element.findall("img")
	
class Assumption:
	def __init__(self, element):
		self.element = element
		if self.element.tag != "assumption": raise AttributeError()
		
		self.type = self.element.get("type")
		self.word = self.element.get("word")
		self.used = self.element.find("value")
		self.alternatives = self.element.findall("value")[1:]
	
	def __str__(self):
		out = ""
		if self.word:
			out += self.word + ": "
		out += self.used.get("desc")
		return out

	

