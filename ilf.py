#!/usr/bin/env python

from optparse import OptionParser

PROG_NAME = "ILF"
VERSION = "0.1"

# tags (copied from SIL toolbox, except \i)
# \t Text to be translated (free-form)
# \i Phonetic rendering of the text (IPA, CXS, etc.)
# \m Text broken into morphemes
# \g Gloss of each morpheme
# \p Part of speech for each morpheme
# \f Free-form translation of the entire text
tabletags = [r'\g', r'\m', r'\p', r'\i']
fftags = [r'\f', r'\t']

def endTable(fn, usewiki):
    if usewiki:
        fn.write('|}\n')
        fn.write('\n')  # blank line for padding
    else:
        fn.write('</table>')
        fn.write('<br />')  # blank line for padding, XHTML

def startTable(fn, usewiki):
    if usewiki:
        fn.write("\n{| class='interlinear'\n")
    else:
        fn.write('<table border="0" cellpadding="0" cellspacing="5" class="interlinear">')

def writeTableRow(fn, usewiki, row, tag):
    if usewiki:
        fn.write("|- class='il_%s'\n" % tag)
        for r in row:
            fn.write('| %s\n' % r)
    else:
        fn.write("<tr class='il_%s'>" % tag)
        for r in row:
            fn.write('<td>%s</td>\n' % r)
        fn.write('</tr>')
    
def writeFreeformRow(fn, usewiki, row, tag, colspan):
    if usewiki:
        fn.write("|- class='il_%s'\n" % tag)
        if colspan:
            fn.write("| colspan=%d" % colspan)
        fn.write('| %s\n' % ' '.join(row))
    else:
        fn.write("<tr class='il_%s'><td colspan='%d'>%s</td></tr>" 
            % (tag, colspan, ' '.join(row)))

if __name__ == '__main__':
    
    # command-line arguments handling
    opts = OptionParser(version=
    "%s %s\n(C) 2007 Michael Potter" % (PROG_NAME, VERSION))
    opts.set_defaults(pfilename='patterns.txt', ffilename='input.txt', 
        ofilename='output.txt', count=1000)
    opts.add_option('-w', '--wiki', action='store_true', dest='usewiki',
        help='output wikitext instead of default HTML')
    opts.add_option('-i', '--input', dest='ifile',
        help='input file name', metavar='INPUT')
    opts.add_option('-o', '--output', dest='ofile',
        help='output file name', metavar='OUTPUT')
    
    (options, args) = opts.parse_args()
    
    inputFile = open(options.ifile, 'r')
    outputFile = open(options.ofile, 'w')
    
    colspan = 0
    isEnded = True
    fileLines = inputFile.readlines()
    for line in fileLines:
        splitLine = line.split()
        if not splitLine:
            endTable(outputFile, options.usewiki)
            isEnded = True
            colspan = 0
        else:
            tag = splitLine[0]
            text = splitLine[1:]
            if tag in tabletags:
                colspan = len(text)
                writeTableRow(outputFile, options.usewiki, text, tag[1:])
            elif tag in fftags:
                if tag == r'\t':
                    nextLine = fileLines[fileLines.index(line)+1]
                    colspan = len(nextLine.split()) - 1 # -1 because of tag
                    startTable(outputFile, options.usewiki)
                    isEnded = False
                writeFreeformRow(outputFile, options.usewiki, text, tag[1:], colspan)
            else:
                continue
    
    outputFile.close()
    inputFile.close()
