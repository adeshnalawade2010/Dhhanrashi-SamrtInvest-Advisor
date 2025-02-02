from  flask import Flask, render_template,request, jsonify, url_for,session,redirect,flash
import mysql.connector
import streamlit as st
import pandas as pd
import json
import requests
import re
from itsdangerous import URLSafeTimedSerializer
import hashlib
import datetime
import joblib
from sklearn.preprocessing import StandardScaler
from retrying import retry
from flask import make_response
from flask_mail import Mail , Message 
from email.mime.text import MIMEText
import smtplib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from random import randint
import functools
data=pd.read_csv('data.csv')

app = Flask(__name__,static_url_path='/static')
mail=Mail(app)
app.secret_key=''
app.config['MAIL_SERVER']=''
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']=''
app.config['MAIL_PASSWORD']=''
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
mail=Mail(app)
# otp=randint(000000,999999)
serializer = URLSafeTimedSerializer(app.secret_key)

def generate_token(email):
     return hashlib.sha256(email.encode()).hexdigest()

scaler = StandardScaler()
# from flask_mysqldb import MySQL
Connection=mysql.connector.connect(
     host='localhost',
     user='root',
     password='',
     database='mutual_fund'
          )

try:
    if Connection is not None and Connection.is_connected():
        db_info=Connection.get_server_info()
        print("conned to mysql successfully",db_info)
        
except Exception as e:
    print("Error occurs due to conn failed ",e)
finally:
    if Connection is not None and Connection.is_connected():
            print("conn is ready")
            Connection.close()
                
def get_db_connection():
    db={
        'user':'root',
        'password':'',
        'host':'localhost',
        'database':'mutual_fund',
        'raise_on_warnings':True}
    conn=mysql.connector.connect(**db)
    return conn

@app.route('/')
def login():
    return render_template('loginform.html')
@app.route('/' ,methods=['POST'])
def login1():
    message= ''
    if request.method=='POST' and 'email' in request.form and 'password' in request.form:
        email=request.form['email']
        password=request.form['password']
        conn= get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registration WHERE email=%s AND password=%s",(email,password))
        client=cursor.fetchone()
        cursor.close()
        conn.close()
        if client:
            session['loggedin']=True
            session['user']=client['user']
            session['name']=client['name']
            session['mobile']=client['mobile']
            session['email']=client['email']
            session['password']=client['password']
            session['confirmpassword']=client['confirmpassword']
            message='logged in successfully'
            return redirect(url_for('homepage'))
        else:
            flash('Please Enter correct email or password')
    return render_template('loginform.html')


def auth(view_func):
    @functools.wraps(view_func)    
    def decorated(*args, **kwargs):
        if 'email' not in session:
            flash("Please Login!!!!")
            return redirect('/')
        return view_func(*args, **kwargs)
    return decorated
            
@app.route('/profile')
@auth
def profile():
    if 'email' in session:
        user=session.get('user')
        name=session.get('name')
        mobile=session.get('mobile')
        email=session.get('email')
        return render_template('profile.html',user=user,name=name,mobile=mobile,email=email)       
    else:
         return "profile not found" if profile is None else redirect(url_for('login'))
@app.route('/registration',methods=['GET','POST'])

def register():
    message = ''
    if request.method=='POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        user=request.form['user']
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password']
        confirmpassword=request.form['confirmpassword']
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM registration WHERE email=%s",(email,))
        account=cursor.fetchone()
        cursor.close()
        
        if account:
            flash('Account already exists ! Please try another Email Address')
            return redirect(url_for('register'))
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',email):
            flash('Invalid Email Address')
            return redirect(url_for('register'))
        elif not re.match(r"^[A-Za-z\s'-]+$",name):
            flash("Please enter valid name!!!")
            return redirect(url_for('register'))
        elif not  all([user, name, mobile, password, confirmpassword]):
            flash('Please fill out the form!!')
            return redirect(url_for('register'))
        elif password != confirmpassword:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('register'))
        else:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute('INSERT INTO registration values(%s,%s,%s,%s,%s,%s)',(user,name,mobile,email,password,confirmpassword))
            conn.commit()
            cursor.close()
            conn.commit()
            conn.close()
            flash('You have successfully registered !')
            return redirect(url_for('login'))
    return render_template('registration.html', message=message)
