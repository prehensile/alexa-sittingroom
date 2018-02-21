import logging 
import os
import json
import random

from flask import Flask
from flask_ask import Ask, statement, question

import boto3

from oulipo import OulipoS7
from dynamodb import DynamoDBHandler

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

# get text from env
text = os.environ.get( "SPEECH_TEXT", text )
logging.debug( "Text: ", text )

# init oulipo instance
oulipo = OulipoS7()

# dynamodb connector
dynamo = DynamoDBHandler()


def next_invocation( iteration_number ):
    
    invocation_name = os.environ.get( "NEXT_INVOCATION", "sitting room" )
    next_wakeword = os.environ.get( "NEXT_WAKEWORD", "Alexa" )
    
    return '{} <break time="500ms"/> ask {} for iteration number {}'.format(
        next_wakeword,
        invocation_name,
        iteration_number
    )

# Geraint, Kimberly, Kendra, Amy, Raveena, Emma, Nicole, Justin, Joanna, Brian, Salli, Russell, Matthew, Ivy, Joey
POLLY_VOICES = [
    "Geraint",
    "Kimberly",
    "Kendra",
    "Amy",
    "Raveena",
    "Emma",
    "Nicole",
    "Justin",
    "Joanna",
    "Brian",
    "Salli",
    "Russell",
    "Matthew",
    # breaks the chain # "Ivy",
    "Joey" 
]

def ssml_for_text( text, next_iteration ):
    
    logging.debug( "ssml_for_text: %s", text )
    
    use_polly = os.environ.get( "USE_POLLYS3", "no" )
    pollys3_arn = os.environ.get( "POLLYS3_ARN" )
    invocation =  next_invocation( next_iteration )
    
    # construct ssml, which will be spoken by polly or alexa
    ssml = """
    <speak>
        {}
        <break time="1s"/>
        {}
    </speak>
    """.format(
        text,
        invocation
    )

    logging.debug( ssml )

    if use_polly != "no":
        # use an instance of polly-s3 to generate voice, get an mp3 URL
        boto_lambda = boto3.client( 'lambda' )
        r = boto_lambda.invoke(
            FunctionName=pollys3_arn,
            Payload=json.dumps({
                "text" : ssml,
                "VoiceId" : random.choice( POLLY_VOICES )
            })
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
    
    if iteration is None:
        logging.debug( "Iteration is NONE, fetch from dynamodb..." )
        iteration = dynamo.get_iteration() + 1

    iteration = int( iteration )
    
    # offset the iteration with an env var, if present
    iteration_offset = int( os.environ.get( "ITERATION_OFFSET", "0" ) )
    iteration_offset = max( 0, iteration + iteration_offset )

    logging.debug( "IterateIntent, iteration #%d", iteration )
    
    iterated = oulipo.iterate( text, iteration_offset, seed=628103 )

    speech = ssml_for_text(
        iterated,
        iteration + 1
    )

    try:
        dynamo.set_iteration( iteration )
    except Exception as e:
        logging.exception( e )
    
    return statement( speech ).simple_card(
        'Iteration #{}'.format( iteration ),
        iterated
    )


def init_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


# running from lambda
def lambda_handler( event, _context ):
    init_logging()
    return ask.run_aws_lambda( event )


# running on command line
if __name__ == '__main__':
    app.run( debug=True )
