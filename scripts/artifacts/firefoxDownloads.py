import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, does_column_exist_in_db, open_sqlite_db_readonly, get_browser_name

def get_firefoxDownloads(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'mozac_downloads_database': # skip -journal and other files
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT url, file_name, destination_directory, 
                   ((created_at/1000000) - 11644473600) as created_at,
                   content_length, content_type
              FROM downloads
              ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox Downloads')
            report.start_artifact_report(report_folder, 'Firefox Downloads')
            report.add_script()
            data_headers = ('url', 'file_name', 'destination_directory', 'created_at', 'content_length', 'content_type')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Firefox Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Firefox Downloads'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox download data available')
        
        db.close()
