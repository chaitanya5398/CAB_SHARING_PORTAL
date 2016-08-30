# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import datetime
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

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
    if len(request.args)>0:
        pageno=int(request.args[0])
    else:
        pageno=0
    Trips=db((db.trip.total_tillnow < db.trip.max_people) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))).select(db.trip.ALL,limitby=(10*pageno,10*(pageno+1)+1))
    return locals()

###A function for users to serach for trips based on criteria
@auth.requires_login()
def after_search():
    if len(request.args)>4:
        pageno=int(request.args[4])
    else:
        pageno=0
    Trips=db((db.trip.max_people-db.trip.total_tillnow <= int(request.args[3])) & (db.trip.date_of_trip==request.args[2]) & (db.trip.from_place==request.args[0]) & (db.trip.to_place==request.args[1]) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))).select(db.trip.ALL,limitby=(10*pageno,10*(pageno+1)+1))
    return locals()

###A function to return a user's trips
@auth.requires_login()
def mytrips():
    if len(request.args)>0:
        pageno1=int(request.args[0])
        if len(request.args)>1:
            pageno2=int(request.args[1])
        else:
            pageno2=0
    else:
        pageno1=0
        pageno2=0
    PrevTrips=db(((auth.user_id==db.trip.strid) & ((db.trip.date_of_trip < datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_end < datetime.datetime.now().time())))) | ((auth.user_id==db.passenger.userid) & (db.passenger.tripid==db.trip.id) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time()))))).select(db.trip.ALL,limitby=(10*pageno1,10*(pageno1+1)+1))
    PendingTrips=db(((auth.user_id==db.trip.strid) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time())))) | ((auth.user_id==db.passenger.userid) & (db.passenger.tripid==db.trip.id) & ((db.trip.date_of_trip > datetime.date.today()) | ((db.trip.date_of_trip==datetime.date.today()) & (db.trip.start_up > datetime.datetime.now().time()))))).select(db.trip.ALL,limitby=(10*pageno2,10*(pageno2+1)+1))
    return locals()

###A function to return form to search for trips
@auth.requires_login()
def form():
    form = SQLFORM.factory(Field('fro','string',label='From',requires=IS_NOT_EMPTY(),widget=SQLFORM.widgets.autocomplete(
request, db.trip.from_place)),
                          Field('to','string',requires=IS_NOT_EMPTY()),
                          Field('Date','date',requires=IS_NOT_EMPTY()),
                          Field('Passengers','integer',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        redirect(URL('after_search',args=[form.vars.fro,form.vars.to,form.vars.Date,form.vars.Passengers]))
    elif form.process().errors:
        response.flash="Errors in search query"
    else:
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
    return locals()

###A computer generated notification
@auth.requires_login()
def create_notification():
    ###If first argument is 1,it is a requst to join the trip from sender to receiver.
    if int(request.args[0])==1:
        msg=request.args[4]+' has sent request to share the cab with you.'
        db.notification.insert(send_id=int(request.args[3]),rec_id=int(request.args[2]),msg=msg,date_of=datetime.date.today(),time_of=datetime.datetime.now().time(),status=0)
        redirect(URL('particular',args=[request.args[1]]))
    return locals()
