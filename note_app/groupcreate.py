
from  flask import Flask ,url_for, Response, redirect, request,render_template,session,jsonify,make_response
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
import __init__


app = Flask(__name__)

@app.route('/note/groupcreate',methods = ['GET','POST'])
def groupcreate(Base):
    session = ses()
    response = make_response()
    groupname = request.args.get('groupname')
    username = request.cookies.get('username')
    groupcheck = session.query(login).filter_by(username = username).first
    if groupcheck == None:
        return 'please login or register '
    if groupcheck == request.cookies.get('username'):
        grab = session.query(group).filter_by(groupname = groupname).first
        if grab == None:
            adding = Group(groupname = groupname,username = username,userrole = 'admin')
            session.add(adding)
            session.commit()
        else:
            return 'inserted data'
    else:
        return 'group already  created'
    
