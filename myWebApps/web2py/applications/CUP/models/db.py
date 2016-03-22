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
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all']) #qui potrei mettere migrate=False
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

from gluon.tools import Auth, Service, PluginManager

service = Service()
plugins = PluginManager()

auth = Auth(db)

# campi comuni a tutte le tabelle
import uuid
Field_uuid = Field('uuid', length=64, default=lambda:str(uuid.uuid4()))
Fields_signature = auth.signature


auth_tablenames ='''
    auth_cas
    auth_event
    auth_group
    auth_membership
    auth_permission
    auth_user
'''.split()

## campi aggiuntivi si definiscono dopo auth = Auth(db)
for auth_tablename in auth_tablenames:
    auth.settings.extra_fields[auth_tablenames]=[Field_uuid]

## e prima di auth.define_tables(...)

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=True)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
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

# My application DB
# WARNING: notnull=True, default='NULL' is a contradition and generates a strange error after some lines !!!!
# The following source code was generated by SQLDesigner and reordered to avoid missing reference (eg. Servizio must come before Categoria_servizio which refers to it)


#mie variabili
valoreNonDefinito=None
mostraCodiceNome=' %(codice)s %(nome)s'

#schema DB creato a partire da (ma non identico a) schema ER del 16/03/2016

#le seguenti due righe aggiungerebbero (append) fields comuni a tutte le tabelle non auth
#db._common_fields.append(Fields_signature) #anche se questa riga viene prima i campi vengono appesi dopo quelli definiti dopo
#db._common_fields.append(Field_uuid) 

#tabelle e relazioni
db.define_table("Categoria_servizio",
    Field_uuid,
    Fields_signature,
    Field("codice", "string", default=valoreNonDefinito,length=3),
    Field("nome", "string", default=valoreNonDefinito))#,
    #migrate=False)

db.define_table("Stato_prestazione",
    Field_uuid,
    Fields_signature,
    Field("codice", "string", notnull=True, default=valoreNonDefinito, length=3),
    Field("nome", "string", default=valoreNonDefinito))

Agente = db.Table(db,"Agente",
    Field_uuid,
    Fields_signature,
    Field("uuid_auth_user", "reference auth_user"),
    Field("codice", "string", default=valoreNonDefinito),
    Field("nome", "string", default=valoreNonDefinito),
    Field("cap", "string", default='00000', length=5),
    Field("via", "string", default=valoreNonDefinito),
    Field("descrizione", "text", default=valoreNonDefinito))
Agente.uuid_auth_user.requires=IS_IN_DB( db, 'auth_user.uuid', ' %(first_name)s %(last_name)s (%(email)s)') 

db.define_table("Cliente", 
    Agente)
db.define_table("Fornitore", 
    Agente)

db.define_table("Servizio",
    Field_uuid,
    Fields_signature,
    Field("id_Categoria_servizio", "reference Categoria_servizio"),
    Field("codice", "string", default=valoreNonDefinito),
    Field("nome", "string", default=valoreNonDefinito),
    Field("descrizione", "text", default=valoreNonDefinito),
    Field("prezzo_SSR", "integer", default=valoreNonDefinito),
    Field("ticket_SSR", "double", default=valoreNonDefinito))
db.Servizio.id_Categoria_servizio.requires=IS_IN_DB( db, 'Categoria_servizio.id', mostraCodiceNome)

db.define_table("Prestazione",
    Field_uuid,
    Fields_signature,
    Field("id_Servizio", "reference Servizio"),
    Field("id_Fornitore", "reference Fornitore"),
    Field("id_Cliente", "reference Cliente"),
    Field("id_Stato_prestazione", "reference Stato_prestazione"),
    Field("messaggio_utente", "text", default=valoreNonDefinito),
    Field("messaggio_studio", "text", default=valoreNonDefinito),
    Field("servizio_richiesto_disponibile", "boolean", default=valoreNonDefinito),
    Field("giorno", "date", default=valoreNonDefinito),
    Field("ora", "time", default=valoreNonDefinito),
    Field("prezzo", "double", default=valoreNonDefinito))
db.Prestazione.id_Servizio.requires=IS_IN_DB( db, 'Servizio.id', mostraCodiceNome)
db.Prestazione.id_Fornitore.requires=IS_IN_DB( db, 'Fornitore.id', mostraCodiceNome)
db.Prestazione.id_Cliente.requires=IS_IN_DB( db, 'Cliente.id', mostraCodiceNome)
db.Prestazione.id_Stato_prestazione.requires=IS_IN_DB( db, 'Stato_prestazione.id', mostraCodiceNome)

db.define_table("Servizio_disponibile",
    Field_uuid,
    Fields_signature,
    Field("id_Servizio", "reference Servizio"),
    Field("id_Fornitore", "reference Fornitore"),
    Field("id_Categoria_servizio", "reference Categoria_servizio"),
    Field("Lunedi_mattina", "boolean", default=valoreNonDefinito),
    Field("Lunedi_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("Martedi_mattina", "boolean", default=valoreNonDefinito),
    Field("Martedi_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("Mercoledi_mattina", "boolean", default=valoreNonDefinito),
    Field("Mercoledi_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("Giovedi_mattina", "boolean", default=valoreNonDefinito),
    Field("Giovedi_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("Venerdi_mattina", "boolean", default=valoreNonDefinito),
    Field("Venerdi_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("Sabato_mattina", "boolean", default=valoreNonDefinito),
    Field("Sabato_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("Domenica_mattina", "boolean", default=valoreNonDefinito),
    Field("Domenica_pomeriggio", "boolean", default=valoreNonDefinito),
    Field("prezzo_listino", "double", default=valoreNonDefinito),
    Field("prezzo_medio", "integer", default=valoreNonDefinito))
db.Servizio_disponibile.id_Servizio.requires=IS_IN_DB( db, 'Servizio.id', mostraCodiceNome)
db.Servizio_disponibile.id_Fornitore.requires=IS_IN_DB( db, 'Fornitore.id', mostraCodiceNome)
db.Servizio_disponibile.id_Categoria_servizio.requires=IS_IN_DB( db, 'Categoria_servizio.id', mostraCodiceNome)

db.define_table("Soddisfazione",
    Field_uuid,
    Fields_signature,
    Field("punteggio_cliente", "integer", default=valoreNonDefinito),
    Field("commento_cliente", "text", default=valoreNonDefinito),
    Field("commento_fornitore", "text", default=valoreNonDefinito),
    Field("commento_cliente_pubblicato", "text", default=valoreNonDefinito),
    Field("commento_fornitore_pubblicato", "text", default=valoreNonDefinito),
    Field("id_Fornitore", "reference Fornitore"),
    Field("id_Cliente", "reference Cliente"),
    Field("pubblicato", "boolean", default=valoreNonDefinito))
db.Soddisfazione.id_Fornitore.requires=IS_IN_DB( db, 'Fornitore.id', mostraCodiceNome)
db.Soddisfazione.id_Cliente.requires=IS_IN_DB( db, 'Cliente.id', mostraCodiceNome)

# end generated source code from SQLDesigner
## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)

db.Categoria_servizio._enable_record_versioning()
db.Cliente._enable_record_versioning()
db.Fornitore._enable_record_versioning()
db.Prestazione._enable_record_versioning()
db.Servizio._enable_record_versioning()
db.Servizio_disponibile._enable_record_versioning()
db.Soddisfazione._enable_record_versioning()
db.Stato_prestazione._enable_record_versioning()
