from flask import Flask ,url_for, Response, redirect, request,render_template,session,jsonify,make_response
import sqlalchemy
import Cookie
import datetime
import random
from sqlalchemy.orm import *
from requests import Request, Session
from marshmallow_sqlalchemy import ModelSchema, fields
from sqlalchemy.ext.declarative import declarative_base

from flask_sqlalchemy import SQLAlchemy
import sys,os
import requests
from sqlalchemy import create_engine, Sequence
from sqlalchemy import Column, Date, Integer, String, DateTime, VARCHAR, ForeignKey
import json
import uuid


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


class Userinfo(ModelSchema):
    class Meta:
         fields = [
             'username',
	     'user_id',
             'e_mail']


class Users(Base):
    __tablename__ = 'users'

    user_id_seq = Sequence ('user_id_seq', metadata = Base.metadata)
    user_id = Column(Integer, user_id_seq, 
              server_default = user_id_seq.next_value(), unique = True)
    user_name = Column(VARCHAR(50))
    e_mail = Column(VARCHAR(50), primary_key = True)
    password = Column(VARCHAR(50))

    def __repr__(self):
        return "<Users(username: '%s', user_id: '%s', e_mail: '%s')> "%(self.user_name, self.user_id, self.e_mail)

class Friends_list(Base):
    __tablename__ = 'friends_list'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    user_id1 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    user_id2 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    created_at = Column(DateTime(timezone = True), default = datetime.datetime.utcnow)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)
    relation = Column(VARCHAR(50), default = 'friends')
    def __repr__(self):
        return "<Friends_list(user_id1 = '%s', user_id2 = '%s' )>"%(self.user_id1, self.user_id2 )


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
    status_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    description = Column(VARCHAR(50), default = 'null')
    created_at = Column(DateTime(timezone = True), default = datetime.datetime.utcnow)
    modified_at = Column(DateTime(timezone = True), default = datetime.datetime.utcnow, onupdate = datetime.datetime.utcnow)
    privacy = Column(VARCHAR(50), default = 'public')
    image = Column(VARCHAR(50), default = 'null')

    def __repr__(self):
        return "<Status(id: '%s', status_by: '%s', description: '%s', created_at: '%s', modified_at: '%s', privacy: '%s', image: '%s')> "%(self.id, self.status_by, self.description, self.created_at, self.modified_at, self.privacy, self.image)


class Likes(Base):
    __tablename__ = 'likes'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    liked_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
    		primary_key = True)
    
class Comments(Base):
    __tablename__ = 'comments'

    id_seq = Sequence('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    comment_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    comment = Column(VARCHAR(50))
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
		primary_key = True)

