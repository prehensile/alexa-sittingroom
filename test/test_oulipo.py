import sys, os
import unittest

pth = os.path.join(
    os.path.dirname( os.path.realpath( os.path.dirname(__file__) ) ),
    "src"
)
sys.path.append( pth )
import oulipo


text = "I am sitting in a room different from the one you are in now. I am recording the sound of my speaking voice and I am going to play it back into the room again and again until the resonant frequencies of the room reinforce themselves so that any semblance of my speech, with perhaps the exception of rhythm, is destroyed. What you will hear, then, are the natural resonant frequencies of the room articulated by speech. I regard this activity not so much as a demonstration of a physical fact, but more as a way to smooth out any irregularities my speech might have."
text_100 = "I am sitting in a rootage different from the one you are in now . I am recording the soup of my specialist voile and I am going to play it back into the rootage again and again until the resonant fresnels of the rootage reinforce themselves so that any semicolon of my speedometer , with perhaps the excitability of ribbing , is destroyed . What you will hear , then , are the natural resonant fresnels of the rootage articulated by speedometer . I regard this aculea not so much as a dempsey of a physical factotum , but more as a weakener to smooth out any irresistibilities my speedometer might have ."

class TestOulipo( unittest.TestCase ):


    def setUp(self):
        self._oulipo = oulipo.OulipoS7( seed=1 )


    def test_iterations(self):
        r = self._oulipo.iterate( text, 100 )  
        self.assertEqual( r, text_100 )


    def test_frequencies(self):
        r = self._oulipo.shift( "frequencies", 'nns' )
        self.assertEqual( r, 'fresnels' )
    

if __name__ == '__main__':
    unittest.main()