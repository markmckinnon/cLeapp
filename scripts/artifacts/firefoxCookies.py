import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_firefoxCookies(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'cookies.sqlite': # skip -journal and other files
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''SELECT name, value, host, path, expiry, 
                  ((lastAccessed/1000000) - 11644473600) as lastAccessed, 
                  ((creationTime/1000000) - 11644473600) as creationTime,
                   isSecure, isHttpOnly FROM moz_cookies
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox Cookies')
            report.start_artifact_report(report_folder, 'Firefox Cookies')
            report.add_script()
            data_headers = ('name', 'value', 'host', 'path', 'expiration', 'last_accessed', 'creation_time', 'is_secure', 'is_http_only')
            data_list = []
            for row in all_rows:
                if wrap_text:
                    data_list.append((row[0],row[1],(textwrap.fill(row[2], width=50)),row[3],row[4],row[5],row[6], row[7], row[8]))
                else:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6], row[7], row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Firefox cookies'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Firefox Cookies'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox cookies data available')
        
        db.close()
