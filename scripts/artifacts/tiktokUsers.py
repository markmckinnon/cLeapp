import sqlite3
import datetime
import os
import json
from scripts.artifacts.appCookies import get_appCookies

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_tiktokUsers(files_found, report_folder, seeker, wrap_text):

    user_id = None
    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if ('wal' in file_name.lower() and ('shm') in file_name.lower()):
            continue
        elif (file_name.lower().endswith('cookies')):
            get_appCookies(file_found, report_folder, seeker, wrap_text, "TikTok")

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
            
        try:
            cursor.execute('''
                         select uid, nick_name, signature, unique_id, 
                                datetime(user_follow_time, 'unixepoch') as user_follow_time
                           from simple_user;
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('TikTok - Users')
            report.start_artifact_report(report_folder, 'TikTok - Users')
            report.add_script()
            data_headers = ('uid', 'nick_name', 'signature', 'unique_id', 'user_follow_time') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'TikTok - Users'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'TikTok - Users'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No TikTok - Users available')
                

        db.close
        
    return