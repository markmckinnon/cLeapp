import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly, usergen

def get_accounts_ce(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/' 

    # Filter for path xxx/yyy/system_ce/0
    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-2]
        try:
            uid_int = int(uid)
            # Skip sbin/.magisk/mirror/data/system_de/0 , it should be duplicate data??
            if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                continue
            process_accounts_ce(file_found, uid, report_folder)
        except ValueError:
                pass # uid was not a number

def process_accounts_ce(folder, uid, report_folder):
    
    #Query to create report
    db = open_sqlite_db_readonly(folder)
    cursor = db.cursor()

    #Query to create report
    cursor.execute('''
    SELECT
        name,
        type,
        password
    FROM
    accounts
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Accounts_ce')
        report.start_artifact_report(report_folder, f'accounts_ce_{uid}')
        html_report = report.get_report_file_path()
        report.add_script()
        data_headers = ('Name', 'Type', 'Password')
        data_list = []
        data_list_usernames = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
            data_list_usernames.append((row[0], row[1], 'Accounts_ce', html_report, f'Password: {row[2]}, Artifact: accounts_ce {uid}'))
        report.write_artifact_data_table(data_headers, data_list, folder)
        report.end_artifact_report()
        
        tsvname = f'accounts ce {uid}'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        usergen(report_folder, data_list_usernames)
        
    else:
        logfunc(f'No accounts_ce_{uid} data available')    
    db.close()