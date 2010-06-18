#!/usr/bin/env python
# encoding: utf-8
"""
action.py

Created by Balfanz, Ryan on 2010-05-25.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import logging
import sys
import unittest

LEVELS = {'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL}
# level_name = sys.argv[1]
level = LEVELS.get('debug', logging.NOTSET)
logging.basicConfig(level=level)

class ActorError(Exception):
	"""Base class for Actor exceptions."""
	def __init__(self, msg):
		super(ActorError, self).__init__(msg)
		self.msg = msg
		
		
class ParseError(ActorError):
	"""docstring for ParseError"""
	def __init__(self, msg):
		super(ParseError, self).__init__(msg)
		self.msg = msg
		
		
class Actor:
	"""An Actor translates a script into something useful by acting on it."""
	def __init__(self):
		self._header = ''
		self._paramMap = None
		self._paramSql = ''
		
	@property
	def header(self):
		"""Return the header."""
		return self._header
		
	def _parse_header(self, header):
		"""docstring for parse_header"""
		import yaml
		sqlMapping = yaml.load(header)
		return sqlMapping
		
	def _parse(self, script):
		"""docstring for parse"""
		inHeader = False
		params = {}
		paramSql = ""
		headerLines = []
		sqlLines = []
		for i, line in enumerate(script):
			if inHeader:
				if line.startswith('*/'):
					try:
						self._header = ''.join(headerLines)
						params = self._parse_header(self._header)['parameters']
					except KeyError:
						pass
					inHeader = False
					continue
				else:
					headerLines.append(line)
				continue
			elif line.startswith('/*'):
				inHeader = True
				continue
			else:
				sqlLines.append(line)
		
		self._paramMap = dict([(p["name"], p["default"]) for p in params])
		self._paramSql = ''.join(sqlLines)
		return True
		
	def act(self, script, *args, **kwargs):
		"""docstring for act"""
		if not self._parse(script):
			raise ParseError("Count not parse script {scriptFile}".format(scriptFile=script))
			
		paramSubs = self._paramMap
		if not paramSubs:
			return self._paramSql
			
		for k, v in kwargs.iteritems():
			try:
				paramSubs[k] = v
			except KeyError:
				raise
				
		return self._paramSql.format(**paramSubs)
		
		
class ActorTests(unittest.TestCase):
	def setUp(self):
		self._actor = Actor()
		self._scriptDir = "../test/scripts/"
		self._scriptExt = "sql"
		
	def test_scripts(self):
		"""docstring for test_scripts"""
		import glob
		actor = self._actor
		for script in glob.glob(self._scriptDir + "*." + self._scriptExt):
			# print "*** Action! {s}***".format(s=script)
			# print actor.act(open(script))
			pass
			
			
def direct(option, opt, value, parser):
	"""Direct a script to do something particular."""
	script, options = parser.rargs[0], parser.rargs[1:]
	logging.debug("Using script %s with %d options" % (script, len(options)))

	scriptOptions = None
	if options:
		scriptOptions = {}
		for option in options:
			assert option.startswith('--')
			opt, val = option.lstrip('--').split('=')
			scriptOptions[opt] = val
			
	actor = Actor()
	action = actor.act(open(script), **scriptOptions)
	print action
	sys.exit()
			
def explain(option, opt, value, parser):
	"""Explain script usage."""
	from pprint import pprint
	actor = Actor()
	script = parser.rargs[0]
	action = actor.act(open(script))
	print actor.header
	sys.exit()
	
if __name__ == '__main__':
	DEBUG = True
	DEBUG = False
	
	if DEBUG:
		unittest.main()
	
	from optparse import OptionParser, OptionValueError, make_option
	optionList = [
		make_option("-s", "--script", metavar="FILE", help="Read input from FILE"),
		# make_option("-o", "--output", metavar="FILE", help="Write output to FILE"),
		make_option("-d", "--direct", action="callback", callback=direct, help="Direct FILE using given parameterization details"),
		make_option("-e", "--explain", action="callback", callback=explain, help="Explain FILE parameterization details"),
		make_option("-v", action="count", dest="verbosity")
	]
	oParser = OptionParser(version="%prog 0.1", option_list=optionList)
	oParser.set_defaults(verbosity=0)
	# (options, args) = oParser.parse_args("-d scripts/select_constant.sql --constant=1337".split())
	(options, args) = oParser.parse_args()
	
	# The script file should be given in one of two ways:
	# 1) Via the -s or --script option or
	# 2) the first positional argument
	if options.script and len(args) > 0:
		raise OptionValueError("You should only specify one scipt per run")
	elif not options.script and not len(args) > 0:
		raise OptionValueError("No script file given")
	elif not options.script and len(args) > 0:
		logging.debug("Script given was '{filename}'".format(filename=args[0]))
		options.script = args[0]
		
	actor = Actor()
	action = actor.act(open(options.script))
	print action
	