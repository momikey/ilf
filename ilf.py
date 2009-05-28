#!/usr/bin/env python

# (C) 2009 Michael Potter
# This program is made available under the MIT License
# See the LICENSE file for more details

from optparse import OptionParser

PROG_NAME = "ILF"
PROG_INFO = "An Interlinear Formatting Script"
VERSION = "0.3"

# These templates make a valid "skeleton" HTML file so the output will be
# a full page instead of an HTML fragment. They aren't used in wiki mode.
TEMPLATE_HTML_BEGIN = \
"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title></title>
<meta name="generator" content="ILF Interlinear Formatter">
<meta name="ROBOTS" content="NOINDEX, NOFOLLOW">
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8">
<meta http-equiv="content-style-type" content="text/css">
<link href="./ilf.css" rel="stylesheet" type="text/css">
</head>
<body>
"""

TEMPLATE_HTML_END = \
"""

</body>
</html>
"""

# tags (copied from SIL toolbox, except \i)
# \t Text to be translated (freeform)
# \i Phonetic rendering of the text (IPA, CXS, etc.)
# \m Text broken into morphemes
# \g Gloss of each morpheme
# \p Part of speech for each morpheme
# \f Freeform translation of the entire text
TABLETAGS = [r'\g', r'\m', r'\p', r'\i']
FFTAGS = [r'\f', r'\t']

class InterlinearFormatter(object):
	"""A formatter for SIL Toolbox interlinear files"""

	def __init__(self, usewiki=False):
		self.wiki = usewiki

	# write the opening tag of a table
	# fn: the target file
	# usewiki: output MediaWiki markup instead of HTML
	def _startTable(self, fn, usewiki=False):
		"""Write the opening markup for a table"""
		if usewiki:
				fn.write("\n{| class='interlinear'\n")
		else:
			# just use a basic table, and let the user's CSS do the rest
			fn.write('<table class="interlinear">\n')

	# write a table row
	# fn: the target file
	# row: the text to write
	# tag: the type of line (phonetic, morphemic, gloss, etc.)
	# usewiki: output MediaWiki markup instead of HTML
	def _writeTableRow(self, fn, row, tag, usewiki=False):
		"""Write a single interlinearized table row, one column per word or morpheme"""
		if usewiki:
			fn.write("|- class='il_%s'\n" % tag)
			for r in row:
				fn.write('| %s\n' % r)
		else:
			fn.write("<tr class='il_%s'>" % tag)
			for r in row:
				fn.write('<td>%s</td>\n' % r)
			fn.write('</tr>\n')
		
	# write a freeform row
	# fn: the target file
	# row: the text to write
	# tag: the type of line (source or target language)
	# colspan: the number of columns in the table
	# usewiki: output MediaWiki markup instead of HTML
	def _writeFreeformRow(self, fn, row, tag, colspan, usewiki=False):
		"""Write a single freeform row, with a single column that spans the whole row"""
		if usewiki:
			fn.write("|- class='il_%s'\n" % tag)
			if colspan:
				fn.write("| colspan=%d" % colspan)
			fn.write('| %s\n' % ' '.join(row))
		else:
			fn.write("<tr class='il_%s'><td colspan='%d'>%s</td></tr>\n" 
				% (tag, colspan, ' '.join(row)))

	# write the closing tag of a table
	# fn: the target file
	# usewiki: output MediaWiki markup instead of HTML
	def _endTable(self, fn, usewiki=False):
		"""Write the closing tag or wiki markup for a table"""
		if usewiki:
			fn.write('|}\n')
			fn.write('\n')  # blank line for padding
		else:
			fn.write('</table>')
			fn.write('<br>\n')  # blank line for padding

	def format(self, inputFile, outputFile):
		"""Write a formatted interlinear to an HTML page or wiki markup"""
		if not self.wiki:
			outputFile.write(TEMPLATE_HTML_BEGIN)

		colspan = 0
		started = False
		fileLines = inputFile.readlines()
		for line in fileLines:
			# split the line, and see if we have a tag
			splitLine = line.split()
			if not splitLine:
				if started:		# don't print table endings before the text
					# a blank line means the end of a table
					self._endTable(outputFile, self.wiki)
					colspan = 0
			else:
				# the tag is always at the beginning of a line
				tag = splitLine[0]
				text = splitLine[1:]
				if tag in TABLETAGS:
					# non-freeform tags have one word per column,
					# but we keep track the highest number of columns
					# so that we'll know how big to make the next freeform row
					colspan = max(colspan, len(text))
					self._writeTableRow(outputFile, text, tag[1:], self.wiki)
					started = True
				elif tag in FFTAGS:
					# "\t" is supposed to come first, so we have to look ahead
					# to know how big it should be
					if tag == r'\t':
						nextLine = fileLines[fileLines.index(line)+1]
						colspan = len(nextLine.split()) - 1 # -1 because of tag
						self._startTable(outputFile, self.wiki)
					self._writeFreeformRow(outputFile, text, tag[1:], colspan, self.wiki)
					colspan = 0
					started = True
				else:
					continue
		
		if not self.wiki:
			outputFile.write(TEMPLATE_HTML_END)


if __name__ == '__main__':
	
	# command-line arguments handling
	opts = OptionParser(version=
	"%s -- %s -- version %s\n(C) 2007-2009 Michael Potter -- See LICENSE file for more information" \
				% (PROG_NAME, PROG_INFO, VERSION))
	opts.set_defaults(ifile="input.txt", ofile="output.html", usewiki=False)
	opts.add_option('-w', '--wiki', action='store_true', dest='usewiki',
		help='output MediaWiki markup instead of default HTML')
	opts.add_option('-i', '--input', dest='ifile',
		help='input file name', metavar='INPUT')
	opts.add_option('-o', '--output', dest='ofile',
		help='output file name', metavar='OUTPUT')
	
	(options, args) = opts.parse_args()
	
	inputFile = open(options.ifile, 'r')
	outputFile = open(options.ofile, 'w')

	ilf = InterlinearFormatter(options.usewiki)

	ilf.format(inputFile, outputFile)

	outputFile.close()
	inputFile.close()
