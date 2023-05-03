# Importing Library
import os
from flask import Flask, flash, request, redirect, url_for, render_template, Markup, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
import pandas as pd
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

from youtube_scrap import video_comments, get_video_metadata, get_video_data, get_video_comments_df


app = Flask(__name__, template_folder='templates')

@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')

@app.route("/scrap_youtube_comments", methods=["GET", "POST"])
def scrap_comments():
    if request.method == 'POST':
        link = request.form.get('link')
        link_extract = get_video_comments_df(link)
        link_extract = link_extract.to_dict('index')
        return link_extract
    
    return render_template("input_link.html")

if __name__ == '__main__':
    app.run(debug=True)