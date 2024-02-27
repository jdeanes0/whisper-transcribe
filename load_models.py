"""
Loads all whisper models in sequence to avoid downloading them later.

@author jdeanes0
@version 2/26/24
"""

import whisper

whisper.load_model('tiny')
whisper.load_model('base')
whisper.load_model('small')
whisper.load_model('medium')
whisper.load_model('large')
whisper.load_model('large-v2')
