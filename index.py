# -*- coding: utf-8 -*-`
import time
import hashlib
import urllib
import json
import os
import soco

import requests
from flask import Flask, render_template, url_for, redirect
from flask import send_file
from flask import abort
import xml.etree.ElementTree as ET

from soco import SoCo

app = Flask(__name__)

app.config.from_pyfile("settings.py")

sonos = SoCo(app.config["SPEAKER_IP"])

host = "192.1668.68.128"
port = 8080
musicHome = "http://192.168.68.128:8080/"
music_title=""

@app.route("/play")
def play():
    sonos.play()
    return redirect(musicHome)


@app.route("/pause")
def pause():
    sonos.pause()
    return redirect(musicHome)

@app.route("/volup")
def volup():
    sonos.volume = sonos.volume + 5
    return redirect(musicHome)

@app.route("/voldown")
def voldown():
    sonos.volume = sonos.volume - 5
    return redirect(musicHome)

@app.route("/deviceInfo")
def deviceInfo():
    dinfo={}
    dvc = []
    devices = {device.player_name: device for device in soco.discover()}
    for dname in devices.keys():
        dinfo[dname]=[]
        dinfo[dname].append(devices[dname].ip_address)
        dinfo[dname].append(str(devices[dname].volume))
    #return dinfo
    return render_template('devices.html', devices=dinfo)


@app.context_processor
def inject_title():
    sonosinfo=sonos.get_current_track_info()
    root=ET.fromstring(sonosinfo['metadata'])
    #root = tree.getroot()
    music_title = root[0][2].text
    return{'title': music_title}

@app.context_processor
def inject_volume():
    return{'volume': str(sonos.volume)}

#@app.route("/")
@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = '/home/john/Downloads/music'

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)
    print(abs_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):

        #return send_file(abs_path)
        #uri='http://192.168.68.128:8081/'+abs_path.lstrip('./music/')
        #uri_path=abs_path.lstrip(BASE_DIR).replace('//','/')
        uri_path=req_path.replace('//','/')
        print(uri_path)
        uri='http://192.168.68.128:8081/'+urllib.parse.quote(uri_path)
        print(uri)
        sonos.play_uri(uri)
        return redirect(musicHome+req_path.rsplit('/',1)[0])


    # Show directory contents
    files = os.listdir(abs_path)
    counter = 0
    return render_template('files.html', files=files)


if __name__ == "__main__":
    app.run(host="192.168.68.128", port=8080,debug=True)
