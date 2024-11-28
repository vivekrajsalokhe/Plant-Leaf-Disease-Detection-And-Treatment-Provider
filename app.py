import os
from flask import Flask, redirect, render_template, request, url_for
from PIL import Image
import torchvision.transforms.functional as TF
import algorithms.CNN as CNN
import numpy as np
import torch
import pandas as pd
import sqlite3
from flask import make_response
import pdfkit

# load data
disease_info = pd.read_csv('source/disease_info.csv' , encoding='cp1252')
supplement_info = pd.read_csv('source/supplement_info.csv',encoding='cp1252')


model = CNN.CNN(39)    
model.load_state_dict(torch.load("models/plant_disease_recognizer.pt"))
model.eval()

def prediction(image_path):
    image = Image.open(image_path)
    image = image.resize((224, 224))
    input_data = TF.to_tensor(image)
    input_data = input_data.view((-1, 3, 224, 224))
    output = model(input_data)
    output = output.detach().numpy()
    index = np.argmax(output)
    return index    


app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact-us.html')

@app.route('/index')
def ai_engine_page():
    return render_template('index.html')

# @app.route('/mobile-device')
# def mobile_device_detected_page():
#     return render_template('mobile-device.html')

# Create a connection to the database
conn = sqlite3.connect('login.db')
c = conn.cursor()

# Create a table to store login details
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             email TEXT NOT NULL,
             username TEXT NOT NULL,
             password TEXT NOT NULL)''')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']
        
        # Check if the user exists in the database
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        
        if user:
            # User exists, redirect to home page
            return render_template('index.html')
        else:
            # User does not exist, show error message
            error = 'Invalid email or password'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        # Check if the email is already registered
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = c.fetchone()
        
        if existing_user:
            # Email is already registered, show error message
            error = 'Email already registered'
            return render_template('signup.html', error=error)
        else:
            # Insert the new user into the database
            c.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
            conn.commit()
            
            # User successfully registered, redirect to login page
            return render_template('login.html')
    
    return render_template('signup.html')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        image = request.files['image']
        filename = image.filename
        file_path = os.path.join('static/uploads', filename)
        image.save(file_path)
        print(file_path)
        pred = prediction(file_path)
        title = disease_info['disease_name'][pred]
        description =disease_info['description'][pred]
        prevent = disease_info['Possible Steps'][pred]
        image_url = disease_info['image_url'][pred]
        supplement_name = supplement_info['supplement name'][pred]
        supplement_image_url = supplement_info['supplement image'][pred]
        supplement_buy_link = supplement_info['buy link'][pred]
        
        # Generate PDF report using Jinja template
        rendered_template = render_template('submit.html', title=title, desc=description, prevent=prevent,
                                            image_url=image_url, pred=pred, sname=supplement_name,
                                            simage=supplement_image_url, buy_link=supplement_buy_link)
        
        # Create PDF file
        # pdf_file_path = os.path.join('static', 'reports', 'report.pdf')
        # pdfkit.from_string(rendered_template, pdf_file_path)
        
        # # Provide download link to the PDF file
        # download_report = url_for('static', filename='reports/report.pdf')
        
        return render_template('submit.html', title=title, desc=description, prevent=prevent,
                               image_url=image_url, pred=pred, sname=supplement_name,
                               simage=supplement_image_url, buy_link=supplement_buy_link)

@app.route('/market', methods=['GET', 'POST'])
def market():
    return render_template('market.html', supplement_image = list(supplement_info['supplement image']),
                           supplement_name = list(supplement_info['supplement name']), disease = list(disease_info['disease_name']), buy = list(supplement_info['buy link']))

if __name__ == '__main__':
    app.run(debug=True)
