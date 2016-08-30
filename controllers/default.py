# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import datetime
@auth.requires_login()
def index():
    reqdate=(datetime.datetime.now() - datetime.timedelta(days=1)).date()
    flag=db((db.trip.date_of_trip==reqdate) & (db.notification.tripid==db.trip.id) & (db.notification.type_of==3)).select(db.notification.ALL)
    if len(flag)==0:
        flag=db(db.trip.date_of_trip==reqdate).select()
        for i in flag:
            flag1=db(db.passenger.tripid==i.id).select()
            for j in flag1:
                db.notification.insert(send_id=i.strid,rec_id=j.userid,tripid=i.id,msg="Please give feedback",date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=3,status=0,flag_of=0,no_of=0)
            db.notification.insert(send_id=1,rec_id=i.strid,tripid=i.id,msg="Please give feedback",date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=3,status=0,flag_of=0,no_of=0)
    form  = SQLFORM(db.trip)
    if form.process().accepted: 
        #Updating the the till now parameters.
        ppl = form.vars.people_start;
        bags  = form.vars.bags_start;
        currid = form.vars.id;
        tmp = db.trip(db.trip.id == currid)
        tmp.update_record(total_tillnow=ppl,bags_till_now=bags)
        #Updating the number of trips for the user.
        qr = db.auth_user.id==auth.user_id;
        nt = 1 + int(db.auth_user(qr).trips_no);
        db.auth_user(qr).update_record(trips_no=nt);
        response.flash = T("Your trip has been registered")
    elif form.errors:
        response.flash = T("Trip details have errors")
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    form1 = SQLFORM.factory(Field('fro','string',label='From',requires=IS_NOT_EMPTY(),widget=SQLFORM.widgets.autocomplete(
request, db.froms.place, limitby=(0,10), min_length=1)),
                          Field('to','string',requires=IS_NOT_EMPTY(),widget=SQLFORM.widgets.autocomplete(
request, db.tos.place, limitby=(0,10), min_length=1)),
                          Field('Date','date',requires=IS_NOT_EMPTY()),
                          Field('Passengers','integer',requires=IS_NOT_EMPTY()))
    if form1.process().accepted:
        redirect(URL('after_search',args=[form1.vars.fro,form1.vars.to,form1.vars.Date,form1.vars.Passengers]))
    elif form1.process().errors:
        response.flash="Errors in search query"
    ###The form porion of the code is done and now the main elements.
    ###This is the function to display the home page.
    ###1)Various trips,2)Notifications,3)Messages from other users.
    ###1)Various trips code.
    uname = db.auth_user(db.auth_user.id == auth.user_id).first_name
    response.flash = T("Cabshare Welcomes you!!!!")
    db(db.froms.id>0).delete()
    db(db.tos.id>0).delete()
    qr = (db.trip.strid!=auth.user_id) & (db.trip.total_tillnow < db.trip.max_people) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))
    fa = db(qr).select(db.trip.from_place,db.trip.to_place)
    froms=[]
    tos=[]
    for i in fa:
        froms+=[i.from_place]
        tos+=[i.to_place]
    froms = list(set(froms))
    tos = list(set(tos))
    for i in froms:
        db.froms.insert(place=i)
    for i in tos:
        db.tos.insert(place=i)
    if len(request.args)>0:
        pageno=int(request.args[0])
    else:
        pageno=0
    Trips=db(qr).select(db.trip.ALL,limitby=(7*pageno,7*(pageno+1)+1))
    ###The code for the trips is done here.
    ###2) Notifications bar
    nqr = db.notification.rec_id == auth.user_id
    nans = db(nqr).select(orderby=db.notification.status|~db.notification.date_of|~db.notification.time_of)
    tt=[]
    name=[]
    ids=[]
    ###make the status one when he visits the page. 
    for k in nans:
        qrr = db.auth_user.id == k.send_id
        tt+=[db.auth_user(qrr).Pp]
        name+=[db.auth_user(qrr).first_name]
        ids+=[db.auth_user(qrr).id]
    ###The notification related code ends here.
    ###The messages code.
    mqr = db.personal_message.rec_id == auth.user_id
    mans = db(mqr).select()
    mn=[];tm=[];dt=[]
    #for j in mans:
    ###The message code is done.
    return locals()

###This is a function to render the feedback form and get feedback
@auth.requires_login()
def fill_feedback():
    tid = request.args(0,cast=int)
    qr = db.trip.id == tid
    trip = db.trip(qr)
    main = trip.strid
    others  = db(db.passenger.tripid==tid).select()
    num = trip.total_tillnow
    return locals()
