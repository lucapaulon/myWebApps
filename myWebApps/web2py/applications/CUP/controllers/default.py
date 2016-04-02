# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index(): redirect(URL(r=request,c='default',f='archivio_richieste'))

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

def archivio_richieste():
    pageTitle=T('Archivio delle richieste')
    if session.flash: response.flash = session.flash
    links=[   lambda row: A('Dettagli richiesta', _href=URL("default","tabella_Prestazione/view/Prestazione",args=[row.Prestazione.id]))
            , lambda row: A('Dettagli servizio', _href=URL("default","tabella_Servizio/view/Servizio",args=[row.Servizio.id]))
            #, lambda row: A('Dettagli fornitore', _href=URL("crud","tabella_Fornitore/view/Fornitore",args=[row.Fornitore.id]))
            , lambda row: A('Dettagli fornitore', _href=URL("default","visualizza_dettagli_fornitore",args=[row.Fornitore.id]))
            , lambda row: A('Modifica dettagli fornitore', _href=URL("default","modifica_dettagli_fornitore",args=[row.Fornitore.id]))
          ]
    
    query = ((db.Prestazione.is_active==True) & (db.Prestazione.created_by==auth.user_id)) if request.get_vars.keywords else (db.Prestazione.id==0)                                        
    grid=SQLFORM.grid(query
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
                    ,details = False # bottone per vedere la prestazione; si disabilita se aggiungo un altro link per questo
                    ,create = False
                    ,selectable = None
                    ,links_placement = 'right', buttons_placement = 'right'
                    ,user_signature=False
                    ,csv=False)
    #youtube = plugin_wiki.widget('youtube',code='l7AWnfFRc7g')
    pie = plugin_wiki.widget('pie_chart',data='10,20,30',names='TAC,RNM,PET',width=300,height=150,align='center')
    bar = plugin_wiki.widget('bar_chart',data='10,20,30',names='TAC,RNM,PET',width=300,height=150,align='center')
    #map = plugin_wiki.widget('map', key='AIzaSyD41CEtZdJ3YqUuisUrQEJgXZIPiV0_r50', table='Fornitore',width=800,height=400)
    return locals() # dict(grid=grid)

def visualizza_dettagli_fornitore():
    pageTitle=T('Dettagli del fornitore')
    id = request.args[0]
    session.fornitore = id
    query = (db.Fornitore.is_active==True) & (db.Fornitore.id==id)
    rows = db(query).select()
    grid=SQLFORM.grid(query
                    ,fields=[db.Fornitore.nome 
                            ,db.Fornitore.id                         
                            ]
                    ,headers={'Fornitore.nome':'Fornitore (nome)','Fornitore.id':'Dettagli (id fornitore)'}
                    ,showbuttontext=False
                    ,deletable=False
                    ,editable = False  #PROVARE editable= [lambda row :  row.locked == 0] #https://groups.google.com/forum/#!searchin/web2py/SQLFORM.grid$20selectable/web2py/7Trx6afrNYI/T8K3k7TXcb8J
                    ,details = False
                    ,create = False
                    ,selectable = None
                    ,links_placement = 'right', buttons_placement = 'right'
                    ,user_signature=False
                    ,csv=False
                    ,searchable=False)                   
    map = _map()
    latitude=rows[0].latitude
    longitude=rows[0].longitude
    map_popup = rows[0].map_popup
    return locals()

def modifica_dettagli_fornitore():
    pageTitle=T('Edit del fornitore')
    id = session.fornitore
    query = (db.Fornitore.is_active==True) & (db.Fornitore.id==id)
    rows = db(query).select()
    record = rows[0]
    form = SQLFORM(db.Fornitore,record)
    if form.validate():
        if form.deleted:
            db(db.Fornitore.id==record.id).delete()
        else:
            form.record.update_record(**dict(form.vars))
        response.flash = 'record updated'

    return dict(form=form)

def nuova_richiesta():
    pageTitle=T('Nuova richiesta di prestazione')
    if session.flash: response.flash = session.flash
    form_richiesta = SQLFORM(db.Prestazione)
    if session.richiesta: form_richiesta.vars = session.richiesta   
    if form_richiesta.validate():
        session.richiesta=form_richiesta.vars
        session.flash = None
        redirect(URL('conferma_richiesta'))
        ### deal with uploads explicitly
    #elif session.richiesta:
    #    form.vars = session.richiesta       
    #else:
    #    form.vars.descrizione='nuovo'
    #    form.vars.auth_user=2   
    return dict(form_richiesta=form_richiesta)

def conferma_richiesta():
    richiesta = session.richiesta
    form_confirm = FORM.confirm('Confermo',{'Non confermo':URL('nuova_richiesta')})
    if form_confirm.accepted:
        id = richiesta.id
        if id:
            #db.Fornitore.update(**dict(richiesta))
            db(db['Prestazione']._id==id).update(**dict(richiesta))
            session.flash = T('Richiesta salvata')   
            session.richiesta = None
        else:
            session.richiesta.id = db.Prestazione.insert(**dict(richiesta))
            session.flash = T('Richiesta salvata')      
            session.richiesta = None 
        redirect(URL('archivio_richieste'))          
    return dict (richiesta=richiesta, form_confirm=form_confirm)

def _map(table='Fornitore'): # IL WIDGET NON VA BENE PERCHE' LEGGE SU UNA TABELLA DEL DB NON FILTRATA 
    map = plugin_wiki.widget('map', key='AIzaSyD41CEtZdJ3YqUuisUrQEJgXZIPiV0_r50', table=table,width=800,height=400)
    return map

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


######################################## crud


tabelle= [tn for tn in db.tables if not (tn.endswith('_archive') or tn.startswith('auth_'))  ]
response.menu = [
        (T('Nuova richiesta'), False, URL('default', 'nuova_richiesta'), []),
        (T('Archivio richieste'), False, URL('default', 'archivio_richieste'), []),
        (T('My Tables'), False, '#',
             [ (T(tn), False, URL('default', 'tabella_%s' % tn) ) for tn in tabelle ])
    ]


def index():
    return dict(message=T("CUP Online. Lavori in corso"))

def tabella_Categoria_servizio():return dict(grid=SQLFORM.grid( db.Categoria_servizio, user_signature=False) )
def tabella_Stato_prestazione():return dict(grid=SQLFORM.grid( db.Stato_prestazione, user_signature=False) )
def tabella_Cliente():return dict(grid=SQLFORM.grid( db.Cliente, user_signature=True) )
def tabella_Fornitore():return dict(grid=SQLFORM.grid( db.Fornitore, user_signature=False) )
def tabella_Servizio():return dict(grid=SQLFORM.grid( db.Servizio, user_signature=False) )
def tabella_Prestazione():return dict(grid=SQLFORM.grid( db.Prestazione, user_signature=False) )
def tabella_Servizio_disponibile():return dict(grid=SQLFORM.grid( db.Servizio_disponibile, user_signature=False) )
def tabella_Soddisfazione():return dict(grid=SQLFORM.grid( db.Soddisfazione, user_signature=False) )

def test():
    config=dict(color='black', language='English')
    form = SQLFORM.dictform(config)
    #if form.process().accepted:
     #   session.config.update(form.vars)
    return dict(form=form)

def session_form_richiesta_none():
    session.form_richiesta = None
    return None