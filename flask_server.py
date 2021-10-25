import os
import flask

from flask import Flask, render_template, jsonify, request, redirect, flash, url_for, json
from werkzeug.utils import secure_filename


UPLOAD_PATH = 'static/query'
INDEX_PATH = 'indexstore'
QUERY = 'static/query'
ALLOWED_EXTENSIONS= {'png', 'jpg'}
N = -1

def createpaths():
    for dir in [UPLOAD_PATH, INDEX_PATH]:
        if not os.path.exists(dir):
            os.makedirs(dir)
createpaths()

import functions

def clearfiles():
    for dir in [UPLOAD_PATH]:
        for path in os.listdir(dir):
            full_path = os.path.join(dir, path)
            if os.path.isfile(full_path):
                os.remove(full_path)
clearfiles()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

query_pics = []
searched_image = ""
img_dir = ""
time = 0

functions.load_encodings(N)

app = Flask(__name__)

@app.route('/')
def upload():
    global query_pics
    global searched_image
    global img_dir
    global time
    send = query_pics
    path = ""
    query_pics = []
    if searched_image and img_dir:
        path = img_dir
        img_dir = ""
        searched_image = ""
    #searched_image = ""
    #paths = (os.listdir(UPLOAD_PATH))
    #print(paths)
    #paths = json.dumps(paths, separators=(',', ':'))

    print(path)
    return render_template('upload.html', searched_image=path, query_pics=send)

@app.route('/', methods=['POST'])
def upload_file():
    global searched_image
    for uploaded_file in request.files.getlist('file'):
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join(UPLOAD_PATH, uploaded_file.filename))
            searched_image = os.path.join(UPLOAD_PATH, uploaded_file.filename)
    return redirect(url_for('upload'))

@app.route('/query', methods=['POST'])
def query():
    global query_pics
    global searched_image
    global img_dir
    global time
    name = request.form['query_search']
    K = int(request.form['k_search'])
    time = 0

    if not searched_image:
        query_pics = functions.image_search(name, K, "rtree")
    else:
        query_pics = functions.analyze_and_return(searched_image, K, "rtree")
    if query_pics:
        img_dir = query_pics[0]
        searched_image = img_dir
        time = query_pics[2]
        query_pics = query_pics[1]
    return redirect(url_for('upload'))

if __name__ == "__main__":    
    app.run(debug=False)