import sqlite3
import datetime
import os
import json
from scripts.artifacts.appCookies import get_appCookies

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, clean_up_br

def get_instragramUsers(files_found, report_folder, seeker, wrap_text):

    thread_user_fields = ('username', 'full_name', 'profile_pic_url', 'profile_pic_id','id','is_private', 'is_verified')
    user_id = None
    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if (file_name.lower().endswith('-wal') or file_name.lower().endswith('-shm') or file_name.lower().endswith('-journal')):
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
            report = ArtifactHtmlReport('Instagram Users')
            report.start_artifact_report(report_folder, 'Instagram Users')
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
            
            tsvname = 'Instagram Users'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Instagram Users'
            timeline(report_folder, tlactivity, data_list, data_headers)
        
        if file_found.endswith('direct.db'):
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(timestamp / 1000000, "unixepoch"),
            user_id,
            recipient_ids, 
            text,
            message_type,
            message
            from messages
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list_messages = []
                convuserdict = {}
                data_list_no_br = []
                
                report = ArtifactHtmlReport('Instagram Threads')
                report.start_artifact_report(report_folder, 'Instagram Threads')
                report.add_script()
                
                for row in all_rows:
                    final = ''
                    recipients = row[2].split(",")
                    for ids in recipients:
                        for x in data_list:
                            if ids in x:
                                username = x[0]
                                fullname = x[1]
                                uid = x[4]
                                convuserdict[uid] = f'{username} <br>{fullname} <br>{uid}  <br><br>'
                        
                    for y in data_list:
                        if row[1] in y:
                            username = y[0]
                            fullname = y[1]
                            uid = y[4]
                            rowtwo = f'{username} <br>{fullname} <br>{uid}  <br><br>'
                                
                    for key, values in convuserdict.items():
                        final = final + values
                    convuserdict ={}
                    
                    message = json.loads(row[5])
                    originator = message['user_id']
                    
                    for z in data_list:
                        if originator in z:
                            username = z[0]
                            fullname = z[1]
                            uid = z[4]
                            origin = f'{username} <br>{fullname} <br>{uid}  <br><br>'
                            
                    data_list_messages.append((row[0], rowtwo, origin, final.lstrip(), row[3], row[4], row[5]))
                    
                    
                data_headers = ('Timestamp','User ID', 'Originator', 'Recipients','Message','Message Type', 'Message JSON')
                report.write_artifact_data_table(data_headers, data_list_messages, file_found, html_escape=False)
                report.end_artifact_report()
                
                clean_data_list = clean_up_br(data_list_messages)
                
                tsvname = 'Instagram Threads'
                tsv(report_folder, data_headers, clean_data_list , tsvname)
                
                tlactivity = f'Instagram Threads'
                timeline(report_folder, tlactivity, clean_data_list, data_headers)
                
                
            
        
                