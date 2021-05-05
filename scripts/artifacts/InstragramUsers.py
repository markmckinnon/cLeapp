import sqlite3
import datetime
import os
import json
from scripts.artifacts.appCookies import get_appCookies

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_instragramUsers(files_found, report_folder, seeker, wrap_text):

    thread_user_fields = ('username', 'full_name', 'profile_pic_url', 'profile_pic_id','id','is_private', 'is_verified')
    user_id = None
    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if ('wal' in file_name.lower() and ('shm') in file_name.lower()):
            continue
        elif (file_name.lower().endswith('cookies')):
            get_appCookies(file_found, report_folder, seeker, wrap_text, "Instragram")

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
            
        try:
            cursor.execute('''
                         select cast (thread_info as text) from threads;
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Instragram - Users')
            report.start_artifact_report(report_folder, 'Instragram - Users')
            report.add_script()
            data_headers = thread_user_fields # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                thread_info = json.loads(row[0])
                thread_user_types = ('inviter', 'recipients')
                for thread_in in thread_info['recipients']:
                    thread_user_info = ""
                    if type(thread_in) == dict:
                        thread_user_info = thread_in
                    else:
                        thread_user_info = json.loads(thread_in)
                    data_list_temp = []
                    for user_fields in thread_user_fields:
                        data_list_temp.append(thread_user_info.get(user_fields))
                    data_list.append(data_list_temp)
                if type(thread_info['inviter']) == dict:
                    thread_user_info = thread_info['inviter']
                else:
                    thread_user_info = json.loads(thread_info['inviter'])
                data_list_temp = []
                for user_fields in thread_user_fields:
                    data_list_temp.append(thread_user_info.get(user_fields))
                data_list.append(data_list_temp)

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Instragram - Users'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Instragram - Users'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Instragram - Users available')
                

        db.close
        
    return