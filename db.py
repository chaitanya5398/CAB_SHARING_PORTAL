# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
###All the imports are start here
from gluon.tools import Auth, Service, PluginManager
from applications.Cabshare.modules.countries import *

###and the imports end here.

auth = Auth(db)
service = Service()
plugins = PluginManager()

###I am adding additional fields to the auth_user table.
auth.settings.extra_fields['auth_user']=[
    Field('Gender','string',requires=[IS_IN_SET(['MALE','FEMALE','OTHER']),IS_NOT_EMPTY() ] ,widget=SQLFORM.widgets.options.widget),
    Field('Pp','upload',requires=IS_EMPTY_OR(IS_IMAGE()),label='Profile Picture'),
    Field('phone_no','integer',requires=IS_INT_IN_RANGE(1111111111,9999999999),label="Phone Number"),
Field('City','string',length=64),
Field('Country',requires=[ IS_IN_SET(COUNTRIES), IS_NOT_EMPTY() ] ,widget=SQLFORM.widgets.options.widget),
    Field('dob','date',requires=[IS_NOT_EMPTY(),IS_DATE()] ,label='Date of birth',widget=SQLFORM.widgets.date.widget),
    Field('mail_nt',requires=[IS_IN_SET(['Yes','No']),IS_NOT_EMPTY()],widget=SQLFORM.widgets.radio.widget,label="Enable e-mail notifications"),
    Field('depend_rate','integer',readable=False,writable=False,default=-1),#If it is -1 then not rated.
    Field('votes_no','integer',readable=False,writable=False,default=0),
    Field('trips_no','integer',readable=False,writable=False,default=0)
]



## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)

## configure email
#from gluon.tools import Mail
#mail  = Mail()
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'cookbook5398@gmail.com'
mail.settings.login = 'cookbook5398:Cookbook'
mail.settings.tls = True

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

### The table trip details start here....

###This is to check if the login page is cleared or not.
if db.auth_user(db.auth_user.id==auth.user_id) is not None:
    usr = db.auth_user(db.auth_user.id==auth.user_id).first_name
else:
    usr = ''

###Dont forget to update the value of total_tillnow when you accept the form to people_start,similarly for Bags also.
db.define_table('trip',
                #The first field tells us the id of the user who floated the trip.
                Field('strid','integer',readable=False,writable=False,default=auth.user_id),
                Field('starter','string',writable=False,readable=False,default=usr),
                Field('from_place','string',requires=IS_NOT_EMPTY(),label="Starting Point"),
                Field('to_place','string',requires=IS_NOT_EMPTY(),label="Destination"),
                Field('date_of_trip','date',requires=[IS_DATE(),IS_NOT_EMPTY()],label="Date Of Trip"),
                Field('start_up','time',requires=[IS_TIME(),IS_NOT_EMPTY()], label="Earliest start time"),
                Field('start_end','time',requires=[IS_TIME(),IS_NOT_EMPTY()] ,label="Latest Start time"),
                Field('people_start','integer',requires=IS_NOT_EMPTY(),default=1,label="People at Start",widget=SQLFORM.widgets.integer.widget),
                Field('max_people','integer',requires=IS_NOT_EMPTY(),default=6,label="Maximum People for the trip",widget=SQLFORM.widgets.integer.widget),
                Field('total_tillnow','integer',readable=False,writable=False),
                Field('bags_start','integer',requires=IS_NOT_EMPTY(),default=1,label="No Of Bags",widget=SQLFORM.widgets.integer.widget),
                Field('bags_till_now','integer',readable=False,writable=False)
 )


###Finishing trip table.

###The votes table.

db.define_table('voting',
               Field('voterid','integer'),
               Field('candid','integer'),
               Field('rating',requires=IS_IN_SET(['1','2','3','4','5'])),
	       Field('name','string'),
               Field('comm','text'))
###The votes table ends here.


###Notification starts.To be generated by the computer.
db.define_table('notification',
                Field('usrid','integer'),
                Field('msg','text'),
                Field('date_of','date'),
                Field('time_of','time'),
                Field('status','integer'),#0- if it is not seen and 1-if it is seen.
)
### Notification ends here.

###Personal messages to users. Form to be created manually and inserted.###1-2 messages###Deciede about form view(SQL or Normal)
db.define_table('personal_message',
                Field('send_id','integer'),
                Field('rec_id','integer'),
                Field('status','integer'),#0- if it is not seen and 1-if it is seen.
                Field('msg_date','date'),
                Field('msg_time','time'),
                Field('msg','text'),
)
###Persnoal messages ends..
