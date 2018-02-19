import os
import random
import logging
from collections import namedtuple

import nltk
from nltk import pos_tag, word_tokenize

import inflect


_MODULE_PATH = os.path.realpath( os.path.dirname(__file__) )


def init_ntlk():    
    pth = os.path.join( _MODULE_PATH, "nltk_data" )
    nltk.data.path.append( pth )

init_ntlk()

p = inflect.engine()


TargetWord = namedtuple( "TargetWord", ['index','word','pos'])


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
        pth = os.path.join( _MODULE_PATH, dict_path )
        with( open(pth) ) as fh:
            wl = [ line.rstrip() for line in fh ]
        return wl


    def shift_singular( self, noun, offset=7 ):
        nouns = self._nouns
        i = (nouns.index( noun ) + offset) % len(nouns)
        # get the offset noun from wordlist
        return nouns[ i ]


    def shift_plural( self, noun, offset=7 ):

        # get the singular form of input noun
        singular = p.singular_noun( noun )
        
        if singular:
            # if we've successfully singularised noun...
            # get the shifted noun
            shifted = self.shift_singular( singular )
            # return pluralised version
            return p.plural( shifted )


    def shift( self, noun, pos, offset=7 ):
        
        # first case: if input noun is in wordlist, just return the shifted version
        if noun in self._nouns:
            return self.shift_singular( noun, offset )
        
        # wordlists are singular, so chances are an unmatched noun is plural

        if pos.lower() == 'nns':
            return self.shift_plural( noun, offset )

        # last case - just return a noun we haven't been able to shift
        return noun 


    def iterate( self, text, iterations, seed=None ):
        
        # reset PRG so that iterations are predictable
        self._random.seed( seed )

        # tokenize text 
        tagged = pos_tag( word_tokenize( text ) )

        words_out = [ tag[0] for tag in tagged ]
        
        # construct a list of noun locations in tokenised sentence
        target_words = []
        for i in range( len(tagged) ):
            tag = tagged[i]
            pos = tag[1]
            # if word is a noun...
            if 'nn' == pos.lower()[:2]:
                target_words.append( TargetWord( index=i, word=tag[0], pos=pos ) )

        while iterations > 0:
            try:
                # target a noun in tokenised sentence and shift it
                target_word = self._random.choice( target_words )
                words_out[ target_word.index ] = self.shift( target_word.word, target_word.pos, offset=7 )
                # decrement counter...
                iterations -=1
            except ValueError as e:
                logging.exception( e )
                pass

        return " ".join( words_out )

        

