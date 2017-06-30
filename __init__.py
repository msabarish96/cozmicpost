from flask import Flask ,url_for, Response, redirect, request,render_template,session,jsonify,make_response,json
import sqlalchemy
import Cookie
import datetime
import random
from sqlalchemy.orm import *
from requests import Request, Session
#from marshmallow_sqlalchemy import ModelSchema, fields
from marshmallow import Schema, fields
from sqlalchemy.ext.declarative import declarative_base

from flask_sqlalchemy import SQLAlchemy
import sys,os
import requests
from sqlalchemy import create_engine, Sequence
from sqlalchemy import Column,LargeBinary, Date, Integer, String, DateTime, VARCHAR, ForeignKey
import json
import uuid


app = Flask(__name__)

def connect(user, password, db, host ='localhost', port=5432):
    
    url = 'postgresql://postgres:postgres@localhost:5432/cozmic'
    url = url.format(user,password,host,port,db)
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    return con,meta


con, meta = connect('postgres','postgres','cozmic','localhost','5432')
Base = declarative_base()
Base.metadata.create_all(con)


def ses():
    Session = sessionmaker(bind=con)
    Session.configure(bind=con)
    session = Session()
    return session


class Userinfo(Schema):
    class Meta:
        fields = [
            'user_name',
    	    'user_id',
            'e_mail'
	]


class Users(Base):
    __tablename__ = 'users'

    user_id_seq = Sequence ('user_id_seq', metadata = Base.metadata)
    user_id = Column(Integer, user_id_seq, 
              server_default = user_id_seq.next_value(), unique = True)
    user_name = Column(VARCHAR(50))
    e_mail = Column(VARCHAR(50), primary_key = True)
    password = Column(VARCHAR(50))


class Friends_list(Base):
    __tablename__ = 'friends_list'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    user_id1 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    user_id2 = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    created_at = Column(DateTime(timezone = True), default = datetime.datetime.utcnow)
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
    def __repr__(self):
        return "<Sent_request(user_id1: '%s', user_id2: '%s')> "%(self.user_id1, self.user_id2)

 
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


class Statusinfo(Schema):
    class Meta:
		fields = [
		    'id',
		    'status_by',
		    'description',
		    'created_at',
		    'modified_at',
		    'privacy',
		    'image'
		]


class Likes(Base):
    __tablename__ = 'likes'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    liked_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
    		primary_key = True)
    def __repr__(self):
        return "<Likes(status_id: '%s', liked_by: '%s')> "%(self.status_id, self.liked_by, self.e_mail)


class Comments(Base):
    __tablename__ = 'comments'

    id_seq = Sequence('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    comment_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    comment = Column(VARCHAR(50))
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
		primary_key = True)
    def __repr__(self):
        return "<Comments(status_id: '%s', comment_by: '%s', comment: '%s')> "%(self.status_id, self.comment_by, self.comment)


class Tagging(Base):
    __tablename__ = 'tagging'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    status_id = Column(Integer, ForeignKey("status.id"), nullable = False)
    tagged_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    tag_to = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(),
    		primary_key = True)
    def __repr__(self):
        return "<Tagging(status_id: '%s', tagged_by: '%s', tag_to: '%s', id: '%s')> "%(self.status_id, self.tagged_by, self.tag_to, self.id)


class Share(Base):
    __tablename__ = 'share'

    id_seq = Sequence('id_seq', metadata = Base.metadata)
    shared_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    status_by = Column(Integer, ForeignKey("status.id"), nullable = False)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)
    def __repr__(self):
        return "<Share(shared_by: '%s', status_by: '%s', id: '%s')> "%(self.shared_by, self.status_by, self.id)

class Groups(Base):
    __tablename__ = 'groups'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    group_id = Column(Integer, id_seq, 
              server_default = id_seq.next_value(), unique = True)
    group_name = Column(VARCHAR(50), primary_key = True)
    admin = Column(Integer, ForeignKey("users.user_id"), nullable = False)
   
    def __repr__(self):
        return "<Groups(group_name: '%s', group_id: '%s', admin: '%s')> "%(self.group_name, self.group_id, self.admin)

