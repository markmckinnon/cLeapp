import sqlite3
import textwrap
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, usergen

def get_crossArtifactTimeline(files_found, report_folder, seeker, wrap_text):

    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    udb_report_folder = os.path.join(report_folder_base, '_Timeline')
    udb_database_file = os.path.join(udb_report_folder, 'tl.db')
    db = open_sqlite_db_readonly(udb_database_file)
    cursor = db.cursor()
    cursor.execute('''  
             select key, activity, datalist from data;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Cross Artifact Timeline')
        report.start_artifact_report(report_folder, 'Cross Artifact Timeline')
        report.add_script()
        data_headers = ('date_time', 'activity', 'data')
        data_list_html = []
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))
        report.write_artifact_data_table(data_headers, data_list, udb_database_file, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Cross Artifact Timeline'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Cross Artifact Timeline'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Cross Artifact Timeline data available')

    db.close()
        
    