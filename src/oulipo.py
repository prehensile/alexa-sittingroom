import os
import random

import nltk

from nltk import pos_tag, word_tokenize

def init_ntlk():    
    pth = os.path.join( os.path.realpath( os.path.dirname(__file__) ), "nltk_data" )
    nltk.data.path.append( pth )

init_ntlk()


class OulipoS7( object ):
    """docstring for OulipoS7"""
    
    def __init__( self, seed=None ):
        super(OulipoS7, self).__init__()
        self._nouns = self._load_nouns( "nouns.txt" )
        self._random = random.Random( seed )


    def _load_nouns( self, data_path ):
        with( open(data_path) ) as fh:
            nouns = [ line.rstrip() for line in fh ]
        return nouns
     

    def shift( self, noun, offset ):
        nouns = self._nouns
        i = (nouns.index( noun ) + offset) % len(nouns)
        return nouns[ i ]


    def iterate( self, text, iterations, seed=None ):
        
        # reset PRG so that iterations are predictable
        self._random.seed( seed )

        # tokenize text 
        tagged = pos_tag( word_tokenize( text ) )

        words_out = [ tag[0] for tag in tagged ]
        
        # construct a list of noun locations in tokenised sentence
        noun_indexes = []
        for i in range( len(tagged) ):
            tag = tagged[i]
            # if word is a noun...
            if 'nn' == tag[1].lower():
                noun_indexes.append(i)

        while iterations > 0:
            try:
                # target a noun in tokenised sentence and shift it
                target_index = self._random.choice( noun_indexes )
                noun = words_out[ target_index ]
                words_out[ target_index ] = self.shift( noun, 7 )
                # decrement counter...
                iterations -=1
            except ValueError as e:
                pass

        return " ".join( words_out )

        