@app.route('/forgot',methods=['GET','POST'])
def forgot_password():
    if request.method== 'POST':
        email=request.form['email']
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registration WHERE email=%s",(email,))
        user=cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            otp=randint(000000,999999)
            token=generate_token(email)
            conn=get_db_connection()
            cursor=conn.cursor(dictionary=True)
            cursor.execute("INSERT INTO password_reset_tokens (email, token, otp, created_at) VALUES (%s, %s, %s, %s)",
                           (email, token, otp, datetime.datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            # return redirect(url_for('reset_password' ,token = token))
            # sending gmail
            msg=Message('OTP',sender='aadinalawade4343@gmail.com',recipients=[email])
            msg.body=str(otp) + " is your Gmail verification code.This is one time password.Do not share with others."
            try:
                mail.send(msg)
                flash("An email containing OTP has been sent to your email address", 'success')
                return redirect(url_for('reset_password' ,token=token))
            except Exception as e:
                return f"Error sending email:{str(e)}"
                
        else:
            return "Email address not found"
    return render_template('forgot.html')
@app.route('/reset_password/<token>', methods=['GET', 'POST'])

def reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True,dictionary=True)  # Ensure cursor returns dictionary
    cursor.execute("SELECT * FROM password_reset_tokens WHERE token = %s", (token,))
    token_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if token_data:
        # expiration_time = token_data['created_at'] + datetime.timedelta(hours=1)
        expiration_time= token_data['created_at'] + datetime.timedelta(days=180)
        if datetime.datetime.now() > expiration_time:
            flash("Reset token has expired")
            return redirect(url_for('forgot_password'))
        if request.method == 'POST':
            
            user_otp=request.form['otp']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if token_data['otp']==int(user_otp):
                if new_password == confirm_password:
                    # hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE registration SET password = %s  , confirmpassword =%s WHERE email = %s",
                               (new_password,confirm_password, token_data['email']))
                    conn.commit()
                    cursor.close()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
                    conn.commit()
                    cursor.close()
                
                
                    # Don't forget to fetch or close this second cursor properly if needed
                    conn.close()
                    # Flash the success message
                    flash("Password has been reset successfully", 'success')
    
                  # Create a response object
                    response = make_response(redirect(url_for('login')))
    
                  # Set cache-control headers to prevent caching
                    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                    response.headers['Pragma']='no-cache'
                    response.headers['Expires']='0'
                    return response
                    # return jsonify({'message': 'Password has been reset successfully'}), 200    
                else:
                  return "Passwords do not match"
            else:
                return "OTP does not match. Please enter correct OTP"
        else:
            return render_template('reset_password.html',token=token)
    else:
        # flash("Invalid reset token",'error')
        return redirect(url_for('forgot_password'))

@app.route('/homepage')
@auth
def homepage():
    return render_template('homepage.html')
@app.route('/index')
@auth
def index():
            return render_template('index.html')
@app.route('/category/')
@auth
def category():
    conn=get_db_connection()
    mycursor=conn.cursor()
    mycursor.execute("SELECT DISTINCT category FROM mutual_funds_cleanup_dataset")
    category=mycursor.fetchall()
    mycursor.close()
    conn.close()
    return jsonify({'category':[sub[0] for sub in category]})
             

@app.route('/sub_category/',methods=['Post'])
def subcategory(): 
                #  category = request.form('category') #
                 conn=get_db_connection()
                 mycursor=conn.cursor()
                 category = request.form['category']
                 
                 mycursor.execute("SELECT DISTINCT sub_category FROM mutual_funds_cleanup_dataset WHERE category = %s", (category,))
                 sub_category=mycursor.fetchall()
                 mycursor.close()
                 conn.close()
                 return jsonify({'sub_category':[sub[0] for sub in sub_category]})
@app.route('/scheme_name/', methods=['Post'])
def scheme_name():
            conn=get_db_connection()
            cursor=conn.cursor()
            category = request.form['category']
            sub_category = request.form['sub_category']
            cursor.execute("SELECT DISTINCT scheme_name FROM mutual_funds_cleanup_dataset WHERE category=%s AND sub_category=%s", (category, sub_category))
            scheme_name = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'scheme_name': [sub[0] for sub in scheme_name]})
@app.route('/amc_name/', methods=['Post'])
def amc_name():
            conn=get_db_connection()
            cursor=conn.cursor()
            category = request.form.get('category')
            sub_category = request.form.get('sub_category')
            scheme_name= request.form.get('scheme_name')
            cursor.execute("select distinct amc_name from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s",(category,sub_category,scheme_name))
            amc_name = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'amc_name': [sub[0] for sub in amc_name]})
