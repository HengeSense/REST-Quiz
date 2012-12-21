# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
#auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'felicity.iiit.ac.in:587'
mail.settings.sender = 'webmaster@felicity.iiit.ac.in'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

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



#### PARTICIPANT Registration #####
auth.settings.extra_fields[auth.settings.table_user_name] = [
    Field('handle',
        unique=True,
        length=50,
        label="Threads Handle"), #Username for competitions. eg. phinfinity
    Field('profile_pic','upload'), #A display pic of their choice.
    Field('about','text',label="Something about you"),
    Field('contact','string',label='Contact Number')
    ]
auth.define_tables()



custom_auth_table = db[auth.settings.table_user_name]



#------ PARTICIPANT VALIDATORS -----#
custom_auth_table.profile_pic.requires = IS_NOT_EMPTY(error_message="Please upload an image. It is your identity.")
custom_auth_table.profile_pic.requires = IS_IMAGE(maxsize=(250,250))
######## END OF PARTICIPANT REG. ############



########################################################################
#                  EVENTS                                              #
########################################################################
db.define_table('events',
    Field('name','string',unique=True),
    Field('start','datetime'),
    Field('end','datetime'),
    Field('flow_of_questions','integer'),
    Field('judge','string'),
    Field('organizer','string'))


########################################################################
#                 Event Questions                                      #
########################################################################
db.define_table('question',
    Field('title','string'),
    Field('event','integer'),
    Field('question_no','integer'),
    Field('question','text'),
    Field('answer','text'))


########################################################################
#                    Event-user                                        #
########################################################################
db.define_table('event_user',
    Field('event_id',requires = IS_IN_DB(db, db.events.id)),
    Field('user_id',requires = IS_IN_DB(db,db.auth_user.id)),
    Field('user_data', 'reference auth_user'),
    Field('score','integer'),
    Field('status','string'),
    Field('penalty','integer'),
    Field('current_question','integer'))

#########################################################################
#                  Event - static pages                                 #
# -> Each event will have a set of tabs like rules,prizes ...           #
#########################################################################

db.define_table('event_tab',
    Field('event_id','integer'),
    Field('tab_id','integer'),
    Field('title','string'),
    Field('raw_content','text'))




#########################################################################
#                 Question Comments                                     #
# Some thing on the lines of Spoj Commenting                            #
#                      - Had to be done by Pallav :/                    #
#########################################################################

db.define_table('comments',
    Field('event_id','integer',readable=False,writable=False),
    Field('question_no','integer',readable=False,writable=False),
    Field('user_id','reference auth_user',writable=False, readable=False),
    Field('comment','string'),
    Field('time_stamp','time',readable=False,writable=False))
    




