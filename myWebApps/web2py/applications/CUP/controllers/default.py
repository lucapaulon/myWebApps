# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index(): redirect(URL(r=request,c='default',f='home'))

def search():
    form = SQLFORM.grid(db.Servizio, user_signature=True, deletable=False, details=False)
    chart=bar_chart(data='1,2,3',names='a,b,c',width=300,height=150,align='center')
    return dict(form=form, chart=chart)

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

def home():
    pageTitle=T('Prestazioni richieste')

    links=[   lambda row: A('Dettagli prestazione', _href=URL("crud","tabella_Prestazione/view/Prestazione",args=[row.Prestazione.id]))
            , lambda row: A('Dettagli servizio', _href=URL("crud","tabella_Servizio/view/Servizio",args=[row.Servizio.id]))
            #, lambda row: A('Dettagli fornitore', _href=URL("crud","tabella_Fornitore/view/Fornitore",args=[row.Fornitore.id]))
            , lambda row: A('Dettagli fornitore', _href=URL("default","fornitore",args=[row.Fornitore.id]))
          ]
    grid=SQLFORM.grid(db.Prestazione
                        ,left=[db.Servizio.on(db.Prestazione.Servizio==db.Servizio.id), db.Cliente.on(db.Prestazione.Cliente==db.Cliente.id), db.Fornitore.on(db.Prestazione.Fornitore==db.Fornitore.id)]
                        ,fields=[db.Cliente.nome
                                ,db.Servizio.nome 
                                ,db.Fornitore.nome 
                                ,db.Prestazione.id,db.Prestazione.giorno       
                                ,db.Servizio.descrizione, db.Servizio.id, db.Fornitore.id                         
                                ]
                        ,headers={'db.Prestazione.id':'Prestazione (id)', 'Prestazione.giorno':'Giorno', 'Cliente.nome':'Cliente','Fornitore.nome':'Fornitore (nome)','Fornitore.id':'Dettagli (id fornitore)','Servizio.nome':'Servizio (nome)','Servizio.id':'Dettagli (id servizio)','Servizio.descrizione':'Dettagli (descrizione servizio)'}
                        ,links=links
                        ,showbuttontext=False
                        ,deletable=False
                        ,editable = False  #PROVARE editable= [lambda row :  row.locked == 0] #https://groups.google.com/forum/#!searchin/web2py/SQLFORM.grid$20selectable/web2py/7Trx6afrNYI/T8K3k7TXcb8J
                        ,details = True # bottone per vedere la prestazione; si disabilita se aggiungo un altro link per questo
                        ,create = False
                        ,selectable = None
                        ,links_placement = 'left', buttons_placement = 'right'
                        ,user_signature=False)

    #youtube = plugin_wiki.widget('youtube',code='l7AWnfFRc7g')
    pie = plugin_wiki.widget('pie_chart',data='10,20,30',names='TAC,RNM,PET',width=300,height=150,align='center')
    bar = plugin_wiki.widget('bar_chart',data='10,20,30',names='TAC,RNM,PET',width=300,height=150,align='center')
    #map = plugin_wiki.widget('map', key='AIzaSyD41CEtZdJ3YqUuisUrQEJgXZIPiV0_r50', table='Fornitore',width=800,height=400)
    return locals() # dict(grid=grid)

def fornitore():
    pageTitle=T('Dettagli del fornitore')
    id = request.args[0]
    record = SQLTABLE(db(db['Fornitore']['id']==id).select()
                        ,fields=[db.Fornitore.nome,db.Fornitore.codice] #NON FUNZIONA
                        )
    #form='FORM'
    table='Fornitore' # QUI BISOGNA USARE UNA TABELLA DI APPOGGIO FILTRATA DA Fornitore PER id  
    map = plugin_wiki.widget('map', key='AIzaSyD41CEtZdJ3YqUuisUrQEJgXZIPiV0_r50', table=table,width=800,height=400)
    return locals()

def Servizio():
    homeTitle=T('I servizi sanitari')
    db.Prestazione.Servizio.writable = False
    grid = SQLFORM.smartgrid( 
        db.Servizio, 
        user_signature=False, 
        linked_tables=['Categoria_servizio'],
        links = [lambda row: A(T('Seleziona'),_href=URL("default","showRecord",args=[row.id]))],
        links_in_grid=True
        )
    return locals()

def showRecord():
    #request.vars
    output = 'Record numero '+str(request.args[0])
    return output

from gluon.contrib.populate import populate
def populate_db():
    output = ''
    #output = output + _populate_db_table('auth_user', db.auth_user, 2)    
    output = output + _populate_db_table('Cliente', db.Cliente, 2) 
    output = output + _populate_db_table('Fornitore', db.Fornitore, 2)  
    output = output + _populate_db_table('Categoria_servizio', db.Categoria_servizio, 2)    
    output = output + _populate_db_table('Servizio', db.Servizio, 2)   
    output = output + _populate_db_table('Servizio_disponibile', db.Servizio_disponibile, 2)    
    output = output + _populate_db_table('Stato_prestazione', db.Stato_prestazione, 2)    
    output = output + _populate_db_table('Prestazione', db.Prestazione, 2)      
    output = output + _populate_db_table('Soddisfazione', db.Soddisfazione, 2)   
    return output
#metodo privato inizia con under score
def _populate_db_table(dbTableName, dbTable, numRows):
    output = ''
    populate(dbTable,numRows)    
    for Entity in db(dbTable.id>0).select(limitby=(0,9)):
        output = output + dbTableName + ': ' + str(Entity.id) + '; '
    return output

def export_db():
    filename = 'export.csv'
    db.export_to_csv_file(open(filename,'wb'))
    #open('Cliente.csv','wb').write(str(db(db.Cliente.id).select()))
    return 'Export db to file ' + filename

def import_db():
    filename = 'export.csv'
    db.import_from_csv_file(open(filename,'rb'))
    return 'Import data from csv into DB'

def export_db_table():
    filename = 'export_table.csv'
    dbTable = db.Cliente
    tablename = 'Cliente'
    open(filename,'wb').write(str(db(dbTable.id).select()))
    return 'Export ' + tablename + ' from db to file ' + filename

#NON FUNZIONA
def import_db_table():
    filename = 'export_table.csv'
    db.import_from_csv_file(open(filename,'rb'))
    return 'Import csv data from file '+filename + 'into DB table'

import StringIO
#Di Pierro
def export():
    s = StringIO.StringIO()
    db.export_to_csv_file(s)
    response.headers['Content-Type'] = 'text/csv'
    return s.getvalue()

def import_and_sync():
    form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
    if form.process().accepted:
        db.import_from_csv_file(form.vars.data.file,unique=False)
        # for every table
        for table in db.tables:
            # for every uuid, delete all but the latest
            try:
                items = db(db[table]).select(db[table].id,
                           db[table].uuid,
                           orderby=db[table].modified_on,
                           groupby=db[table].uuid)
                for item in items:
                    print '...'+str(item)+' imported'
                    db((db[table].uuid==item.uuid)&(db[table].id!=item.id)).delete()
            except Exception, e:
                print 'oops: %s' % e
                print 'problems with '+str(item)
            finally:
                print 'done'
    return dict(form=form)