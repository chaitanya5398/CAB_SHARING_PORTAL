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
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    ###This is the function to display the home page.
    ###1)Various trips,2)Notifications,3)Messages from other users.
    ###1)Various trips code.
    uname = db.auth_user(db.auth_user.id == auth.user_id).first_name
    response.flash = T("Cabshare Welcomes you!!!!")
    db(db.froms.id>0).delete()
    db(db.tos.id>0).delete()
    qr = (db.trip.total_tillnow < db.trip.max_people) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))
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
    Trips=db(qr).select(db.trip.ALL,limitby=(10*pageno,10*(pageno+1)+1))
    ###The code for the trips is done here.
    ###2) Notifications bar
    nqr = db.notification.rec_id == auth.user_id
    nans = db(nqr).select(limitby=(0,5),orderby=~db.notification.status|~db.notification.time_of)
    tt=[]
    name=[]
    ids=[]
    for k in nans:
        qrr = db.auth_user.id == k.send_id
        tt+=[ db.auth_user(qrr).Pp]
        name+=[db.auth_user(qrr).first_name]
        ids+=[db.auth_user(qrr).id]
    ###The notification related code ends here.
    ###The messages code.
    mqr = db.personal_message.rec_id == auth.user_id
    mans = db(mqr).select()
    ###The message code is done.
    return locals()

###This the ajax function for getting more notifications.The function returns the table and the buttons of navigation.
"""def ntfrl():
    print "hi"
    npg = request.args(0,cast=int)
    nqr = db.notification.rec_id == auth.user_id
    nans = db(nqr).select(limitby=(npg*5,(npg+1)*5+1),orderby=~db.notification.status|~db.notification.time_of)
    tt=[]
    name=[]
    ids=[]
    chk=0;#To display the next button only if needed.
    for k in nans:
        chk = chk+1
        qrr = db.auth_user.id == k.send_id
        tt+=[ db.auth_user(qrr).Pp]
        name+=[db.auth_user(qrr).first_name]
        ids+=[db.auth_user(qrr).id]
    ###Creating the div.
    cnt=0
    name=""
#    fields_one=[]
#    fields_two=[]
    for j in nans:
        name += 'TR(_class="one",'
        
        if j.type_of==1 or j.type_of==2:
            name+= "A(_href=URL('default','profile_view',args=ids[cnt])"  +",IMG(_src=URL('default','download',args=tt[cnt]),_alt='Name',_height='50px',_weight='50px'))"
    print name
#    DIV(_id="notif",A(_href=URL('default','ntf')),TABLE(_id="ntt",
#   TR()                                                    
#    ))
"""

###Just a simple page to show all the notifications in separate page.
def ntf():
    nqr = db.notification.rec_id == auth.user_id
    if len(request.args)>0:
        pageno=int(request.args[0])
    else:
        pageno=0
    nans = db(nqr).select(limitby=(pageno*10,(pageno+1)*10+1),orderby=~db.notification.status|~db.notification.time_of)
    tt=[]
    name=[]
    ids=[]
    for k in nans:
        qrr = db.auth_user.id == k.send_id
        tt+=[ db.auth_user(qrr).Pp]
        name+=[db.auth_user(qrr).first_name]
        ids+=[db.auth_user(qrr).id]
    return locals()

###This is the page which renders the form to float a trip.
@auth.requires_login()
def start_trip():
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
    else:
        response.flash = T("Please fill the Trip details")

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

###Afunction for users to join others' trip.
@auth.requires_login()
def join_trip():
    db(db.froms.id>0).delete()
    db(db.tos.id>0).delete()
    qr = (db.trip.total_tillnow < db.trip.max_people) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))
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
    Trips=db(qr).select(db.trip.ALL,limitby=(10*pageno,10*(pageno+1)+1))
    return locals()

###A function for users to serach for trips based on criteria
@auth.requires_login()
def after_search():
    if len(request.args)>4:
        pageno=int(request.args[4])
    else:
        pageno=0
    Trips=db((db.trip.total_tillnow-db.trip.max_people >= int(request.args[3])) ).select(db.trip.ALL,limitby=(10*pageno,10*(pageno+1)+1))
    return locals()