class Groupsmembers(Base):
    __tablename__ = 'groupsmembers'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    id = Column(Integer, id_seq, 
              server_default = id_seq.next_value(), unique = True, primary_key = True)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable = False)
    member_id = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    accesstype = Column(VARCHAR(50), default = 'public')
    def __repr__(self):
        return "<Groupsmembers(group_id: '%s', member_id: '%s', accesstype: '%s')> "%(self.group_id, self.member_id, self.accesstype)

class Grouppost(Base):
    __tablename__ = 'grouppost'

    id_seq = Sequence ('id_seq', metadata = Base.metadata)
    id = Column(Integer, id_seq, server_default = id_seq.next_value(), 
		primary_key = True)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable = False)
    post_by = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    description = Column(VARCHAR(50), default = 'null')
    created_at = Column(DateTime(timezone = True), default = datetime.datetime.utcnow)
    modified_at = Column(DateTime(timezone = True), default = datetime.datetime.utcnow, onupdate = datetime.datetime.utcnow)
    image = Column(VARCHAR(50), default = 'null')

class Grouppostinfo(Schema):
    class Meta:
        fields = [
            'id',
            'group_id',
            'post_by',
            'description',
            'created_at',
            'modified_at',
            'image'
        ]



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
    if uid == None:
	    checkuser = session.query(Users).filter_by(e_mail = email).first()
	    if checkuser == None :
	        adduser = Users(user_name=username,e_mail=email,password=password)
        	session.add(adduser)
	        session.commit()
        	return 'welcome to cosmic, login to continue'
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
    username = request.args.get('username')
    logincheck = session.query(Users).filter_by(e_mail = email, password = password).first()
    uid = request.cookies.get('uuid')
    cookiecheck = session.query(Cookies).filter_by(uuid = uid).first()
    if uid == None:
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
			print "succesfully logged in" 
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
		return Userinfo(many = True).dumps(friendslistinfo).data

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
            return Userinfo(many = True).dumps(sendviews).data


@app.route('/cosmic/newsfeed', methods =['GET'])
def newsfeed():
    session = ses()
    resp = make_response()
    news = []
    newstag = []
    flist = []
    glist = []
    newsshare = []
    slist = []
    newsgroup = []
    tlist = []
    clist = []
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
            print newspost
            if newspost != None:
                comm = session.query(Comments).filter_by(status_id = newspost.id).all()
                news.append(newspost)
                news.append(comm)
            
        print  news
        # from tags

        tagfilter = session.query(Tagging).filter_by(tag_to = checkuser.user_id).all()
        for tags in tagfilter:
           # tagsinfo = session.query(Status).filter_by(status_id = tags).all()
            tlist.append(tagfilter.status_id)

        for n in tlist:

                newspost = session.query(Status).filter_by(status_id = n).all()
                newstag.append(newspost)
        print "news from tags"
        print newstag
        # from groups       
        groupfilter1 = session.query(Groupsmembers).filter_by(member_id = checkuser.user_id).all()
        groupfilter2 = session.query(Groups).filter_by(admin = checkuser.user_id).all()
        for member in groupfilter1:
            glist.append(member.group_id)
        for admin in groupfilter2:
            glist.append(admin.group_id)
            print glist
        for n in glist:
            newspot = session.query(Grouppost).filter_by(group_id = n).all()
            
            
            newsgroup.append(newspot)

        print newsgroup
        print glist
        # from share
        sharefilter = session.query(Share).filter_by(shared_by = checkuser.user_id).all()
        for n in sharefilter:
            slist.append(n.shared_by)
        for n in slist:    
            newspot = session.query(Status).filter_by(status_by = n).all()
            newsshare.append(newspot)
        print newsshare
        return jsonify({'groupost': Grouppostinfo(many = True).dumps(newspot).data,
                'status': Statusinfo(many = True).dumps(news).data})



@app.route('/cosmic/about',methods =['GET'])
def about():
    userprofile = []
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
	return "please login"
    else:
    	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
    	userinfo = session.query(Users).filter_by(user_id = userid.user_id).one()
    	#print(userinfo.__dict__)

	"""
	userprofile.append(userinfo)
	print userprofile
	sh = str(userprofile) 
	message = 'about the user\n'
	"""
	return Userinfo().dumps(userinfo).data
