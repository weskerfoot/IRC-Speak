#!/usr/bin/env python2

try:
    import simplejson as json
except ImportError as exception:
    print exception
    import json

import xchat
import argparse
from espeak import espeak

__module_name__ = "IRC Speak" 
__module_version__ = "1.1" 
__module_description__ = "Allows you to make certain users' text run through a voice synthesizer"

editor = argparse.ArgumentParser(description="""
Specify a user. If that user already exists their options will be updated. If they do not exist they will be added.
If you do not specify arg(s) then the default values will be used for each of them.
""")

editor.add_argument("--name", nargs=1, type=str, required=True, help="e.g. /ircspeak set -volume=<int> -pitch=<int> --name=foo")
editor.add_argument("-volume", nargs=1, type=int, default=[70], help="default=70")
editor.add_argument("-pitch", nargs=1, type=int, default=[50], help="default=50")
editor.add_argument("-rate", nargs=1, type=int, default=[175], help="default=175")
editor.add_argument("-vrange", nargs=1, type=int, default=[50], help="default=50")
editor.add_argument("-language", nargs=1, type=str, help="type \"/ircspeak langlist\" to get a list of languages", default=["english"])

##options = json.load(open("options.json", "rw"))

aliases = {"rate" : 1,
            "volume" : 2,
            "pitch" : 3,
            "vrange" : 4}

options = {"nick-here" : {"args": {"pitch" : 200}, "language" : "english"},"nick2-here" :  {"args": {"pitch" : 40}, "language" : "english"}}

def edit_users(*args, **new_options):
    nick = new_options['name'][0]
    if not options.has_key(nick):
        options[nick] = {"args": {}}
        
    for item in new_options:
        if (new_options[item] and (item!="name") and (item!="language")):
        # don't want to use name or language, because language needs to get set separately
        # and name is only used to create the main dictionary for their options
            options[nick]["args"][item] = new_options[item][0]
    
    if new_options["language"]:
        options[nick]["language"] = new_options["language"][0]
    return options    

def irc_speak(word, word_eol, users):
    if options.has_key(word[0]): # check to see if the user is in the options dictionary (word[0] == their nick)
        [espeak.set_parameter(aliases[arg], options[word[0]]["args"][arg]) for arg in options[word[0]]["args"]]
        # options[word[0]]["args"][arg] is the same as options[nickname]["args"][arg] (where arg is some one of the names in aliases
        # which corresponds to some integer value in options[nick][args])
        espeak.set_voice(name=options[word[0]]["language"])
        return espeak.synth(word[1])
    return # return nothing because they weren't in the options dictionary

def commands(word, word_eol, users):
    arguments = word[1:]
    if arguments[0] == "set":
        try:
            print edit_users(**vars(editor.parse_args(arguments[1:])))
            # argparse raises a SystemExit error if you use --help or -h, or have the wrong arguments
        except SystemExit:
            pass
    elif arguments[0] == "langlist":
        for item in espeak.list_voices():
            print item["name"] 

xchat.hook_print("Channel Message", irc_speak)
xchat.hook_command("ircspeak",commands)  
