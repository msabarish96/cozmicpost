from flask import Flask ,url_for, Response, redirect, request,render_template,session,jsonify,make_response
import sqlalchemy
import Cookie
import datetime
import random
from sqlalchemy.orm import *
from requests import Request, Session

from sqlalchemy.ext.declarative import declarative_base

from flask_sqlalchemy import SQLAlchemy
import sys,os
import requests
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String
import json
import uuid
import groupcreate


app = Flask(__name__)

def connect(user, password, db, host ='localhost', port=5432):
    
    url = 'postgresql://harish:harish@localhost:5432/test'
    url = url.format(user,password,host,port,db)
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    return con,meta


con, meta = connect('harish','harish','test','localhost','5432')
Base = declarative_base()
Base.metadata.create_all(con)


def ses():
    Session = sessionmaker(bind=con)
    Session.configure(bind=con)
    session = Session()
    return session



class User(Base):
    __tablename__ = 'login'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    def __repr__(self):
        return "<User(username= '%s', password ='%s' )>" %(self.username, self.password)

class Group(Base):
    __tablename__ = 'group'

    group_id = Column(Integer, primary_key=True)
    groupname = Column(String)
    username = Column(String)
    userrole = Column(String)

    def __repr__(self):
                            
        return "<Group(groupname= '%s', username ='%s', userrole = '%s' )>" %(self.groupname, self.username,self.userrole)




Base.metadata.create_all(con)
@app.route('/')
def index():
    user = request.cookies.get('user')
    resp=make_response()
    resp.set_cookie('user','the username')

@app.route('/note/User', methods=['GET', 'POST'])

def signup():
    session = ses()
    username = request.args.get('user')
    password = request.args.get('password')
    oue = session.query(User).filter_by(username = username).first()
    if oue == None :
        id_user = User(username= username, password=password)
        session.add(id_user)
        session.commit()
        return 'logged in'
    else:
        return 'user already exist'

@app.route('/note/login',methods=['GET','POST'])
def login():
    
    session = ses()
    resp = make_response()
    

    username = request.args.get('user') 
    password = request.args.get('password')
    print (username, password)
    usercheck = session.query(User).filter_by(username = username).first()

    resp.set_cookie('user',username) 
    
    if usercheck == None:
        return 'you are not costumer'
    else:
        if usercheck.password == password:
            return resp
        
        else:
            return 'password not currect'

@app.route('/note/logout',methods =['GET'])
def logout():
    resp = make_response()
    resp.set_cookie('user' , expires = 0)
    print "good bye"
    return resp
    

if __name__ == '__main__':


    
    app.run(debug=True,port = 8800)