###This is a background Java-script function to accept and reject feedback and to create notifications with regard to it.
@auth.requires_login()
def form_feed():
    k = request.args(0,cast=int)
    print k
    if k==1:
        print "hi"
        cmt=request.vars.cmt
        print cmt
        rt= int(request.vars.rating)
        cid= int(request.vars.dummy)
        tid= int(request.vars.tid)
        print tid,rt,cid
        db.voting.insert(voterid=auth.user_id,candid=cid,tripid=tid,time_of=datetime.datetime.now().time(),date_of=datetime.date.today(),rating=rt,comm=cmt,fill_status=1)
        print "The vote has been inserted."
        #creating a view feedback-notification.
        db.notification.insert(send_id=auth.user_id,rec_id=cid,tripid=tid,msg="hello",date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=4,status=0,flag_of=0,no_of=0)
        print "Notification is inserted."
        #updating the rating of the person and the votes_no.
        rate =  db.auth_user(db.auth_user.id == cid).depend_rate
        novot = db.auth_user(db.auth_user.id == cid).votes_no
        sumt = int(novot*rate)
        ns = sumt + rt;nnvt = int(novot + 1)
        nrt = ns/nnvt;
        db.auth_user(db.auth_user.id == cid).update_record(depend_rate=nrt,votes_no=nnvt)
        print "The user is updated."
    elif k==0:
        cid= request.vars.dummy;tid=request.vars.tid
        db.voting.insert(voterid=auth.user_id,candid=cid,tripid=tid,time_of=datetime.datetime.now().time(),date_of=datetime.date.today(),fill_status=-1)
        return k

###This is a page to display the feedback given by others for a trip.
def view_feedback():
    return locals()

###Just a simple page to show all the notifications in separate page.
def ntf():
    nqr = db.notification.rec_id == auth.user_id
    if len(request.args)>0:
        pageno=int(request.args[0])
    else:
        pageno=0
    nans = db(nqr).select(limitby=(pageno*7,(pageno+1)*7+1),orderby=~db.notification.status|~db.notification.time_of)
    tt=[];name=[];ids=[]
    for k in nans:
        qrr = db.auth_user.id == k.send_id
        tt+=[ db.auth_user(qrr).Pp]
        name+=[db.auth_user(qrr).first_name]
        ids+=[db.auth_user(qrr).id]
    return locals()

###This is a simple function called by ajax to just change the status of the notifiacation.
def nvis():
    #print "hi" + request.args[0] 
    nid = request.args(0,cast=int)
    qr = db.notification.id == nid
    db.notification(qr).update_record(status=1)
    #print "hello"
    return locals()


###Theese are the functions by default...
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

###A function to manage the users.
#def manage():

###A function for users to serach for trips based on criteria
@auth.requires_login()
def after_search():
    if len(request.args)>4:
        pageno=int(request.args[4])
    else:
        pageno=0
    Trips=db((db.trip.max_people-db.trip.total_tillnow >= int(request.args[3])) & (db.trip.strid!=auth.user_id) & (db.trip.date_of_trip==request.args[2]) & (db.trip.to_place==request.args[1]) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))).select(db.trip.ALL,limitby=(7*pageno,7*(pageno+1)+1))
    #& (db.trip.from_place==request.args[0]) 
    return locals()

###A function to return a user's trips
@auth.requires_login()
def PendingTrips():
    if len(request.args)>0:
        pageno1=int(request.args[0])
    else:
        pageno1=0
    if len(request.args)>1:
        pageno2=int(request.args[1])
    else:
        pageno2=0
    qr2 = ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))
    PendTripsasadmin=db((auth.user_id==db.trip.strid) & qr2).select(db.trip.ALL,limitby=(7*pageno1,7*(pageno1+1)+1))
    PendTrips=db((auth.user_id==db.passenger.userid) & (db.passenger.tripid==db.trip.id) & qr2).select(db.trip.ALL,limitby=(7*pageno2,7*(pageno2+1)+1))
    return locals()

@auth.requires_login()
def PrevTrips():
    if len(request.args)>0:
        pageno1=int(request.args[2])
    else:
        pageno1=0
    if len(request.args)>1:
        pageno2=int(request.args[3])
    else:
        pageno2=0
    qr1 = ((db.trip.date_of_trip < datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_end < datetime.datetime.now().time())))
    PrevTripsasadmin=db((auth.user_id==db.trip.strid) & qr1).select(db.trip.ALL,limitby=(7*pageno1,7*(pageno1+1)+1))
    PrevTrips=db((auth.user_id==db.passenger.userid) & (db.passenger.tripid==db.trip.id) & qr1).select(db.trip.ALL,limitby=(10*pageno2,10*(pageno2+1)+1))
    return locals()

