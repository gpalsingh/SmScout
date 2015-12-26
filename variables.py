#-*- coding: utf:8 -*-
#This files contains values global to whole project
import os

homepage = 'http://int.soccerway.com'
files =os.path.abspath( os.path.join('.','SWdata') )
test_folder = os.path.join( files, 'testing')
database_folder = os.path.join( files, 'databases' )
main_database = os.path.join( database_folder, 'logs.db' )
done_leagues_table = 'doneleagues'
testing_database = test_folder + 'logtest.db'
attrs_required = ['mins','apps','goals','linups']
attrs_to_save = ['name', 'age', 'team', 'pos' ]
for att in attrs_required:
    attrs_to_save.extend([x+att for x in ['', 'tot', 'career']])
extra_attrs_to_save = { 'fname':'string', 'lname':'string', 'league_name':'string' }
        
try:
    os.mkdirst( database_folder )
except:
    pass
