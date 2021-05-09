import sqlite3
import datetime
import os
import json
from scripts.artifacts.appCookies import get_appCookies

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_skype(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if (file_found.endswith('RKStorage')):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            Select key, value from catalystLocalStorage
            where lower(key) = 'skypexskypeid'
                ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                for row in all_rows:
                    skype_user_id = row[1]   #Could there be more than one skype id with corresponding DBs? If so this should be a list and the next loop be indented to this one
                    skype_user_id = skype_user_id +'.db'
            else:
                skype_user_id = ""

    for file_found in files_found:
        file_found = str(file_found)
        if (file_found.endswith(skype_user_id)):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            cursor.execute('''
            Select nsp_data from localAddressBookContacts
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            if usageentries > 0:
                report = ArtifactHtmlReport('Skype - Local Address Book Contacts')
                report.start_artifact_report(report_folder, 'Skype - Local Address Book Contacts')
                report.add_script()
                data_headers = ('id', 'first_name', 'middle_name', 'last_name', 'email_addresses', 'phones') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    addressDict = json.loads(row[0])
                    id_name = addressDict['id']
                    data_list.append((id_name.replace('abc:',''), addressDict['firstName'], addressDict['middleName'], addressDict['lastName'], addressDict['emails'], addressDict['phones']))
                    
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Skype - Local Address Book Contacts'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                
            else:
                logfunc('No Skype - Local Address Book Contacts available')

    for file_found in files_found:
        file_found = str(file_found)
        
        if (file_found.endswith('Cookies')):
            get_appCookies(file_found, report_folder, seeker, wrap_text, "Skype")