@app.route('/calculation')
@auth
def calculation():
            category = request.args.get('category')
            sub_category = request.args.get('sub_category')
            scheme_name= request.args.get('scheme_name')
            amc_name=request.args.get('amc_name')
            ammount=request.args.get('input_value')
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("select distinct min_sip from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s",(category,sub_category,scheme_name,amc_name))
            min_sip_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct min_lumpsum from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            min_lumpsum_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct expense_ratio from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            expense_ratio_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct fund_size_cr from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            fund_size_cr_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct fund_age_yr from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            fund_age_yr_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct sortino from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            sortino_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct alpha from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            alpha_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct sd from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            sd_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct beta from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            beta_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct sharpe from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            sharpe_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct risk_level from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            risk_level_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct rating from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            rating_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct returns_1yr from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            returns_1yr_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct returns_3yr from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            returns_3yr_res=cursor.fetchone()
            cursor.close()
            cursor=conn.cursor()
            cursor.execute("select distinct returns_5yr from mutual_funds_cleanup_dataset where category=%s and sub_category=%s and scheme_name=%s and amc_name=%s limit 1",(category,sub_category,scheme_name,amc_name))
            returns_5yr_res=cursor.fetchone()
            cursor.close()
            
            conn.close()
            min_sip=min_sip_res[0] if min_sip_res else 'Not available'
            min_lumpsum=min_lumpsum_res[0] if min_lumpsum_res else 'Not available'
            expense_ratio=expense_ratio_res[0] if expense_ratio_res else 'Not available'
            fund_size_cr=fund_size_cr_res[0] if fund_size_cr_res else 'Not available'
            fund_age_yr=fund_age_yr_res[0] if fund_age_yr_res else 'Not available'
            sortino=sortino_res[0] if sortino_res else 'Not available'
            alpha=alpha_res[0] if alpha_res else 'Not available'
            sd=sd_res[0] if sd_res else 'Not available'
            beta=beta_res[0] if beta_res else 'Not available'
            sharpe=sharpe_res[0] if sharpe_res else 'Not available'
            risk_level=risk_level_res[0] if risk_level_res else 'Not available'
            rating=rating_res[0] if rating_res else 'Not available'
            returns_1yr=returns_1yr_res[0] if returns_1yr_res else 'Not available'
            returns_3yr=returns_3yr_res[0] if returns_3yr_res else 'Not available'
            returns_5yr=returns_5yr_res[0] if returns_5yr_res else 'Not available'
            # calculating return ammount
            
            ammount = float(ammount)
            returns_1yr = float(returns_1yr)
            returns_3yr = float(returns_3yr)
            returns_5yr = float(returns_5yr)
            returns_1yr_amt=(ammount+((ammount*returns_1yr)/100))
            returns_3yr_amt=(ammount+((ammount*returns_3yr)/100))
            returns_5yr_amt=(ammount+((ammount*returns_5yr)/100))
            
            return render_template('calculation.html',category=category, sub_category=sub_category, scheme_name=scheme_name, amc_name=amc_name, ammount=ammount,min_sip=min_sip,min_lumpsum=min_lumpsum,expense_ratio=expense_ratio,fund_size_cr=fund_size_cr,fund_age_yr=fund_age_yr,sortino=sortino,alpha=alpha,sd=sd,beta=beta,sharpe=sharpe,risk_level=risk_level,rating=rating,returns_1yr_rate=returns_1yr,returns_3yr_rate=returns_3yr,returns_5yr_rate=returns_5yr,returns_1yr_amt=returns_1yr_amt,returns_3yr_amt=returns_3yr_amt,returns_5yr_amt=returns_5yr_amt)

@app.route('/dashborad')
@auth
def dashboard():
    return render_template('dashborad.html')
@app.route('/logout')
@auth
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page
    response=make_response(redirect(url_for('login')))
    #set cache control headers
    response.headers['Cache_control']='no-store,no-cache,must-revalidate,max-age=0'
    response.headers['Pragma']='no-cache'
    response.headers['Expires']='-1'
    response.cache_control.no_cache=True
    response.cache_control.no_store=True
    return response
@app.route('/prediction')
@auth
def prediction():
    return render_template('prediction.html')

@app.route('/output')
@auth
def output():
    return render_template('output.html')
model = joblib.load('model1.pkl')
label_encoders=joblib.load('label_encoder.pkl')

@app.route('/predict', methods=['POST','GET'])
@auth
def predict():
   
    
    input_data=[float(x) for x in request.form.values()]
    predict=[np.array(input_data)]
    
    # Make prediction
    prediction = model.predict(predict)

    # Convert prediction to a meaningful response
          
    category= label_encoders['category'].inverse_transform([int(prediction[0][0])])[0],
    sub_category= label_encoders['sub_category'].inverse_transform([int(prediction[0][1])])[0],
    scheme_name=label_encoders['scheme_name'].inverse_transform([int(prediction[0][2])])[0],
    amc_name= label_encoders['amc_name'].inverse_transform([int(prediction[0][3])])[0],
    returns_1yr= prediction[0][4],
    returns_3yr= prediction[0][5],
    returns_5yr= prediction[0][6],
        
        
    return render_template('output.html',category=category,sub_category=sub_category,scheme_name=scheme_name,amc_name=amc_name,returns_1yr=returns_1yr,returns_3yr=returns_3yr,returns_5yr=returns_5yr )
    
@app.route('/calculator')
@auth
def calculator():
    return render_template('calculator.html')
@retry(wait_fixed=2000, stop_max_attempt_number=3)
def fetch_news(category):
    API_KEY = ''
    url = f'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'in',
        'apiKey': API_KEY,
        'category': category
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['articles']
@app.route('/news/<category>')
@auth
def news(category):
    try:
        articles = fetch_news(category)
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch news: {e}")
        articles = []
    return render_template('news.html', articles=articles)

    
if __name__ == '__main__':
    app.secret_key=''
    app.run(debug=True)