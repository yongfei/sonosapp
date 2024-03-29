# -*- coding: utf-8 -*-`
import time
import hashlib
import urllib
import json
import os
import soco

import requests
from flask import Flask, render_template, request, redirect, abort
from flask_autoindex import AutoIndex
import xml.etree.ElementTree as ET

def set_master(masterName):
    master = soco.discovery.by_name(masterName)
    if not master.is_coordinator:
        master.unjoin()
    for d in soco.discover():
        if d != master:
            d.join(master)
    return master

app = Flask(__name__)

app.config.from_pyfile("settings.py")
files_index = AutoIndex(app, browse_root='/home/john/Downloads/music/', add_url_rules=False)

#sonos =soco.discovery.any_soco().group.coordinator
#make patio speaker the master
sonos = set_master("Patio")

BASE_DIR = app.config["BASE_DIR"]
print("playing music at : " + BASE_DIR)
devices = {device.player_name: device for device in soco.discover()}

host = "192.168.68.128"
port = 8080
musicHome = "http://192.168.68.128:8080/"

@app.route("/mfiles")
@app.route('/mfiles/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path, template='template.html')

@app.route("/play")
def play():
    devName = request.args.get('devName')
    if devName and not devName.isspace():
        devices[devName].play()
    else:
        sonos.play()
    return redirect(request.referrer.replace("playfoler=true", ""))

@app.route("/next")
def next():
    devName = request.args.get('devName')
    if devName and not devName.isspace():
        devices[devName].next()
    else:
        sonos.next()
    return redirect(request.referrer.replace("playfoler=true", ""))

@app.route("/play_queue")
def play_queue():
    devName = request.args.get('devName')
    if devName and not devName.isspace():
        devices[devName].play_from_queue(1)
    else:
        sonos.play_from_queue(1)
    return redirect(request.referrer+"?started=true")

@app.route("/queueInfo")
def queueInfo():
    playlist=[]
    q = sonos.get_queue()
    for item in q:
        playlist.append(item.title)
    #print(playlist)
    #return tuple(playlist)
    return render_template('musicinfo.html', playlist=playlist)


@app.route("/pause")
def pause():
    devName = request.args.get('devName')
    if devName and not devName.isspace():
        devices[devName].pause()
    else:
        sonos.pause()
    return redirect(request.referrer)

@app.route('/volup')
def volup():
    devName = request.args.get('devName')
    if devName and not devName.isspace():
        devices[devName].volume += 5
    else:
        for d in devices:
            devices[d].volume += 5
    return redirect(request.referrer.replace("playfolder=true", ""))

@app.route("/voldown")
def voldown():
    devName = request.args.get('devName')
    if devName and not devName.isspace():
        devices[devName].volume -= 5
    else:
        for d in devices:
            devices[d].volume -= 5
    return redirect(request.referrer.replace("playfolder=true", ""))

@app.route("/deviceInfo")
def deviceInfo():
    dinfo={}
    dvc = []
    for dname in sorted(devices.keys(),reverse=True):
        dinfo[dname]=[]
        dinfo[dname].append(devices[dname].ip_address)
        dinfo[dname].append(str(devices[dname].volume))
        dinfo[dname].append(devices[dname].is_coordinator)
    #return dinfo
    return render_template('devices.html', devices=dinfo)

@app.route("/trackinfo")
def trackinfo():
    sonosinfo=sonos.get_current_track_info()
    #print(sonosinfo)
    music_title=""
    try:
        music_length = sonosinfo['duration']
        music_pos = sonosinfo['position']
    except:
        music_length="not availabe"
        music_pos="not known"
    try:
        root=ET.fromstring(sonosinfo['metadata'])
        for elem in root.iter():
            if 'title' in elem.tag:
                music_title += elem.text
            if 'creator' in elem.tag:
                music_title += elem.text
    except Exception as e:
        music_title = ""
    return music_title + "  "+music_length+" <-> " + music_pos + " volume: " + str(sonos.volume)


@app.context_processor
def inject_title():
    sonosinfo=sonos.get_current_track_info()
    music_title=""
    try:
        music_length = sonosinfo['duration']
        music_pos = sonosinfo['position']
    except:
        music_length="not availabe"
        music_pos="not known"
    try:
        root=ET.fromstring(sonosinfo['metadata'])
        for elem in root.iter():
            if 'title' in elem.tag:
                music_title += elem.text
            if 'creator' in elem.tag:
                music_title += elem.text
    except Exception as e:
        music_title = ""
    return{'title': music_title + " duration: "+music_length+" playing at: " + music_pos}

@app.context_processor
def inject_volume():
    return{'volume': str(sonos.volume)}

@app.context_processor
def inject_musicHome():
    return{'musicHome': musicHome}

#@app.route("/")
@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    player=request.args.get('player')
    rhost = request.host.split(':',1)[0]
    hosturl = 'http://'+rhost+':8080/'
    streamurl = 'http://'+rhost+':8080/mfiles/'

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)
    print(abs_path)
    uri_path=req_path.replace('//','/')

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):

        print(uri_path)
        uri=streamurl+urllib.parse.quote(uri_path)
        print('playing' + uri)
        if player != 'local':  sonos.play_uri(uri)
        return redirect(hosturl+req_path.rsplit('/',1)[0])


    # Show directory contents
    files = sorted(os.listdir(abs_path))
    playfolder =  request.args.get('playfolder')
    print(playfolder)
    if playfolder and playfolder == "true":
        sonos.clear_queue()
        for file in files:
            if ".mp3" in file or ".wav" in file:
                uri=streamurl+urllib.parse.quote(uri_path+'/'+file)
                print('adding to queue:'+ uri)
                sonos.add_uri_to_queue(uri)
        print("queue size: " +str(sonos.queue_size))
        if sonos.queue_size>0:
            sonos.play_from_queue(0)

    buri = hosturl+uri_path;
    print(buri)
    return render_template('files.html', files=files, player=player, qsize=sonos.queue_size,buri=buri.rsplit('/',1)[0], streamurl=streamurl.rstrip('/'))


if __name__ == "__main__":
    app.run(host="192.168.68.128", port=8080,debug=False)
