import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_providerDownloaders(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('downloads.db'):
            continue # Skip all other files

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select 
        datetime("lastmod"/1000, 'unixepoch'),
        title, 
        uri, 
        description,
        hint, 
        _data, 
        mimetype,
        total_bytes 
        from downloads;
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Provider Downloads')
            report.start_artifact_report(report_folder, 'Provider Downloads')
            report.add_script()
            data_headers = ('Last Modification Data','Title','URI','Description','Hint','File Location','Mimetype','Bytes')
            data_list=[]
            for row in all_rows:
                if wrap_text:
                    data_list.append((row[0], row[1], textwrap.fill(row[2], width=50), row[3], row[4], row[5], row[6], row[7]))
                else:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Provider Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Provider Downloads'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Provider Downloads data available')

    db.close()
    