@auth.requires_login()
def voting():
    form=SQLFORM(db.voting)
    return locals()

###A function to view details of trip and user and to send him request to join him.
@auth.requires_login()
def particular():
    userid=auth.user_id
    trip=db.trip[request.args[0]]
    seT=[]
    i=0
    while i < (int(trip.max_people-trip.total_tillnow)):
        seT.append(i+1)
        i+=1
    form=SQLFORM.factory(Field('No_of_people','integer',requires=IS_IN_SET(seT)))
    user=db.auth_user[trip.strid]
    if form.process().accepted:
        redirect(URL('create_notification',args=[1,trip.id,trip.strid,userid,user.username,form.vars.No_of_people]))
    elif form.process().errors:
        response.flash="Enter a number less than vacant seats"
    flag=db((db.notification.send_id==userid) & (db.notification.tripid==trip.id)).select(db.trip.ALL)
    if len(flag)>0:
        flag=1
    else:
        flag=0
    return locals()

###A function to view passengers of trip and to accept requests to join trip.
@auth.requires_login()
def particularasadmin():
    trip=db.trip[request.args[0]]
    comments=db(db.tc.tid==trip.id).select(db.tc.ALL)
    qr=(db.notification.type_of==1) & (db.notification.tripid==trip.id) & (db.notification.flag_of==0) &(db.notification.send_id==db.auth_user.id)
    requests=db(qr).select(db.auth_user.ALL)
    notif=db(qr).select(db.notification.ALL)
    accepted=db((trip.id==db.passenger.tripid) & (db.auth_user.id==db.passenger.userid)).select(db.auth_user.ALL)
    return locals()

def particularwithcomm():
    curr=auth.user_id
    trip=db.trip[request.args[0]]
    starter=db.auth_user[trip.strid]
    comments=db(db.tc.tid==trip.id).select(db.tc.ALL)
    passengers=db((db.passenger.tripid==trip.id) & (db.passenger.userid==db.auth_user.id)).select(db.auth_user.ALL)
    return locals()

###A computer generated notification creating fucntion.
@auth.requires_login()
def create_notification():
    ###If first argument is 1,it is a requst to join the trip from sender to receiver.
    if int(request.args[0])==1:
        msg=request.args[4]+' has sent request to share the cab with you.'
        db.notification.insert(send_id=int(request.args[3]),rec_id=int(request.args[2]),tripid=int(request.args[1]),msg=msg,date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=1,status=0,flag_of=0,no_of=int(request.args[5]))
        redirect(URL('index'))
    elif int(request.args[0])==2:
        msg=request.args[2]+' has accepted you request.'
        db.notification.insert(send_id=int(request.args[2]),rec_id=int(request.args[3]),tripid=int(request.args[1]),msg=msg,date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=2,status=0,flag_of=0,no_of=int(request.args[5]))
        db.passenger.insert(userid=int(request.args[3]),tripid=int(request.args[1]),no_of=int(request.args[5]))
        db((db.notification.tripid==request.args[1]) & (db.notification.send_id==request.args[3]) & (db.notification.type_of==1)).update(flag_of=1)
        db(db.trip.id==int(request.args[1])).update(total_tillnow=db.trip.total_tillnow+request.args[5])
        redirect(URL('particularasadmin',args=[int(request.args[1])]))
    redirect(URL('PendingTrips'))
    return locals()

###A function called on clicking the profile pictures to see the profile details of the user.
@auth.requires_login()
def profile_view():
    usrid = request.args(0,cast=int)
    info  = db.auth_user(db.auth_user.id==usrid)
    qr = db.voting.candid == usrid
    cms = db(qr).select(orderby=~db.voting.time_of,limitby=(0,5))
    img=[];udrid=[];nms=[]
    cnt=0;ck=0
    for j in cms:
        ck = ck+1
        udrid +=[j.voterid]
        img+=[db.auth_user(db.auth_user.id == j.voterid).Pp]
        nms+=[db.auth_user(db.auth_user.id == j.voterid).first_name]
        print 'j'
        #        cmt+=[db.auth_user(db.auth_user.id == j.voterid).comm]
    return locals()

def myprofile():
    redirect("http://127.0.0.1:8000/Cabshare/default/user/profile?_next=/Cabshare/default/myprofile")
    return locals()
