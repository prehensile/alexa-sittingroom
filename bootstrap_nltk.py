import os
import nltk

pth = os.path.realpath( os.path.dirname(__file__) )    
pth = os.path.join( pth, "src/nltk_data" )
    
if not os.path.exists( pth ):
    os.makedirs( pth )

nltk.download( 'perluniprops', download_dir=pth )