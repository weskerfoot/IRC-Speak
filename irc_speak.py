#!/usr/bin/env python2

import xchat
from espeak import espeak
__module_name__ = "IRC Speak" 
__module_version__ = "1.0" 
__module_description__ = "Allows you to make certain users' text run through a voice synthesizer"


defaults = {"rate" : (1,175),
            "volume" : (2,70),
            "pitch" : (3,50),
            "vrange" : (4,50)}

names = {"nick-here" : {"args": {"pitch" : 200}, "language" : "english"},
         "nick-here" :  {"args": {"pitch" : 40}, "language" : "english"}}

def say(sentence, language="english", **kargs):
    espeak.set_voice(name=language)
    if not kargs:
        [espeak.set_parameter(defaults[arg][0], defaults[arg][1]) for arg in defaults] #setting the values, the [1] is there because defaults has tuples, not single values
    else:
        [espeak.set_parameter(defaults[arg][0], kargs[arg]) for arg in kargs]
    return espeak.synth(sentence)

def irc_speak(word, word_eol, users):
    if names.has_key(word[0]):
        say(word[1], names[word[0]]["language"], **names[word[0]]["args"])

def commands(word, word_eol, users):
    arguments = word[1:]
    cmds = {"langlist" : "\n".join([item["name"] for item in espeak.list_voices()]),
            "names" : names}
    print cmds[arguments[0]]

xchat.hook_print("Channel Message", irc_speak)
xchat.hook_command("speaker",commands)  
