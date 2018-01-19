import logging 
import os

from flask import Flask
from flask_ask import Ask, statement, question

from oulipo import OulipoS7


app = Flask( __name__ )
ask = Ask( app, '/' )

text = "I am sitting in a room different from the one you are in now. I am recording the sound of my speaking voice and I am going to play it back into the room again and again until the resonant frequencies of the room reinforce themselves so that any semblance of my speech, with perhaps the exception of rhythm, is destroyed. What you will hear, then, are the natural resonant frequencies of the room articulated by speech. I regard this activity not so much as a demonstration of a physical fact, but more as a way to smooth out any irregularities my speech might have."
oulipo = OulipoS7()


@ask.launch
def launch():
    logging.debug( "LaunchIntent" )
    return iterate( 1 )


@ask.intent( 'AMAZON.HelpIntent' )
def help():
    logging.debug( "HelpIntent" )
    speech_text = 'Try asking me for a numbered iteration.'
    return question(speech_text).reprompt(speech_text).simple_card(
        'Help',
        speech_text
    )


@ask.intent( 'IterateIntent', mapping={'iteration': 'IterationNumber'} )
def iterate( iteration ):
    iteration = int( iteration )
    logging.debug( "IterateIntent, iteration #%d", iteration )
    iterated = oulipo.iterate( text, iteration, seed=315890 )
    next_iteration = "Alexa, ask {} for iteration {}".format(
        os.environ.get( "SKILL_NAME", "sitting room" ),
        iteration + 1
    )
    speech = "{}{}".format(
        iterated,
        next_iteration
    )
    return statement( speech ).simple_card(
        'Iteration #{}'.format( iteration ),
        iterated
    )


def lambda_handler( event, _context ):
    return ask.run_aws_lambda( event )


if __name__ == '__main__':
    app.run( debug=True )
