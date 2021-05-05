import os
import sqlite3
import datetime
from scripts.artifacts.appCookies import get_appCookies

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db

def get_quickedit(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if (file_name.lower().endswith('cookies')):
            get_appCookies(file_found, report_folder, seeker, wrap_text, "Quickedit")
            continue
        if not os.path.basename(file_name) == 'edit.db': # skip -journal and other files
            continue

        source_file = file_found.replace(seeker.directory, '')

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        cursor.execute('''
                    SELECT path, datetime(date_opened, 'unixepoch') as date_opened
                      FROM recent_files;''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            report = ArtifactHtmlReport('Quickedit - Recent Files')
            report.start_artifact_report(report_folder, 'Quickedit - Recent Files')
            report.add_script()
            data_headers = ('path','date_opened') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Quickedit - Recent Files'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)

            tlactivity = f'Quickedit - Recent Files'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Quickedit Recent Files found')

        db.close
    
    return