import os
import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db

def get_editor(file_found):
    if 'slides' in file_found.lower():
        return 'Google Slides'
    elif 'sheets' in file_found.lower():
        return 'Google Sheets'
    else:
        return 'Google Docs'

def get_googleDocs(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if (file_name.lower().endswith('doclist.db')):
            app_name = get_editor(file_found)
            db = open_sqlite_db_readonly(file_name)
            cursor = db.cursor()
            cursor.execute('''
                        select accountHolderName, dbFilePath, datetime(lastAppMetadataSyncTime/1000, 'unixepoch') as LastAppMetadataSynctime
                          from appMetadata244, account244
                         where account_id = account;''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:
                report = ArtifactHtmlReport(f'{app_name} - Metadata Files')
                report.start_artifact_report(report_folder, f'{app_name} - Metadata Files')
                report.add_script()
                data_headers = ('account_holder_name', 'db_file_path', 'LastAppMetadataSynctime')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'{app_name} - Metadata Files'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)

                tlactivity = f'{app_name} - Metadata Files'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc(f'No {app_name} - Metadata Files found')

            db.close

            continue
        if (file_name.lower().endswith('storage.db')): # skip -journal and other files
            app_name = get_editor(file_found)
            db = open_sqlite_db_readonly(file_name)
            cursor = db.cursor()
            cursor.execute('''
                        select path, sizeInBytes, key, type  
                          from stash
                          left join DocumentStorageMetadata on stashId = stash.rowid;''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:
                report = ArtifactHtmlReport(f'{app_name} - Stash Files')
                report.start_artifact_report(report_folder, f'{app_name} - Stash Files')
                report.add_script()
                data_headers = ('path', 'size_in_bytes', 'key', 'type')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'{app_name} - Stash Files'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)

                tlactivity = f'{app_name} - Stash Files'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc(f'No {app_name} - Stash Files found')

            db.close
            continue

    return