###A function to return a user's trips
@auth.requires_login()
def mytrips():
    if len(request.args)>0:
        pageno1=int(request.args[0])
    else:
        pageno1=0
    if len(request.args)>1:
        pageno2=int(request.args[1])
    else:
        pageno2=0
    if len(request.args)>2:
        pageno3=int(request.args[2])
    else:
        pageno3=0
    if len(request.args)>3:
        pageno4=int(request.args[3])
    else:
        pageno4=0
    qr1 = ((db.trip.date_of_trip < datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_end < datetime.datetime.now().time())))
    qr2 = (db.trip.total_tillnow < db.trip.max_people) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))
    PrevTripsasadmin=db((auth.user_id==db.trip.strid) & qr1).select(db.trip.ALL,limitby=(10*pageno3,10*(pageno3+1)+1))
    PendTripsasadmin=db((auth.user_id==db.trip.strid) & qr2).select(db.trip.ALL,limitby=(10*pageno1,10*(pageno1+1)+1))
    PrevTrips=db((auth.user_id==db.passenger.userid) & (db.passenger.tripid==db.trip.id) & qr1).select(db.trip.ALL,limitby=(10*pageno4,10*(pageno4+1)+1))
    PendTrips=db((auth.user_id==db.passenger.userid) & (db.passenger.tripid==db.trip.id) & qr2).select(db.trip.ALL,limitby=(10*pageno2,10*(pageno2+1)+1))
    return locals()

###A function to return form to search for trips
@auth.requires_login()
def form():
    form = SQLFORM.factory(Field('fro','string',label='From',requires=IS_NOT_EMPTY(),widget=SQLFORM.widgets.autocomplete(
request, db.froms.place, limitby=(0,10), min_length=1)),
                          Field('to','string',requires=IS_NOT_EMPTY(),widget=SQLFORM.widgets.autocomplete(
request, db.tos.place, limitby=(0,10), min_length=1)),
                          Field('Date','date',requires=IS_NOT_EMPTY()),
                          Field('Passengers','integer',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        response.flash="Please Fill the form."
        redirect(URL('after_search',args=[form.vars.fro,form.vars.to,form.vars.Date,form.vars.Passengers]))        
        print "hello"
    elif form.process().errors:
        print "sorry"
        response.flash="Errors in search query"
    else:
        print "atleast this."
        response.flash="Please fill all fields"
    return form

@auth.requires_login()
def voting():
    form=SQLFORM(db.voting)
    return locals()

###A function to view details of trip and user and to send him request to join him.
@auth.requires_login()
def particular():
    userid=auth.user_id
    trip=db.trip[request.args[0]]
    user=db.auth_user[trip.strid]
    flag=db((db.notification.send_id==userid) & (db.notification.tripid==trip.id)).select(db.trip.ALL)
    if len(flag)==1:
        flag=1
    else:
        flag=0
    return locals()

###A function to view passengers of trip and to accept requests to join trip.
@auth.requires_login()
def particularasadmin():
    trip=db.trip[request.args[0]]
    requests=db((db.notification.type_of==1) & (db.notification.rec_id==auth.user_id) & (db.notification.tripid==trip.id) & (db.notification.send_id==db.auth_user.id) & ((db.auth_user.id!=db.passenger.userid) | (trip.id!=db.passenger.tripid))).select(db.auth_user.ALL)
    accepted=db((trip.id==db.passenger.tripid) & (db.auth_user.id==db.passenger.userid)).select(db.auth_user.ALL)
    return locals()

###A computer generated notification
@auth.requires_login()
def create_notification():
    ###If first argument is 1,it is a requst to join the trip from sender to receiver.
    if int(request.args[0])==1:
        msg=request.args[4]+' has sent request to share the cab with you.'
        db.notification.insert(send_id=int(request.args[3]),rec_id=int(request.args[2]),tripid=int(request.args[1]),msg=msg,date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=1,status=0)
    elif int(request.args[0])==2:
        msg=request.args[4]+' has sent request to share the cab with you.'
        db.notification.insert(send_id=int(request.args[2]),rec_id=int(request.args[3]),tripid=int(request.args[1]),msg=msg,date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),type_of=2,status=0)
        db.passenger.insert(userid=int(request.args[3]),tripid=int(request.args[1]))
        db(db.trip.id==int(request.args[1])).update(total_tillnow=db.trip.total_tillnow+1)
    redirect(URL('index'))
    return locals()

@auth.requires_login()
def profile_view():
    usrid = request.args(0,cast=int)
    info  = db.auth_user(db.auth_user.id==usrid)
    return locals()
