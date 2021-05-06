import sqlite3
import datetime
import os
import json
from scripts.artifacts.appCookies import get_appCookies

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_skype_userid(files_found):

    skype_user_id = ""
    for file_found in files_found:
        file_name = str(file_found)
        if (file_name.lower().endswith("rkstorage")):
            db = open_sqlite_db_readonly(file_name)
            cursor = db.cursor()

            try:
                cursor.execute('''Select key, value from catalystLocalStorage
                                  where lower(key) = 'skypexskypeid'
                ''')

                all_rows = cursor.fetchall()
                for row in all_rows:
                    skype_user_id = row[1]
            except:
                skype_user_id = ""

    return skype_user_id


def get_skype(files_found, report_folder, seeker, wrap_text):

    user_id = None
    source_file = ''
    skype_user_id = get_skype_userid(files_found)
    for file_found in files_found:
        
        file_name = str(file_found)
        if ((skype_user_id in file_name.lower()) and ('wal' not in file_name.lower())
            and ('shm') not in file_name.lower()):
           skype_db = str(file_found)
        elif (file_name.lower().endswith('cookies')):
            get_appCookies(file_found, report_folder, seeker, wrap_text, "Skype")
        else:
           continue


        db = open_sqlite_db_readonly(skype_db)
        cursor = db.cursor()
            
        try:
            cursor.execute('''
                         Select nsp_data from localAddressBookContacts
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
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
            
            tlactivity = f'Skype - Local Address Book Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Skype - Local Address Book Contacts available')
                

        db.close
        
    return