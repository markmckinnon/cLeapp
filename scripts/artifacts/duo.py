import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, usergen

def get_duo(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('tachyon.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select 
        datetime(system_contact_last_update_millis/1000, "unixepoch"),
        user_id,
        contact_display_name
        FROM duo_users
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Duo Contacts')
            report.start_artifact_report(report_folder, 'Duo Contacts')
            html_report = report.get_report_file_path()
            report.add_script()
            data_headers = ('Last System Contact Update', 'User ID', 'Contact Display Name') 
            data_list = []
            data_list_usernames = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2]))
                data_list_usernames.append((row[1], 'Duo Contacts', 'DUO', html_report, f'Display Name: {row[2]}, Last System Contact Update: {row[0]}'))
    
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Duo Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Duo Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            usergen(report_folder, data_list_usernames)
            
        else:
            logfunc('No Duo Contacts data available')
        
        db.close()
        
    