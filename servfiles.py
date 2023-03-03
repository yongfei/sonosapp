# -*- coding: utf-8 -*-`

import time
import hashlib
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

files_index = AutoIndex(app, browse_root='/home/john/Downloads/music/', add_url_rules=False)


@app.route("/")
@app.route('/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path, template='template.html')


if __name__ == "__main__":
    app.run(host='192.168.68.128', port=8081,debug=True)