#	return message + userinfo.e_mail +  sh


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
         
@app.route('/cosmic/unfriend',methods = ['GET','POST'])
def unfriend():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	email = request.args.get('email')
	userinfo2 = session.query(Users).filter_by(e_mail = email).first()
	if userinfo2 == None:
		return "user not exist"
	else:
	  if userid.user_id == userinfo2.user_id:
		return redirect(url_for('about'))
	  else:
		friendlist = session.query(Friends_list).filter_by(user_id1 = userid.user_id, user_id2 = userinfo2.user_id).first()
		friendlist1 = session.query(Friends_list).filter_by(user_id1 = userinfo2.user_id, user_id2 = userid.user_id).first()
		if friendlist == None and friendlist1 == None:
			return "He is not a friend for you"
		elif friendlist1 == None:
			session.delete(friendlist)
			session.commit()
			return "You unfriend him"
		else:
			session.delete(friendlist1)
			session.commit()
			return "You unfriend him"


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
	
		print addstatus.__dict__
		session.commit()
		print addstatus.__dict__
		return {
		'succesfully post updated' : True,
		'Status' : Statusinfo().dumps(addstatus).data
		}
		
		#return  "successfully posted\n" + Statusinfo().dumps(addstatus).data 
		
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
		return "succesfully image uploaded" + str(addimage)

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
		if modifystatus.status_by == userid.user_id:
			modifystatus.description = description
			#modifystatus.modified_at = datetime.datetime.now(timezone = True)
			session.commit()
			return "succesfully post modified" + str(modifystatus)
		else:
			return "you dont have permission to modify"
	
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
		if modifyimage == None:
			return "Post id is wrong"
		else:
			if modifyimage.status_by == userid.user_id:
				modifyimage.image = imageurl
				session.commit()
				return "succesfully image modified" + str(modifyimage)
			else:
				return "You dont have permission to modify the post"

@app.route('/cosmic/postdelete',methods = ['GET','POST'])
def postdelete():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	statusid = request.args.get('postid')
	if statusid == None:
		return "nothing to post"
	else:
		deletestatus = session.query(Status).filter_by(id = statusid).first()
		if deletestatus == None:
			return "Post id is wrong"
		else:
			if deletestatus.status_by == userid.user_id:
				deletetags = session.query(Tagging).filter_by(status_id = statusid).all()
				for deletetag in deletetags:
					session.delete(deletetag)
					session.commit()
				deletelikes = session.query(Likes).filter_by(status_id = statusid).all()
				for deletelike in deletelikes:
					session.delete(deletelike)
					session.commit()
				deletecomments = session.query(Comments).filter_by(status_id = statusid).all()
				for deletecomment in deletecomments:
					session.delete(deletecomment)
					session.commit()
				session.delete(deletestatus)
				session.commit()
				return "succesfully post deleted" 
			else :
				return "you dont have permission to delete the post"




@app.route('/cosmic/post/like', methods =['GET','POST'])
def likes():
    session = ses()
    resp = make_response()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'log in'
    else:
        checkuser = session.query(Cookies).filter_by(uuid = cookievalue).one()
        print checkuser.user_id
	statusid = request.args.get('postid')
        postdetails = session.query(Status).filter_by(id = statusid).first()
      	if postdetails == None:
		return "the post id is wrong"
	else:
		likesdetails = session.query(Likes).filter_by(status_id = statusid, liked_by = checkuser.user_id).first()
		if likesdetails == None:
			addlikes = Likes(liked_by = checkuser.user_id, status_id = statusid)
		        session.add(addlikes)
			session.commit()
			return "you like the post"
		else:
			removelikes = session.query(Likes).filter_by(status_id = statusid,liked_by = checkuser.user_id).first()
			session.delete(removelikes)
			session.commit()

			return "likes removed from the post"

