# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

#def index(): redirect(URL(r=request,c='default',f='archivio_richieste'))
def index(): 
    response.title = T('Gratis, rapido e ti fa risparmiare!')
    return dict(message=T(""))

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
    links=[   lambda row: A('Dettagli richiesta', _href=URL("default","visualizza_dettagli_richiesta",args=[row.Prestazione.id]))
            , lambda row: A('Dettagli servizio', _href=URL("default","visualizza_dettagli_servizio",args=[row.Servizio.id]))
            #, lambda row: A('Dettagli fornitore', _href=URL("crud","tabella_Fornitore/view/Fornitore",args=[row.Fornitore.id]))
            , lambda row: A('Dettagli fornitore', _href=URL("default","visualizza_dettagli_fornitore",args=[row.Fornitore.id]))
            #, lambda row: A('Modifica dettagli fornitore', _href=URL("default","modifica_dettagli_fornitore",args=[row.Fornitore.id]))
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

def nuova_richiesta():
    pageTitle=T('Richiesta')
    if session.flash: response.flash = session.flash

    form_richiesta = SQLFORM(db.Prestazione                     
                            ,fields=[
                                     'Servizio' 
                                    ,'Fornitore'  
                                    ,'Cliente'
                                    ,'messaggio_utente'                
                                    ]
                            ,col3 = {
                                     'Servizio':A(T('ricerca il servizio'), _href=URL("default", "ricerca_servizio"))
                                    ,'Fornitore':A(T('ricerca il fornitore'), _href=URL("default", "ricerca_fornitore"))
                                    ,'Cliente':A(T('ricerca il cliente'), _href=URL("default", "ricerca_cliente"))
                                    }
                            )
    if session.richiesta: 
        form_richiesta.vars = session.richiesta
    else: 
        session.richiesta=form_richiesta.vars   
    if form_richiesta.validate():
        #session.richiesta=form_richiesta.vars
        session.flash = None
        redirect(URL('conferma_richiesta'))
        ### deal with uploads explicitly
    #elif session.richiesta:
    #    form.vars = session.richiesta       
    #else:
    #    form.vars.descrizione='nuovo'
    #    form.vars.auth_user=2   
    return dict(pageTitle=pageTitle, form_richiesta=form_richiesta)

def conferma_richiesta():
    pageTitle=T('Confermi la richiesta ?')
    richiesta = session.richiesta
    form_confirm = FORM.confirm(T('Sì'),{T('No'):URL('nuova_richiesta')})
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
    return dict (pageTitle=pageTitle,richiesta=richiesta, form_confirm=form_confirm)

def visualizza_dettagli_richiesta():
    pageTitle=T('Richiesta (dettagli)')
    id = request.args[0]
    query = (db.Prestazione.is_active==True) & (db.Prestazione.id==id)
    rows = db(query).select()
    grid=SQLFORM(db.Prestazione, db.Prestazione[id]
                    ,fields=['uuid', 'Servizio', 'Fornitore', 'Cliente' 
                            ,'messaggio_utente', 'giorno', 'prezzo', 'messaggio_studio'                   
                            ]
                    ,labels={'Servizio':T('Servizio richiesto'),'Fornitore':T('al fornitore'), 'Cliente':T('per il cliente'), 'messaggio_utente':T('Messaggio inviato'),'uuid':T('identificativo univoco della richiesta'), 'prezzo':T('e un prezzo di euro'), 'giorno':T('Il fornitore ha proposto il giorno'), 'messaggio_studio':T('specificando')}
                    ,readonly=True,showid=True)                   
    return locals()

def visualizza_dettagli_fornitore():
    pageTitle=T('Fornitore (dettagli)')
    id = request.args[0]
    query = (db.Fornitore.is_active==True) & (db.Fornitore.id==id)
    rows = db(query).select()
    grid=SQLFORM.grid(query
                    ,fields=[db.Fornitore.nome 
                            ,db.Fornitore.id                         
                            ]
                    ,headers={'Fornitore.nome':'Fornitore (nome)','Fornitore.id':'Dettagli (id)', 'Fornitore.codice':'Dettagli (codice)'}
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

def visualizza_dettagli_cliente():
    pageTitle=T('Cliente (dettagli)')
    id = request.args[0]
    query = (db.Cliente.is_active==True) & (db.Cliente.id==id)
    rows = db(query).select()
    grid=SQLFORM.grid(query
                    ,fields=[db.Cliente.nome 
                            ,db.Cliente.id
                            ,db.Cliente.codice                         
                            ]
                    ,headers={'Cliente.nome':'Cliente (nome)','Cliente.id':'Dettagli (id)', 'Cliente.codice':'Dettagli (codice)'}
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

def visualizza_dettagli_servizio():
    pageTitle=T('Servizio (dettagli)')
    id = request.args[0]
    query = (db.Servizio.is_active==True) & (db.Servizio.id==id)
    rows = db(query).select()
    grid=SQLFORM.grid(query
                    ,fields=[db.Servizio.nome 
                            ,db.Servizio.id
                            ,db.Servizio.codice                         
                            ]
                    ,headers={'Servizio.nome':'Servizio (nome)','Servizio.id':'Dettagli (id)', 'Servizio.codice':'Dettagli (codice)'}
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


tabelle= [tn for tn in db.tables if not (tn.endswith('_archive') or tn.startswith('auth_') or tn.startswith('plugin_'))  ]
response.menu = [
                    (T('Richiesta'), False, URL('default', 'nuova_richiesta'), [])
                    ,(T('Servizio'), False, URL('default', 'ricerca_servizio'), [])
                    ,(T('Fornitore'), False, URL('default', 'ricerca_fornitore'), [])
                    ,(T('Cliente'), False, URL('default', 'ricerca_cliente'), [])
                    ,(T('Archivio richieste'), False, URL('default', 'archivio_richieste'), [])
                    ,(T('HQ'), False, '#',
                                            [ (T(tn), False, URL('default', 'gestione_%s' % tn) ) for tn in tabelle ])
                    #,(T('R&S'), False, '#',
                    #                        [ 
                    #                            (T('Sito sviluppo applicazione'), False, URL('admin','design','CUP'), []),
                    #                            (T('Crea gruppi CUP'), False, URL('default','crea_gruppi_CUP'), [])
                    #                        ])            
                ]



def gestione_Categoria_servizio():return _gestione_tabella('Categoria_servizio') #SQLFORM.grid( db.Categoria_servizio, user_signature=False) )
def gestione_Stato_prestazione():return _gestione_tabella('Stato_prestazione')
def gestione_Cliente():return _gestione_tabella('Cliente')
def gestione_Fornitore():return _gestione_tabella('Fornitore')
def gestione_Servizio():return _gestione_tabella('Servizio')
def gestione_Prestazione():return _gestione_tabella('Prestazione')
def gestione_Servizio_disponibile():return _gestione_tabella('Servizio_disponibile')
def gestione_Soddisfazione():return _gestione_tabella('Soddisfazione')

def _gestione_tabella(tableName):
    pageTitle=T(tableName)
    grid=SQLFORM.grid( db[tableName])                      
    return dict(grid=grid, pageTitle=pageTitle)


def ricerca_fornitore():
    pageTitle=T('Fornitore')   
    elemento_selezionato=T('Nessuno selezionato')    
    id = 0
    if session.richiesta.Fornitore: 
        id = session.richiesta.Fornitore
        elemento_selezionato = db.Fornitore[id].nome+'('+db.Fornitore[id].codice+') '+T('selezionato')
        elemento_selezionato = A(elemento_selezionato, _href=URL("default","visualizza_dettagli_fornitore",args=[id]))
    else: fornitore = 0
    query = ((db.Fornitore.is_active==True)) if request.get_vars.keywords else (db.Fornitore.id==id)   
    links=[   
             lambda row: A('Dettagli', _href=URL("default","visualizza_dettagli_fornitore",args=[row.id]))
            ,lambda row: A('Seleziona', _href=URL("default","_seleziona_fornitore",args=[row.id]))
          ] 
    grid=SQLFORM.grid( query
                      ,fields=[db.Fornitore.id, db.Fornitore.nome, db.Fornitore.codice                         
                            ]
                      ,links=links                  
                      ,showbuttontext=False
                      ,deletable=False
                      ,editable = False  #PROVARE editable= [lambda row :  row.locked == 0] #https://groups.google.com/forum/#!searchin/web2py/SQLFORM.grid$20selectable/web2py/7Trx6afrNYI/T8K3k7TXcb8J
                      ,details = True
                      ,create = False
                      ,selectable = None
                      ,links_placement = 'right', buttons_placement = 'right'
                      ,user_signature=False
                      ,csv=False
                      ,searchable=True
                    )                       
    return dict(pageTitle=pageTitle, elemento_selezionato=elemento_selezionato, grid=grid)

def _seleziona_fornitore(): 
    session.richiesta.Fornitore = request.args[0]
    session.flash = T('Fornitore selezionato')      
    redirect(URL('nuova_richiesta'))    
    return

###################################################################################################################################
def ricerca_servizio():
    pageTitle=T('Servizio')   
    elemento_selezionato=T('Nessuno selezionato')
    id = 0    
    if session.richiesta.Servizio: 
        id = session.richiesta.Servizio
        elemento_selezionato = db.Servizio[id].nome+'('+db.Servizio[id].codice+') '+T('selezionato')
        elemento_selezionato = A(elemento_selezionato, _href=URL("default","visualizza_dettagli_servizio",args=[id]))
    else: fornitore = 0
    query = ((db.Servizio.is_active==True)) if request.get_vars.keywords else (db.Servizio.id==id)     
    links=[   
             lambda row: A('Dettagli', _href=URL("default","visualizza_dettagli_servizio",args=[row.id]))
            ,lambda row: A('Seleziona', _href=URL("default","_seleziona_servizio",args=[row.id]))
          ] 
    grid=SQLFORM.grid( query
                      ,fields=[db.Servizio.id, db.Servizio.nome, 
                               db.Servizio.codice                         
                              ]
                      ,links=links                  
                      ,showbuttontext=False
                      ,deletable=False
                      ,editable = False  #PROVARE editable= [lambda row :  row.locked == 0] #https://groups.google.com/forum/#!searchin/web2py/SQLFORM.grid$20selectable/web2py/7Trx6afrNYI/T8K3k7TXcb8J
                      ,details = True
                      ,create = False
                      ,selectable = None
                      ,links_placement = 'right', buttons_placement = 'right'
                      ,user_signature=False
                      ,csv=False
                      ,searchable=True
                    )                       
    return dict(pageTitle=pageTitle, elemento_selezionato=elemento_selezionato, grid=grid)

def _seleziona_servizio(): 
    session.richiesta.Servizio = request.args[0]
    session.flash = T('Servizio selezionato')      
    redirect(URL('nuova_richiesta'))    
    return
###################################################################################################################################

###################################################################################################################################
def ricerca_cliente():
    pageTitle=T('Cliente')   
    elemento_selezionato=T('Nessuno selezionato')
    id = 0    
    if session.richiesta.Cliente: 
        id = session.richiesta.Cliente
        elemento_selezionato = db.Cliente[id].nome+'('+db.Cliente[id].codice+') '+T('selezionato')
        elemento_selezionato = A(elemento_selezionato, _href=URL("default","visualizza_dettagli_cliente",args=[id]))
    else: fornitore = 0
    query = ((db.Cliente.is_active==True) & (db.Cliente.created_by==auth.user_id)) if request.get_vars.keywords else (db.Cliente.id==id)   
    links=[   
             lambda row: A('Dettagli', _href=URL("default","visualizza_dettagli_cliente",args=[row.id]))
            ,lambda row: A('Seleziona', _href=URL("default","_seleziona_cliente",args=[row.id]))
          ] 
    grid=SQLFORM.grid( query
                      ,fields=[db.Cliente.id, db.Cliente.nome, 
                               db.Cliente.codice                         
                              ]
                      ,links=links                  
                      ,showbuttontext=False
                      ,deletable=False
                      ,editable = False  #PROVARE editable= [lambda row :  row.locked == 0] #https://groups.google.com/forum/#!searchin/web2py/SQLFORM.grid$20selectable/web2py/7Trx6afrNYI/T8K3k7TXcb8J
                      ,details = True
                      ,create = False
                      ,selectable = None
                      ,links_placement = 'right', buttons_placement = 'right'
                      ,user_signature=False
                      ,csv=False
                      ,searchable=True
                    )                       
    return dict(pageTitle=pageTitle, elemento_selezionato=elemento_selezionato, grid=grid)

def _seleziona_cliente(): 
    session.richiesta.Cliente = request.args[0]
    session.flash = T('Cliente selezionato')      
    redirect(URL('nuova_richiesta'))    
    return
###################################################################################################################################



def test():
    config=dict(color='black', language='English')
    form = SQLFORM.dictform(config)
    #if form.process().accepted:
     #   session.config.update(form.vars)
    return dict(form=form)

@auth.requires(auth.has_membership(role='Sviluppatore'))
def crea_gruppi_CUP():
    groups ='''
        Cliente
        Fornitore
        Amministratore
    '''.split()
    for group in groups:  
        auth.add_group(group, T(group)) 

    #auth.add_group('Cliente', T('Cliente'))
    #auth.add_group('Fornitore', T('Fornitore'))
    #auth.add_group('Amministratore', T('Amministratore)')
    #auth.add_group('Sviluppatore', T('Sviluppatore'))
    return dict(message=T("Gruppi creati:"),groups=groups)