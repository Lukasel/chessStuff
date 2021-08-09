'''
This python script accepts a file with FEN-strings (Forsyth-Edwards Notation)
and additional metadata and transforms it into a PGN file (Portable Game Notation).
FEN data has to be in the form:

{ ( FEN \n Metadata ) | ( Metadata \n FEN ) \n (solution)? \n }*

with - FEN being a valid FEN string that desrcibes a chess position
        * exmple: r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0
     - Metadata = <white name> vs <black name>, <location>, <year>
        * example: Henry Buckle vs NN, London, 1840
     - solution is an optional puzzle solution in PGN notation
        * example: 1. Nf6+ gxf6 2. Bxf7#

This script will need some work to make more generally applicable.
'''

import sys
import re

# The a-hA-H in the castling rights section is for compatability
# with Shredder-FEN for Chess960
fen_re = re.compile(r"[a-zA-Z1-8]+(?:/[a-zA-Z1-8]+){7}\s[wb]\s(-|[KkQqa-hA-H]+)\s(-|[a-h][36])\s\d+\s\d+")
meta_re = re.compile(r"(?P<white>.*)\svs\s(?P<black>.*),\s(?P<site>.*),\s(?P<year>\d*)")

def pgnize(fen: str, metaline: str, solution: str, includesolution: bool):
    '''Returns the PGN output for the data from the FEN file'''
    meta = re.match(meta_re, metaline)
    if includesolution:
        playline = solution + ' *'
    else:
        playline = '*'
    if meta:
        return '[Variant "From Position"]\n[FEN "' + fen.strip() + '"]\n[Site "' + \
            meta.group('site') + '"]\n[Date "' + meta.group('year') + '"]\n[White "' + \
            meta.group('white') + '"]\n[Black "' + meta.group('black') + \
            '"]\n[Result "*"]\n' + playline + '\n\n'
    else:
        return '[Variant "From Position"]\n[FEN "' + fen.strip() + \
            '"]\n[Result "*"]\n' + playline + '\n\n'


def discernfen(stra, strb):
    '''Finds out which string is the FEN and returns the tuple (FEN, metaline) or
    None if neither string matches'''
    if re.match(fen_re, stra):
        return stra, strb
    elif re.match(fen_re, strb):
        return strb, stra
    else:
        return None


def fen_convert_loop(fenfile, pgnfile, includesolutions):
    firstloop = True

    while fenfile:
        if firstloop:
            firstloop = False
        else:
            fenfile.readline()  # read an empty separator line away
        stra = fenfile.readline()
        strb = fenfile.readline()
        solution = fenfile.readline()
        fenresult = discernfen(stra, strb)
        if fenresult:
            fen, metaline = fenresult
        else:
            if stra and strb:
                print(stra)
                print(strb)
            else:
                break;
            print('No FEN match')
            continue
        pgn = pgnize(fen, metaline, solution, includesolutions)
        pgnfile.write(pgn)


def convert_fen_to_pgn(fenfilename: str, pgnfilename: str, includesolutions=True):
    '''Given an input filename (fenfilename) and a filename for the output
    (pgnfilename) the FEN input data will be converted to PGN format and saved
    in the output file.'''
    fenfile = open(fenfilename, 'r')
    pgnfile = open(pgnfilename, 'w')

    fen_convert_loop(fenfile, pgnfile, includesolutions)

    fenfile.close()
    pgnfile.close()


if __name__ == '__main__':
    # command line argument handling
    # arg 0 is the programm name
    if len(sys.argv) >= 2:
        rawfilename = sys.argv[1]
        if rawfilename.endswith('.fen'):
            fenfilename = rawfilename
            pgnfilename = rawfilename[0:-4] + '.pgn'
        else:
            fenfilename = rawfilename + '.fen'
            pgnfilename = rawfilename + '.pgn'

    else:
        print('Bitte Dateiname als Argument angeben. Dateiname muss auf .fen enden')
        sys.exit()

    includesolutions = False
    if len(sys.argv) >= 3:
        if sys.argv[2] == 'True' or sys.argv[2] == 'true' or sys.argv[2] == 't':
            includesolutions = True

    convert_fen_to_pgn(fenfilename, pgnfilename, includesolutions)

