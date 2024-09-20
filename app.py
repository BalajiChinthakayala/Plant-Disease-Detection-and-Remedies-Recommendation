from __future__ import division, print_function
import os
import numpy as np
import sqlite3
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load the pre-trained model
model_path2 = 'models/model_xception.h5'
classes2 = {0: "Bacteria", 1: "Fungi", 2: "Nematodes", 3: "Normal", 4: "Virus"}
CTS = load_model(model_path2)

def model_predict2(image_path, model):
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image / 255
    image = np.expand_dims(image, axis=0)
    
    result = np.argmax(model.predict(image))
    
    if result == 0:
        return "Bacteria", "result.html"
    elif result == 1:
        return "Fungi", "result.html"
    elif result == 2:
        return "Nematodes", "result.html"
    elif result == 3:
        return "Normal", "result.html"
    elif result == 4:
        return "Virus", "result.html"

# Dummy user credentials for simplicity
USERS = {'user': 'pass'}

@app.route('/')
def index():
    return render_template('index.html')

# In-memory storage for user data
users = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists and the password matches
        if username in users and users[username] == password:
            return redirect(url_for('predict2'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the username already exists
        if username in users:
            return render_template('register.html', error='Username already exists')
        
        # Store user credentials in the in-memory dictionary
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/predict2', methods=['GET', 'POST'])
def predict2():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('predict2.html', error="No file part")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('predict2.html', error="No selected file")
        
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            pred, output_page = model_predict2(file_path, CTS)
            
            con = sqlite3.connect('remedies.db')
            cur = con.cursor()
            cur.execute("select `label` from data2 where `message` = ?", (pred,))
            remedies = cur.fetchall()
            
            if not remedies:
                remedies = ["No remedies found"]
                
            return render_template(output_page, pred_output=pred, remedies=remedies, img_src=UPLOAD_FOLDER + filename)
    
    return render_template('predict2.html')

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
