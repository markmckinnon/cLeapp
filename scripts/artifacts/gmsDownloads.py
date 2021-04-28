import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_gmsDownloads(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('downloads.db'):
            continue # Skip all other files

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        filename,
        url,
        sizeBytes,
        sha1,
        destination,
        enabled,
        retries
        from downloads
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('GMS Downloads')
            report.start_artifact_report(report_folder, 'GMS Downloads')
            report.add_script()
            data_headers = ('Filename','URL','Bytes','SHA1','Destination','Enabled','Retries')
            data_list=[]
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'GMS Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc('No GMS Downloads data available')

    db.close()
    