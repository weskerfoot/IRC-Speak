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

options = json.load(open("/home/wes/.xchat2/options.json", "rw"))

aliases = {"rate" : 1,
            "volume" : 2,
            "pitch" : 3,
            "vrange" : 4}

def edit_users(*args, **new_options):
    """Edits the options dictionary to add/update a user's settings"""
    
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
    """Checks to see if a user is set to be voiced, and if so synthesizes their text"""
    
    if options.has_key(word[0]): # check to see if the user is in the options dictionary (word[0] == their nick)
        [espeak.set_parameter(aliases[arg], options[word[0]]["args"][arg]) for arg in options[word[0]]["args"]]
        # options[word[0]]["args"][arg] is the same as options[nickname]["args"][arg] (where arg is some one of the names in aliases
        # which corresponds to some integer value in options[nick][args])
        espeak.set_voice(name=options[word[0]]["language"])
        return espeak.synth(word[1])
    return # return nothing because they weren't in the options dictionary

def set_user(arguments):
    try:
        return edit_users(**vars(editor.parse_args(arguments[1:])))
        # argparse raises a SystemExit error if you use --help or -h, or have the wrong arguments
    except SystemExit as exception:
        return "Exited with status %s" % (exception)
              
def save(arguments):
    with open('/home/wes/.xchat2/options.json', mode='w') as jsonfile:
        json.dump(options, jsonfile)
    return "Saved!"

def commands(word, word_eol, users):
    """Function for doing different commands with XChat"""
    
    arguments = word[1:]

    if not arguments:
        return xchat.EAT_XCHAT
            
    commands = {"set" : set_user,
            "langlist" : (lambda x:", ".join([item["name"] for item in espeak.list_voices()])),
            "save" : save}
    try:
        print commands[arguments[0]](arguments)
    except KeyError as exception:
        print "No such option", exception
            
    return xchat.EAT_XCHAT

xchat.hook_print("Channel Message", irc_speak)
xchat.hook_command("ircspeak",commands, userdata=None, help="/ircspeak set --help")  