@app.route('/cosmic/post/share', methods =['GET','POST'])
def share():
    session = ses()
    resp = make_response()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'log in'
    else:
        checkuser = session.query(Cookies).filter_by(uuid = cookievalue).one()
        print checkuser.user_id
	statusid = request.args.get('postid')
        postdetails = session.query(Status).filter_by(id = statusid).first()
      	if postdetails == None:
		return "the post id is wrong"
	else:
		sharedetails = session.query(Share).filter_by(status_by = statusid, shared_by = checkuser.user_id).first()
		if sharedetails == None:
			if postdetails.status_by == checkuser.user_id:
				return "Your post cannot be shared by Yourself"
			else:
				addshare = Share(status_by = statusid, shared_by = checkuser.user_id)
			        session.add(addshare)
				session.commit()
				return "you shared the post" 
		else:
			removeshare = session.query(Share).filter_by(status_by = statusid,shared_by = checkuser.user_id).first()
			session.delete(removeshare)
			session.commit()

			return "Shared post is deleted"
@app.route('/cosmic/post/comments', methods =['GET','POST'])
def commentmethod():

    session = ses()
    resp = make_response()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'login'
    else:
        checkuser = session.query(Cookies).filter_by(uuid = cookievalue).first()
        comm = request.args.get('comm')
        status_id = request.args.get('status_id')
    
        if comm == None:
            return 'no comment still your opioin in your mind'
        else:
            commentdetail =  Comments(status_id = status_id, comment_by = checkuser.user_id, comment = comm )

            session.add(commentdetail)
            session.commit()
            return "commented"
    return resp
@app.route('/cosmic/post/removecomment')
def removecomment():
    session =ses()
    resp = make_response()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'please login this your valueble credintieal'
    else:
        checkuser = session.query(Cookies).filter_by(uuid = cookievalue).first()
        removecomm = request.args.get('removecommid')
        if removecomm == None:
            return "please enter removed comment"
        else:
            checkcomment = session.query(Comments).filter_by(id = removecomm).first()
            checkstatusowner = session.query(Status).filter_by(status_by = checkuser.user_id).first()
            print checkcomment
            print checkstatusowner
            if checkuser.user_id == checkcomment.comment_by:
                removedetails = session.query(Comments).filter_by(id = removecomm).first()
                session.delete(removedetails)
                session.commit()

                return "delete by commented person"
            elif checkuser.user_id == checkstatusowner.status_by:
                removedetails = session.query(Comments).filter_by(id = removecomm).first()
                session.delete(removedetails)
                session.commit()
                return "removed comment succefully"

            else:
                return "you can not delete this comment because your are not auth"


    return resp

@app.route('/cosmic/post/tags', methods =['GET','POST'])
def tagging():
    session = ses()
    resp = make_response()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None:
        return 'log in'
    else:
        checkuser = session.query(Cookies).filter_by(uuid = cookievalue).first()
        print checkuser.user_id
	tagemail = request.args.get('email')
	statusid = request.args.get('postid')
        postdetails = session.query(Status).filter_by(id = statusid).first()
      	tagidinfo = session.query(Users).filter_by(e_mail = tagemail).first()
	if postdetails == None:
		return "the post id is wrong"

	else:
	 if postdetails.status_by == checkuser.user_id:
		if tagidinfo == None:
			return "tagging friend not exist"
		else:
		 tagdetails = session.query(Tagging).filter_by(status_id = statusid, tag_to = tagidinfo.user_id).first()
		 friendlist = session.query(Friends_list).filter_by(user_id1 = checkuser.user_id, user_id2 = tagidinfo.user_id).first()
		 friendlist1 = session.query(Friends_list).filter_by(user_id1 = tagidinfo.user_id, user_id2 = checkuser.user_id).first()
		 if friendlist1 == None and friendlist == None :
			if checkuser.user_id == tagidinfo.user_id:
				if tagidinfo.e_mail == tagemail:
					return "self tagging is not available" 
				elif tagdetails == None:
					return "You are not tagged to this post"
				else :
					removetags = session.query(Tagging).filter_by(status_id= statusid, tag_to = tagidinfo.user_id)
					session.delete(removetags)
					session.commit()
					return "You are successfully removed from post"
			else:
				return "Tagging friend is not Your friend"
		 else:
			if tagdetails == None:
				addtags = Tagging(tagged_by = checkuser.user_id, status_id = statusid, tag_to = tagidinfo.user_id)
			        session.add(addtags)
				session.commit()
				return "succesfully friend is tagged to post" + str(addtags)
			else:
				
				removetags = session.query(Tagging).filter_by(status_id = statusid,tag_to = tagidinfo.user_id).first()
				session.delete(removetags)
				session.commit()
				return "succesfully Your friend is removed from the post"
		
	 else:
		return "You are not have permission to tag in post"

