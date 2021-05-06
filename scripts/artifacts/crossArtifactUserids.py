import sqlite3
import textwrap
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, usergen

def get_crossArtifactUserids(files_found, report_folder, seeker, wrap_text):

    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    udb_report_folder = os.path.join(report_folder_base, '_Usernames DB')
    udb_database_file = os.path.join(udb_report_folder, '_usernames.db')
    db = open_sqlite_db_readonly(udb_database_file)
    cursor = db.cursor()
    cursor.execute('''  
             select distinct username, appname, '<b><a href="'||html_report||'">'||artifactname||'</a></b>' as html_artifact_name, 
                    artifactname, data from data;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Cross Artifact Userids')
        report.start_artifact_report(report_folder, 'Cross Artifact Userids')
        report.add_script()
        data_headers = ('user_name', 'app_name', 'artifact reference', 'other user information')
        data_list_html = []
        data_list = []
        for row in all_rows:
            data_list_html.append((row[0],row[1],row[2],row[4]))
            data_list.append((row[0],row[1],row[3],row[4]))
        report.write_artifact_data_table(data_headers, data_list_html, udb_database_file, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Cross Artifact Userids'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Cross Artifact Userids'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Cross Artifact Userids data available')

    db.close()
        
    