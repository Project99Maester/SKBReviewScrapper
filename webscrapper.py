from flask import Flask,request,redirect,url_for
from flask.helpers import flash
from flask_cors import cross_origin
from flask.templating import render_template
import requests
# from werkzeug.datastructures import ResponseCacheControl
# from requests.api import request
from SKBRS import RunThis
app=Flask(__name__)
app.secret_key='NeverMindNeverMindNeverMindNeverMind'
@app.route('/')
@cross_origin()
def HomePage():
    return render_template('HomePage.html')

@app.route('/results',methods=['POST'])
@cross_origin()
def Results():
    searchString=request.form['searchString']
    if searchString=='':
        flash("Please Enter a Search String!!")
        return redirect(url_for('HomePage'))
    results=RunThis(searchString=searchString)
    return render_template('Results.html',results=results[0],searchStr=searchString,Num=results[1])

@app.after_request
def add_security_headers(resp):
    # resp.headers['Content-Security-Policy']='default-src \'self\''
    resp.headers['Cache-Control']="no-cache, no-store, must-revalidate"
    return resp