@app.route('/cosmic/group',methods = ['GET','POST'])
def group():
    session = ses()
    groupinfodetails = []
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	groupname = request.args.get('name')
	if groupname == None:
		return "enter group name"
	else:
		groupdetails = session.query(Groups).filter_by(group_name = groupname).first()
		if groupdetails == None:
			addgroup = Groups(group_name = groupname, admin = userid.user_id)
        		session.add(addgroup)
			session.commit()
			return "Group succesfully created" + str(addgroup)
		else:
			memberinfogroup = session.query(Groupsmembers).filter_by(group_id = groupdetails.group_id, member_id = userid.user_id).first()
			if groupdetails.admin == userid.user_id:
				groupinfodetail = session.query(Grouppost).filter_by(group_id = groupdetails.group_id).all()
				for grouppost in groupinfodetail:
					groupinfodetails.append(grouppost)
				print groupinfodetails
				return "Group post is shown" + str(groupinfodetails)
			elif memberinfogroup == None:
				memberrequest = Groupsmembers(group_id = groupdetails.group_id, member_id = userid.user_id)
				session.add(memberrequest)
				session.commit()
				return "Member request is sent to Group"

			else:
				groupsinfodetails = session.query(Grouppost).filter_by(group_id = groupdetails.group_id).all
				print groupsinfodetails
				for groupost in groupsinfodetails:
					groupinfodetails.append(groupost)
				print groupinfodetails
				return "Group post is shown" + str(groupinfodetails)


@app.route('/cosmic/groupdelete',methods = ['GET','POST'])
def groupdelete():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	groupname = request.args.get('name')
	if groupname == None:
		return "enter group name"
	else:
		groupdetails = session.query(Groups).filter_by(group_name = groupname).first()
		print groupdetails
		if groupdetails == None:
			return "No group in this name as you admin"
		else:
			if groupdetails.admin == userid.user_id:
				postdetails = session.query(Grouppost).filter_by(group_id = groupdetails.group_id).all()
				groupmembers = session.query(Groupsmembers).filter_by(group_id = groupdetails.group_id).all()
				for members in groupmembers:
				 session.delete(members)
				 session.commit()
				for posts in postdetails:
				 #print postdetails
				 session.delete(posts)
				 session.commit()
				session.delete(groupdetails)
				session.commit()
				return "Group is deleted successfully"

			else:
				return "You dont have permission to delete"

@app.route('/cosmic/group/remove',methods = ['GET','POST'])
def removemembers():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	membername = request.args.get('email')
	groupname = request.args.get('groupname')
	if membername == None:
		return "enter member name"
	elif groupname == None:
		return "enter groupname"
	else:
		groupdetails = session.query(Groups).filter_by(group_name = groupname).first()
		print groupdetails
		if groupdetails == None:
			return "No group in this name "
		else:
			memberdetails = session.query(Users).filter_by(e_mail = membername).first()
			if memberdetails == None:
				return "no user in the name in group"
			else:
				groupmemberdetails = session.query(Groupsmembers).filter_by(member_id = memberdetails.user_id, group_id = groupdetails.group_id).first()
				print groupmemberdetails
				if groupdetails.admin == memberdetails.user_id:
					return "you are the admin so you cannot remove yourself"
				elif groupdetails.admin != userid.user_id and groupmemberdetails.member_id != userid.user_id:
					return "you are not belong this group"
				elif groupmemberdetails == None:
					return "He is not a member of this group"
				else:
					postdetails = session.query(Grouppost).filter_by(group_id = groupdetails.group_id, post_by = memberdetails.user_id).all()
					session.delete(groupmemberdetails)
				 	for posts in postdetails:
				 	#print postdetails
				 	 session.delete(posts)
				 	 session.commit()
					session.commit()
					return "Group member is removed successfully"

			

