# -*- coding: utf-8 -*-`
import time
import hashlib
import urllib
import json
import os

import requests
from flask import Flask, render_template, url_for
from flask_autoindex import AutoIndex
from flask import send_file
from flask import abort

from soco import SoCo

app = Flask(__name__)

app.config.from_pyfile("settings.py")

sonos = SoCo(app.config["SPEAKER_IP"])

#files_index = AutoIndex(app, browse_root='music/', add_url_rules=False)

def gen_sig():
    return hashlib.md5(
        (
            app.config["ROVI_API_KEY"]
            + app.config["ROVI_SHARED_SECRET"]
            + repr(int(time.time()))
        ).encode("utf-8")
    ).hexdigest()


def get_track_image(artist, album):
    blank_image = url_for("static", filename="img/blank.jpg")
    if "ROVI_SHARED_SECRET" not in app.config:
        return blank_image
    elif "ROVI_API_KEY" not in app.config:
        return blank_image

    headers = {"Accept-Encoding": "gzip"}
    req = requests.get(
        "http://api.rovicorp.com/recognition/v2.1/music/match/album?apikey="
        + app.config["ROVI_API_KEY"]
        + "&sig="
        + gen_sig()
        + "&name= "
        + album
        + "&performername="
        + artist
        + "&include=images&size=1",
        headers=headers,
    )

    if req.status_code != requests.codes.ok:
        return blank_image

    result = json.loads(req.content)
    try:
        return result["matchResponse"]["results"][0]["album"]["images"][0]["front"][3][
            "url"
        ]
    except (KeyError, IndexError):
        return blank_image
@app.route('/music', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = '/home/john/Downloads/'

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
        return "Ok"


    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)

@app.route("/play")
def play():
    sonos.play()
    return "Ok"

"""
@app.route("/music")
@app.route("/music/")
@app.route('/music/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path, template='template.html')
"""

@app.route("/pause")
def pause():
    sonos.pause()
    return "Ok"


@app.route("/next")
def next():
    sonos.next()
    return "Ok"


@app.route("/previous")
def previous():
    sonos.previous()
    return "Ok"


@app.route("/info-light")
def info_light():
    track = sonos.get_current_track_info()
    return json.dumps(track)


@app.route("/info")
def info():
    track = sonos.get_current_track_info()
    track["image"] = get_track_image(track["artist"], track["album"])
    return json.dumps(track)


@app.route("/")
def index():
    track = sonos.get_current_track_info()
    track["image"] = get_track_image(track["artist"], track["album"])
    return render_template("index.html", track=track)


if __name__ == "__main__":
    app.run(host='192.168.68.128', port=8080,debug=True)
