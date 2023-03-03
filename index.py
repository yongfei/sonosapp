# -*- coding: utf-8 -*-`
import time
import hashlib
import urllib
import json
import os

import requests
from flask import Flask, render_template, url_for
from flask import send_file
from flask import abort

from soco import SoCo

app = Flask(__name__)

app.config.from_pyfile("settings.py")

sonos = SoCo(app.config["SPEAKER_IP"])


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
        return "Ok"


    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)


if __name__ == "__main__":
    app.run(host='192.168.68.128', port=8080,debug=True)
