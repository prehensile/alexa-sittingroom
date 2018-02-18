#! /usr/bin/env python
import os
import nltk
from nltk.corpus import wordnet

pth = os.path.realpath( os.path.dirname(__file__) )
pth = os.path.join( os.path.dirname( pth ), "src/nltk_data" )
print (pth)
nltk.data.path.append( pth )

try:
    wordnet.all_synsets('n')
except LookupError as e:
    raise
else:
    pass
finally:
    pass


def get_wordlist( pos ):

    # construct an alphabetised list of nouns from wordnet
    # TODO: make this less stupid
    wl = []
    for synset in list(wordnet.all_synsets( pos )):
        name = synset.name().split(".")[0]
        if "_" in name:
            continue
        if "-" in name: 
            name = name.replace( "-", " " )
        
        wl.append( name )

    wl.sort()
    return wl


if __name__ == '__main__':
    
    #wordlists = [ 'n', 'v' ]
    wordlists = [ 'v' ]

    for pos in wordlists:
        wl = get_wordlist( pos )
        with open( "wordlist_%s.txt" % pos, "w" ) as fh:
            fh.writelines( "%s\n" % word for word in wl )

