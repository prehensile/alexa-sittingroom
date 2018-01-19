import logging 
import os
import json

from flask import Flask
from flask_ask import Ask, statement, question

import boto3

from oulipo import OulipoS7


app = Flask( __name__ )
ask = Ask( app, '/' )

#text = "I am sitting in a room different from the one you are in now. I am recording the sound of my speaking voice and I am going to play it back into the room again and again until the resonant frequencies of the room reinforce themselves so that any semblance of my speech, with perhaps the exception of rhythm, is destroyed. What you will hear, then, are the natural resonant frequencies of the room articulated by speech. I regard this activity not so much as a demonstration of a physical fact, but more as a way to smooth out any irregularities my speech might have."
text = """ I am sitting in a room different from the one you are in now.
I am recording the sound of my speaking voice and I am going to play it 
back into the room again and again until the resonant frequencies of the 
room reinforce themselves so that any semblance of my speech, with perhaps 
the exception of rhythm, is destroyed. What you will hear, then, are the 
natural resonant frequencies of the room articulated by speech. 
I regard this activity not so much as a demonstration of a physical fact, 
but more as a way to smooth out any irregularities my speech might have."""
oulipo = OulipoS7()


def ssml_for_text( text, next_iteration ):
    
    logging.debug( "ssml_for_text: %s", text )
    
    use_polly = os.environ.get( "USE_POLLYS3", "no" )
    pollys3_arn = os.environ.get( "POLLYS3_ARN" )
    invocation_name = os.environ.get( "NEXT_INVOCATION", "sitting room" )
    
    # construct ssml, which will be spoken by polly or alexa
    ssml = '<speak>{}<break strength="x-strong"/>Alexa, ask {} for iteration {}</speak>'.format(
        text,
        invocation_name,
        next_iteration
    )

    if use_polly != "no":
        # use an instance of polly-s3 to generate voice, get an mp3 URL
        boto_lambda = boto3.client( 'lambda' )
        r = boto_lambda.invoke(
            FunctionName=pollys3_arn,
            Payload=json.dumps(
                { "text" : ssml }
            )
        )
        payload = r['Payload']
        url = json.load( payload )
        # rewrite output ssml to just the polly-generated mp3 
        ssml = '<speak><audio src="{}" /></speak>'.format( url )
    
    return ssml


@ask.launch
def launch():
    logging.debug( "LaunchIntent" )
    return iterate( 0 )


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
    
    iterated = oulipo.iterate( text, iteration, seed=628103 )

    speech = ssml_for_text(
        iterated,
        iteration + 1
    )
    
    return statement( speech ).simple_card(
        'Iteration #{}'.format( iteration ),
        iterated
    )


def lambda_handler( event, _context ):
    return ask.run_aws_lambda( event )


if __name__ == '__main__':
    app.run( debug=True )
