import argparse
from scanner import Scanner,tokens
from parser import Parser

if __name__ == "__main__":

    # this is the command line parser, not the C-simple parser
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', type=str)
    parser.add_argument('--symbol_table', '-s', action='store_true')
    args = parser.parse_args()

    f = open(args.file_name)    
    f_contents = f.read()
    f.close()
    
    s = Scanner(tokens)
    p = Parser(s, args.symbol_table)
    p.parse(f_contents)
