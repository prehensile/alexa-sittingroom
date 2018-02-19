import os
import nltk

pth = os.path.realpath( os.path.dirname(__file__) )    
pth = os.path.join( pth, "src/nltk_data" )
    
if not os.path.exists( pth ):
    os.makedirs( pth )

packages = [
    'perluniprops',
    'punkt',
    'averaged_perceptron_tagger'
]

for package in packages:
    nltk.download( package, download_dir=pth )
