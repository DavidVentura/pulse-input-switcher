#!/usr/bin/env python2

import subprocess
import re
import sys

def program_list(blacklist=[]):
    ret = []
    output = subprocess.Popen(["pacmd", "list-sink-inputs"], stdout=subprocess.PIPE).communicate()[0]
    p_all=re.compile('index: (?P<index>\d+)|application.name = (?P<appname>.*)|application.icon_name = (?P<iconname>.*)|sink: (?P<sink>\d+)')

    last_index=-1
    cur_item = dict()

    for line in output.split("\n"):
        a = p_all.search(line)
        if a is None:
            continue
        index = a.group("index") 
        appname = a.group("appname")
        iconname = a.group("iconname")
        sink = a.group("sink")
        if index is not None:
            if index!=last_index and cur_item!=dict():
                if cur_item["appname"] not in blacklist and (("iconname" in cur_item and cur_item["iconname"] not in blacklist) or True):
                    if not "iconname" in cur_item:
                        cur_item["iconname"]=cur_item["appname"]

                    ret.append(cur_item)
                cur_item=dict()

            cur_item["index"]=int(index)
        if sink is not None:
            cur_item["sink"]=int(sink)
        if appname is not None:
            cur_item["appname"]=appname.strip('"')
        if iconname is not None:
            cur_item["iconname"]=iconname.strip('"')

    if not "iconname" in cur_item:
        cur_item["iconname"]=cur_item["appname"]
    ret.append(cur_item)
    return ret

def sink_list():
    ret = []
    output = subprocess.Popen(["pacmd", "list-sinks"], stdout=subprocess.PIPE).communicate()[0]
    p_all=re.compile('index: (?P<index>\d+)|device.profile.description = (?P<desc>.*)')
    last_index=-1
    cur_item = dict()

    for line in output.split("\n"):
        a = p_all.search(line)
        if a is None:
            continue
        index = a.group("index") 
        desc = a.group("desc")
        if index is not None:
            if index!=last_index and cur_item!=dict():
                ret.append(cur_item)
                cur_item=dict()
            cur_item["index"]=int(index)
        if desc is not None:
            cur_item["desc"]=desc.strip('"')

    ret.append(cur_item)
    return ret

def move_program(program, sink):
    subprocess.Popen(["pacmd","move-sink-input", program, sink])

def pretty_print(dict_list):
    col_width = max(len(str(value)) for item in dict_list for key,value in item.iteritems()) + 2
    print_header=True
    for item in dict_list:
        if print_header:
            for key,value in item.iteritems():
                sys.stdout.write("".join(str(key).ljust(col_width)))
                print_header=False
            print("")
            print("="*col_width*(len(item.keys())+1))

        for key,value in item.iteritems():
            sys.stdout.write("".join(str(value).ljust(col_width)))
        print("")

programs=program_list(["speech-dispatcher"])
sinks=sink_list()

if len(sys.argv) != 3:
    print("Programs")
    pretty_print(programs)
    print("")
    print("Sinks")
    pretty_print(sinks)
    print("")
    print("Usage: %s <program> <sink>" % sys.argv[0])
else:
    move_program(sys.argv[1], sys.argv[2])
