import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, usergen

def get_chromeSync(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('chromesync.data_store'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
                select idx_origin, idx_signon_realm, idx_username from password_index;
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Chrome Synced Users')
            report.start_artifact_report(report_folder, 'Chrome Synced Users')
            html_report = report.get_report_file_path()
            report.add_script()
            data_headers = ('url origin', 'url realm', 'username')
            data_list = []
            data_list_usernames = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2]))
                data_list_usernames.append((row[2], row[2], 'ChronmeSync', html_report, ''))
    
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Chrome Synced Users'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Chrome Synced Users'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            usergen(report_folder, data_list_usernames)
            
        else:
            logfunc('No Chrome Synced Users data available')
        
        db.close()
        
    