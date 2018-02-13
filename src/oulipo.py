import os
import random
import logging

import nltk
from nltk import pos_tag, word_tokenize

import inflect


def init_ntlk():    
    pth = os.path.join( os.path.realpath( os.path.dirname(__file__) ), "nltk_data" )
    nltk.data.path.append( pth )

init_ntlk()

p = inflect.engine()


class OulipoS7( object ):
    """docstring for OulipoS7"""
    
    def __init__( self, seed=None ):
        super(OulipoS7, self).__init__()
        # load wordlists
        self._nouns = self._load_wordlist( "nouns.txt" )
        # self._adjectives = self._load_wordlist( "adjectives.txt" )
        # we'll use this instance of Random so we can control the state of its PRG 
        self._random = random.Random( seed )


    def _load_wordlist( self, dict_path ):
        with( open(dict_path) ) as fh:
            wl = [ line.rstrip() for line in fh ]
        return wl
     

    def shift( self, noun, offset ):
        nouns = self._nouns
        
        # get the singular form of input noun
        singular = p.singular_noun( noun )
        # nouns wordlist is singular forms, so look up the singular and calculate offset index
        i = (nouns.index( singular ) + offset) % len(nouns)
        # get the offset noun from wordlist
        out = nouns[ i ]
        # assume that if singular != original noun, original is plural
        if noun != singular:
            # re-pluralise offset noun before returning
            out = p.plural( singular )
        return out


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
                logging.exception( e )
                pass

        return " ".join( words_out )

        

