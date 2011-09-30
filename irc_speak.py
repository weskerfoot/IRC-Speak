#!/usr/bin/env python2

"""
Copyright (C) 2011

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

try:
    import simplejson as json
except ImportError as exception:
    print exception
    import json

import xchat
import argparse
import os
from espeak import espeak

options_path = os.path.expanduser("~/.xchat2/options.json")

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

options = json.load(open(options_path, "rw"))

aliases = {"rate" : 1,
            "volume" : 2,
            "pitch" : 3,
            "vrange" : 4}

def edit_users(**new_options):
    """Edits the options dictionary to add/update a user's settings"""
    nick = new_options['name'][0]
    if not nick in options:
        options[nick] = {"args": {}}
    options[nick]["args"] = {key : value[0] for key,value in new_options.iteritems() if (key and (key!="name") and (key!="language"))}
    # don't want to use name or language, because language needs to get set separately
    # and name is only used to create the main dictionary for their options
    if new_options["language"]:
        options[nick]["language"] = new_options["language"][0]
    return options[nick]

def irc_speak(word, word_eol, users):
    """Checks to see if a user is set to be voiced, and if so synthesizes their text"""
    if word[0] in options: # check to see if the user is in the options dictionary (word[0] == their nick)
        [espeak.set_parameter(aliases[arg], options[word[0]]["args"][arg]) for arg in options[word[0]]["args"]]
        # options[word[0]]["args"][arg] is the same as options[nickname]["args"][arg] (where arg is some one of the names in aliases
        # which corresponds to some integer value in options[nick][args])
        espeak.set_voice(name=options[word[0]]["language"])
        espeak.synth(word[1])
        xchat.emit_print("Channel", word[0], word[1])
        return xchat.EAT_NONE
    return xchat.EAT_NONE # return nothing because they weren't in the options dictionary

def set_user(arguments):
    """Parses arguments and calls the edit_users function"""
    try:
        arguments = editor.parse_args(arguments)
        return edit_users(**vars(arguments))
        # argparse raises a SystemExit error if you use --help or -h, or have the wrong arguments
    except SystemExit as exception:
        return "Exited with status %s" % (exception)
              
def save():
    """Saves a user in the json file"""
    with open(options_path, mode='w') as jsonfile:
        json.dump(options, jsonfile)
    return "Saved!"

def deluser(user):
    """Deletes a user from the global dictionary"""
    if user[0] in options:
        del options[user[0]]
        return "Deleted!"
    return "No such user"
    
def commands(word, word_eol, users):
    """Function for doing different commands with XChat"""
    commands = {"set" : set_user,
                "rm" : deluser,
                "langlist" : (lambda x: ", ".join([item["name"] for item in espeak.list_voices()])),
                "save" : (lambda x: save()),
                "list" : (lambda x: "\n".join(["%s : %s" % (key, value["args"]) for key, value in options.iteritems()]))}

    arguments = word[1:]
    try:
        print commands[arguments[0]](arguments[1:])
    except KeyError:
        return xchat.EAT_XCHAT

xchat.hook_command("ircspeak", commands, help="/ircspeak set --help")
xchat.hook_print("Channel Message", irc_speak)
