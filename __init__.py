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
from sqlalchemy import Column, Date, Integer, String, DateTime
import json
import uuid
import groupcreate


app = Flask(__name__)

def connect(user, password, db, host ='localhost', port=5432):
    
    url = 'postgresql://postgres:postgres@localhost:5432/cozmicpost'
    url = url.format(user,password,host,port,db)
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    return con,meta


con, meta = connect('postgres','postgres','cozmicpost','localhost','5432')
Base = declarative_base()
Base.metadata.create_all(con)


def ses():
    Session = sessionmaker(bind=con)
    Session.configure(bind=con)
    session = Session()
    return session



class Users(Base):
    __tablename__ = 'users'

    user_id_seq = Sequence ('user_id_seq', metadata = Base.metadata)
    user_id = Column(Integer, user_id_seq, 
              server_default = user_id_seq.next_value(), unique = True)
    user_name = Column(VARCHAR(50))
    e_mail = Column(VARCHAR(50), primary_key = True)
    password = Column(VARCHAR(50))

    def __repr__(self):
        return "<Users(username= '%s', password ='%s', user_id = '%s', e_mail = '%s' )>"
			 %(self.user_name, self.password, self.user_id, self.e_mail)

class Friends_list(Base):
    __tablename__ = 'friends_list'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    user_id1 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    user_id2 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    created_at = Column(DateTime, default = datetime.datetime.uctnow)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)
    relation = Column(VARCHAR(50), default = 'friends')

class Sent_request(Base):
    __tablename__ = 'sent_request'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    user_id1 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    user_id2 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)
    
class Status(Base):
    __tablename__ = 'status'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)
    status_by = Column(Integer, ForeignKey("users.user_id"), nullabe = False)
    description = Column(VARCHAR(50), default = 'null')
    created_at = Column(DateTime, default = datetime.datetime.uctnow)
    modified_at = Column(dateTime, default = datetime.datetime.uctnow)
    privacy = Column(VARCHAR(50), default = 'public')
    image = Column(VARCHAR(50), default = 'null')

class Likes(Base):
    __tablename__ = 'likes'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    liked_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
    		primarykey = True)
    
class Comments(Base):
    __tablename__ = 'comments'

    id_seq = Sequence('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    comment_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    comment = Column(VARCHAR(50))
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
		primarykey = True)

class Share(Base):
    __tablename__ = 'share'

    id_seq = Sequence('id_seq', metadata = Base.metadata)
    shared_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    status_by = Column(Integer, ForeignKey("status.id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primarykey = True)

Base.metadata.create_all(con)
@app.route('/')
def index():
    user = request.cookies.get('user')
    resp=make_response()
    resp.set_cookie('user','the username')

@app.route('cosmic/signup', methods=['GET', 'POST'])

def signup():
        session = ses()
        username = request.args.get('username')
        email   = request.args.get('email')
        password = request.args.get('password')
        checkuser = session.query(users).filter_by(user_name = username).first()
        if checkuser == None :
            adduser = users(user_name=username,e_mail=email,password=password)
            session.add(adduser)
            session.commit()
            return 'welcome to cosmic'
        else:
            return 'user already exist'



@app.route('/cosmic/login',methods=['GET','POST'])
def login():

    session = ses()
    resp = make_response()

    email = request.args.get('email')
    
    password = request.args.get('password')
    
    print (username, password)
    
    logincheck = session.query(users).filter_by(e_mail = email).first()



    resp.set_cookie('username',user_name)

    
    if logincheck == None:
    
        return 'you are not accountant'
        
    else:
    
        if logincheck.password == password:
        
            return resp


        else:
            return 'password'
@app.route('/cosmic/logout',methods =['GET'])
def logout():
    resp = make_response()
    resp.set_cookie('username' , expires = 0)
    print "good bye"
    return resp

    

if __name__ == '__main__':


    
    app.run(debug=True,port = 8800)