class Share(Base):
    __tablename__ = 'share'

    id_seq = Sequence('id_seq', metadata = Base.metadata)
    shared_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    status_by = Column(Integer, ForeignKey("status.id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)

class Cookies(Base):
    __tablename__ = 'cookies'

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key = True)
    uuid = Column(VARCHAR(100), nullable = False, primary_key = True)

    def __repr__(self):
        return "<Cookies(user_id = '%s', uuid = '%s' )>"%(self.user_id, self.uuid)


Base.metadata.create_all(con)
@app.route('/')
def index():
    user = request.cookies.get('user')
    resp=make_response()
    resp.set_cookie('user','the username')

@app.route('/cosmic/signup', methods=['GET', 'POST'])

def signup():
    session = ses()
    username = request.args.get('username')
    email   = request.args.get('email')
    password = request.args.get('password')
    uid = request.cookies.get('uuid')
    if uuid == None:
	    checkuser = session.query(Users).filter_by(e_mail = email).first()
	    if checkuser == None :
	        adduser = Users(user_name=username,e_mail=email,password=password)
        	session.add(adduser)
	        session.commit()
        	return 'welcome to cosmic'
	    else:
        	return 'user already exist'
    else:
	return "already someone is logged in so just logout and try to sign up"
       
@app.route('/cosmic/login',methods=['GET','POST'])
def login():
    session = ses()
    resp = make_response()
    email = request.args.get('email')
    password = request.args.get('password')
    logincheck = session.query(Users).filter_by(e_mail = email, password = password).first()
    uid = request.cookies.get('uuid')
    cookiecheck = session.query(Cookies).filter_by(uuid = uid).first()
    if uuid == None:
	    if logincheck == None:
        	return 'you are not accountant'


	    else :
	  	if cookiecheck == None:
        		print logincheck
			u =str(uuid.uuid4())
			adduuid = Cookies(user_id = logincheck.user_id, uuid = u)
			session.add(adduuid)
			session.commit()
	    		resp.set_cookie('uuid',value=u)
			return resp
	    	else:
			resp.set_cookie('uuid', value = cookiecheck.uuid)
			print "user already logged in"
			return resp
    elif logincheck == None:
	return "already someone is logged in and just logout and try to log in"
    elif logincheck.user_id == cookiecheck.user_id:
	return "you are already logged in"
    	
    else:
	return "already someone is logged in and just logout and try to log in"  
     
@app.route('/cosmic/friendlist',methods = ['GET','POST'])
def list():
    friendslistid = []
    friendslistinfo = []
    session = ses()
    resp = make_response()
    uid = request.cookies.get('uuid')
    if uuid == None:
	return "please login"
    else:
	cookieuser = session.query(Cookies).filter_by(uuid = uid).one()
	print cookieuser.user_id
	friendlist1 = session.query(Friends_list).filter_by(user_id1 = cookieuser.user_id).all()
	friendlist2 = session.query(Friends_list).filter_by(user_id2 = cookieuser.user_id).all()
	print friendlist1
	print friendlist2
	if friendlist1 == None and friendlist == None:
		return "no friends still"
	else:
		for user2 in friendlist2:
			 friendslistid.append(user2.user_id1)
		for user3 in friendlist1:
			 friendslistid.append(user3.user_id2)
		print friendslistid
		for n in friendslistid:
			userinfo = session.query(Users).filter_by(user_id = n).first()
			friendslistinfo.append(userinfo)
		print "FRIENDS LIST",friendslistinfo
	return resp


@app.route('/cosmic/requestviews',methods = ['GET'])
def views():
    session = ses()
    resp = make_response()
    viewlist = []
    sendviews = []
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'log in dude'
    else:
        checkuuid = session.query(Cookies).filter_by(uuid = cookievalue).first()
        view = session.query(Sent_request).filter_by(user_id1 = checkuuid.user_id).all()
        print view
        if view == None:
            return "no request"
        else:
            for person in view:
                viewlist.append(person.user_id2)
            print viewlist
            for username in viewlist:
                userinfo = session.query(Users).filter_by(user_id = username).first()
                sendviews.append(userinfo)
            print sendviews
            return resp


@app.route('/cosmic/newsfeed', methods =['GET'])
def newsfeed():
    session = ses()
    resp = make_response()
    news = []
    flist = []
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'log in'
    else:
        checkuser = session.query(Cookies).filter_by(uuid = cookievalue).one()
        print checkuser.user_id
        friendlist1 = session.query(Friends_list).filter_by(user_id1 = checkuser.user_id).all()
        friendlist2 = session.query(Friends_list).filter_by(user_id2 = checkuser.user_id).all()
        
        for user1 in friendlist1:
            flist.append(user1.user_id2)
            for user2 in friendlist2:
                flist.append(user2.user_id1)

                for n in flist:
                    
                    newspost = session.query(Status).filter_by(status_by = n).first()
                    news.append(newspost)
                print news
    return resp    



@app.route('/cosmic/about',methods =['GET'])
def about():
    userprofile = []
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
	return "please login"
    else:
    	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
    	userinfo = session.query(Users).filter_by(user_id = userid.user_id).first()
    	print userinfo
	userprofile.append(userinfo)
	print userprofile
	return {
             'userinfo': Userinfo(
                 many=True).dumps(userinfo).data
                 }
 


@app.route('/cosmic/sentrequest',methods = ['GET','POST'])
def sentrequest():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	req_email = request.args.get('sentto')
	userinfo2 = session.query(Users).filter_by(e_mail = req_email).first()
	if userinfo2 == None:
		return "user not exist"
	else:
	  if userid.user_id == userinfo2.user_id:
		return redirect(url_for('about'))
	  else:
		friendlist = session.query(Friends_list).filter_by(user_id1 = userid.user_id, user_id2 = userinfo2.user_id).first()
		friendlist1 = session.query(Friends_list).filter_by(user_id1 = userinfo2.user_id, user_id2 = userid.user_id).first()
		if friendlist == None and friendlist1 == None:
			sentreq = session.query(Sent_request).filter_by(user_id1 = userid.user_id, user_id2 = userinfo2.user_id).first()
			sentreq1 = session.query(Sent_request).filter_by(user_id1 = userinfo2.user_id, user_id2 = userid.user_id).first()
			if sentreq == None and sentreq1 == None:
				adduser = Sent_request(user_id1=userid.user_id,user_id2=userinfo2.user_id)
        			session.add(adduser)
	        		session.commit()
				return "request sent"
			else :
				if sentreq == None:
					return "request from his pending for Your acceptance"
				else :
					return "already you sent a request which is in pending"
		else :
			return "already you are friends"

        
@app.route('/cosmic/confirm',methods = ['GET','POST'])
def confirm():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	accept_email = request.args.get('accept')
	userinfo2 = session.query(Users).filter_by(e_mail = accept_email).first()
	if userinfo2 == None:
		return "user not exist"
	else:
	  if userid.user_id == userinfo2.user_id:
		return redirect(url_for('about'))
	  else:
		friendlist = session.query(Friends_list).filter_by(user_id1 = userid.user_id, user_id2 = userinfo2.user_id).first()
		friendlist1 = session.query(Friends_list).filter_by(user_id1 = userinfo2.user_id, user_id2 = userid.user_id).first()
		if friendlist == None and friendlist1 == None:
			sentreq1 = session.query(Sent_request).filter_by(user_id1 = userinfo2.user_id, user_id2 = userid.user_id).first()
			if sentreq1 == None:
				return "There is no friend request from this id"
			else :
				adduser = Friends_list(user_id1=userid.user_id,user_id2=userinfo2.user_id)
				delsentrequest = session.query(Sent_request).filter_by(user_id1 = userinfo2.user_id, user_id2 = userid.user_id).first()
        			session.add(adduser)
				session.delete(delsentrequest)
	        		session.commit()
				return "request accepted"
		else :
			return "already you are friends"
 
@app.route('/cosmic/post/text',methods = ['GET','POST'])
def text():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	description = request.args.get('desc')
	if description == None:
		return "nothing to post"
	else:
		addstatus = Status(status_by = userid.user_id, description = description)
        	session.add(addstatus)
		session.commit()
		return "succesfully post updated"
		
@app.route('/cosmic/post/image',methods = ['GET','POST'])
def image():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	imageurl = request.args.get('url')
	if imageurl == None:
		return "nothing to post"
	else:
		addimage = Status(status_by = userid.user_id, image = imageurl)
	        session.add(addimage)
		session.commit()
		return "succesfully image uploaded"

@app.route('/cosmic/post/modifytext',methods = ['GET','POST'])
def modifytext():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	description = request.args.get('modify')
	statusid = request.args.get('postid')
	if description == None:
		return "nothing to post"
	else:
		modifystatus = session.query(Status).filter_by(id = statusid).first()
		print modifystatus
		modifystatus.description = description
		#modifystatus.modified_at = datetime.datetime.now(timezone = True)
		session.commit()
		return "succesfully post modified"
	
@app.route('/cosmic/post/modifyimage',methods = ['GET','POST'])
def modifyimage():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	imageurl = request.args.get('modify')
	statusid = request.args.get('postid')
	if imageurl == None:
		return "nothing to post"
	else:
		modifyimage = session.query(Status).filter_by(id = statusid).first()
		modifyimage.image = imageurl
		#modifyimage.modified_at = datetime.datetime.now(timezone = True)
		session.commit()
		return "succesfully image modified"
	
@app.route('/cosmic/logout',methods =['GET'])
def logout():
    session = ses()
    resp = make_response()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "you are not logged in for logout"
    else:
	    deletecookie = session.query(Cookies).filter_by(uuid = cookievalue).first()
	    resp.set_cookie('uuid' , expires = 0)
	    session.delete(deletecookie)
	    session.commit()
	    print "good bye"
	    return resp

    

if __name__ == '__main__':


    
    app.run(debug=True,port = 8800)