@app.route('/cosmic/addgroup',methods = ['GET','POST'])
def addgroup():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	groupname = request.args.get('name')
	memberemail = request.args.get('email')
	if groupname == None:
		return "enter group name"
	else:
		memberdetails = session.query(Users).filter_by(e_mail = memberemail).first()
		if memberdetails == None:
			return "Member id is not found"
		else:
			groupdetails = session.query(Groups).filter_by(group_name = groupname, admin = userid.user_id).first()
			if groupdetails == None:
				return "No group is found"
			else:
				memberinfodetails = session.query(Groupsmembers).filter_by(group_id = groupdetails.group_id, member_id = memberdetails.user_id).first()
				print memberinfodetails
				if groupdetails.admin == memberdetails.user_id:
					return "You are already admin to group"
				elif memberinfodetails == None :
					addmember = Groupsmembers(group_id = groupdetails.group_id, member_id = memberdetails.user_id, accesstype = 'member')
					session.add(addmember)
					session.commit()
					return "member is successfully added to the group"
				else:
					groupmemberinfo = session.query(Groupsmembers).filter_by(group_id = groupdetails.group_id, member_id = memberdetails.user_id).first()
					if groupmemberinfo.accesstype == 'public' and groupmemberinfo.accesstype != 'member' :
						memberinfodetails.accesstype = "member"
						session.commit()
						return "Member request for group is accepted"
					else:
						return "member is already in the Group"

@app.route('/cosmic/group/post',methods = ['GET','POST'])
def addpost():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	groupname = request.args.get('name')
	text = request.args.get('text')
	image = request.args.get('image')
	if groupname == None:
		return "enter group name"
	else:
		groupdetails = session.query(Groups).filter_by(group_name = groupname).first()
		if groupdetails == None:
			return "No group is found"
		else:
			memberinfodetails = session.query(Groupsmembers).filter_by(group_id = groupdetails.group_id, member_id = userid.user_id, accesstype = 'member').first()
			if memberinfodetails == None and groupdetails.admin != userid.user_id:
				return "you dont have permission to post in group"
			else:
				if text == None:
					addimage = Grouppost(group_id = groupdetails.group_id, post_by = userid.user_id, image = image)
					session.add(addimage)
					session.commit()
					return "Image Url is posted to the group"
				elif image == None:
					addtext = Grouppost(group_id = groupdetails.group_id, post_by = userid.user_id, description = text)
					session.add(addtext)
					session.commit()
					return "Text is posted to the group"
				else :
					return "nothing to post"


@app.route('/cosmic/group/modifypost',methods = ['GET','POST'])
def modifypost():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	postid = request.args.get('postid')
	text = request.args.get('text')
	image = request.args.get('image')
	if  postid == None:
		return "enter post id"
	else:
		postdetails = session.query(Grouppost).filter_by(id = postid).first()
		if postdetails == None:
			return "No post is found"
		else:
			groupinfodetails = session.query(Groups).filter_by(group_id = postdetails.group_id).first()
			if postdetails.post_by != userid.user_id and groupinfodetails.admin != userid.user_id:
				return "you dont have permission to modify post in group"
			else:
				if text == None:
					postdetails.image = image
					session.commit()
					return "Image Url is modified successfully"
				elif image == None:
					postdetails.description = text
					session.commit()
					return "Text is modified successfully"
				else:
					return "Nothing to modify"


@app.route('/cosmic/group/deletepost',methods = ['GET','POST'])
def deletepost():
    session = ses()
    cookievalue = request.cookies.get('uuid')
    if cookievalue == None :
	return "please login"
    else :
	userid = session.query(Cookies).filter_by(uuid = cookievalue).first()
	postid = request.args.get('postid')
	if  postid == None:
		return "enter post id"
	else:
		postdetails = session.query(Grouppost).filter_by(id = postid).first()
		if postdetails == None:
			return "No post is found"
		else:
			groupinfodetails = session.query(Groups).filter_by(group_id = postdetails.group_id).first()
			if postdetails.post_by != userid.user_id and groupinfodetails.admin != userid.user_id:
				return "you dont have permission to delete post in group"
			else:
				session.delete(postdetails)
				session.commit()
				return "Post is deleted successfully"
				



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

