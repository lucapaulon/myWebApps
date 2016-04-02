# -*- coding: utf-8 -*-
#response.generic_patterns = ['crud/*'] #abilita le view generiche

#from gluon.tools import Crud
#crud = Crud(db)
#crud.settings.controller = 'crud'

#tabelle= [tn for tn in db.tables if not (tn.endswith('_archive') or tn.startswith('auth_'))  ]
#response.menu = [
#        (T('Home'), False, URL('default', 'index'), []),
#        (T('My Tables'), False, '#',
#             [ (T(tn), False, URL('crud', 'tabella_%s' % tn) ) for tn in tabelle ])
#    ]


#def index():
#    return dict(message=T("CUP Online. Lavori in corso"))

#def tabella_Categoria_servizio():return dict(grid=SQLFORM.grid( db.Categoria_servizio, user_signature=False) )
#def tabella_Stato_prestazione():return dict(grid=SQLFORM.grid( db.Stato_prestazione, user_signature=False) )
#def tabella_Cliente():return dict(grid=SQLFORM.grid( db.Cliente, user_signature=True) )
#def tabella_Fornitore():return dict(grid=SQLFORM.grid( db.Fornitore, user_signature=False) )
#def tabella_Servizio():return dict(grid=SQLFORM.grid( db.Servizio, user_signature=False) )
#def tabella_Prestazione():return dict(grid=SQLFORM.grid( db.Prestazione, user_signature=False) )
#def tabella_Servizio_disponibile():return dict(grid=SQLFORM.grid( db.Servizio_disponibile, user_signature=False) )
#def tabella_Soddisfazione():return dict(grid=SQLFORM.grid( db.Soddisfazione, user_signature=False) )

#def test():
#    config=dict(color='black', language='English')
#    form = SQLFORM.dictform(config)
#    #if form.process().accepted:
#     #   session.config.update(form.vars)
#    return dict(form=form)

#def session_form_richiesta_none():
#    session.form_richiesta = None
#    return None