from flask import Flask, render_template, request, url_for, redirect, flash, session
import boto3
import key_config as keys
import dynamodb_handler
import json
from boto3.dynamodb.conditions import Key, Attr
import urllib.parse

app = Flask(__name__)
app.secret_key = 'flask_server'

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id     = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name = keys.REGION_NAME,
)

@app.route('/')
def index():
    
    #create table below
    #dynamodb_handler.create_user_table()
    #return 'Table Created'
    
    #create bucket below to upload image
    #dynamodb_handler.create_bucket()
    #return "bucket created"
    
    return render_template('sign-up.html')

@app.route('/login')
def login():
    messages = session.pop('flash_messages', [])
    return render_template('login.html', messages=messages)
    

@app.route('/redirect')
def redirect_to_sign_in():
    return redirect(url_for('index'))
    
    
@app.route('/signup', methods=['post'])
def signup():
    
    user_data = request.form.to_dict()
    dynamodb_handler.add_item_to_user_table(user_data['fullname'], int(user_data['registration_number']), user_data['email'], user_data['password'], user_data['degree'], (user_data['contact']), user_data['introduction'], user_data['gpa'], user_data['skills'])
    flash ("Registration completed successfully!")

    return redirect(url_for('login'))


@app.route('/check', methods=['post'])
def check():
    email = request.form["email"]
    login_password = request.form["password"]
    
    table = dynamodb.Table('users')
    
    
    response = table.query(
        KeyConditionExpression=Key("email").eq(email)
    )
    
    if response['Items']:
        items = response['Items']
        fullname = items[0]['fullname']
        registration_number = items[0]['registration_number']
        password = items[0]['password']
        degree = items[0]['degree']
        contact = items[0]['contact']
        introduction = items[0]['introduction']
        gpa = items[0]['GPA']
        skills = items[0]['skills']
        profile_image = items[0]['profile_image']
    else:
        flash("User not found try again!")
        return redirect(url_for("login"))
    
    if login_password == password:
        return render_template('update.html', email=email, password=password, fullname=fullname, registration_number=registration_number, 
        degree=degree, contact=contact, introduction=introduction, gpa=gpa, skills=skills, profile_image=profile_image)
    else:
        flash ("Invalid password try again!")
        return redirect(url_for("login"))
        

@app.route('/upload', methods=['POST', 'PUT'])
def upload_user_profile_image():   
    
    filename, bucket_name = dynamodb_handler.upload_image()
    
    encoded_object_key = urllib.parse.quote(filename)
    object_url = f"https://{bucket_name}.s3.amazonaws.com/{encoded_object_key}"
    
    dynamodb_handler.update_image_url(object_url)
    
    email = request.form['email']
    
    profile = dynamodb_handler.get_user_details(email)
    fullname = profile["fullname"]
    email = profile["email"]
    registration_number = profile["registration_number"]
    password = profile["password"]
    degree = profile["degree"]
    contact = profile["contact"]
    introduction = profile["introduction"]
    gpa = profile["GPA"]
    skills = profile["skills"]
    profile_image = profile["profile_image"]
    
    return render_template('update.html', email=email, password=password, fullname=fullname, registration_number=registration_number, 
    degree=degree, contact=contact, introduction=introduction, gpa=gpa, skills=skills, profile_image=profile_image)


    
@app.route('/update/<string:email>', methods=['PUT'])
def update_profile(email):
    data = request.get_json()
    
    dynamodb_handler.update_user_profile(email,data)
    
    profile = dynamodb_handler.get_user_details(email)
    fullname = profile["fullname"]
    email = profile["email"]
    registration_number = profile["registration_number"]
    password = profile["password"]
    degree = profile["degree"]
    contact = profile["contact"]
    introduction = profile["introduction"]
    gpa = profile["GPA"]
    skills = profile["skills"]
    profile_image = profile["profile_image"] 
        
    return render_template('update.html', email=email, password=password, fullname=fullname, registration_number=registration_number, 
    degree=degree, contact=contact, introduction=introduction, gpa=gpa, skills=skills, profile_image=profile_image)

    
@app.route('/view/<int:registration_number>', methods=['GET'])
def public_profile_view(registration_number):
    profile = dynamodb_handler.get_user_profile(registration_number)
    
    fullname = profile["fullname"]
    email = profile["email"]
    registration_number = profile["registration_number"]
    degree = profile["degree"]
    contact = profile["contact"]
    introduction = profile["introduction"]
    GPA = profile["GPA"]
    skills = profile["skills"]
    profile_image = profile["profile_image"]
        
    return render_template("view.html", fullname=fullname, email=email, registration_number=registration_number, degree=degree, contact=contact, introduction=introduction, GPA=GPA, skills=skills, profile_image=profile_image)

        

if __name__ == '__main__':
    app.run()
    
    
    
