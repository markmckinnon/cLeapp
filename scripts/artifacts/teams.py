import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_teams(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('SkypeTeams.db'):
            continue # Skip all other files

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime("arrivalTime"/1000, 'unixepoch'),
        userDisplayName,
        content,
        displayName,
        datetime("deleteTime"/1000, 'unixepoch'),
        Message.conversationId,
        messageId
        FROM Message
        left join Conversation
        on Message.conversationId = Conversation.conversationId
        ORDER BY  Message.conversationId, arrivalTime
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Teams Messages')
            report.start_artifact_report(report_folder, 'Teams Messages')
            report.add_script()
            data_headers = ('Timestamp','User Display Name','Content','Topic Name','Delete Time','Conversation ID','Message ID')
            data_list=[]
            for row in all_rows:
                timeone = row[0]
                timetwo = row[4]
                if timeone == '1970-01-01 00:00:00':
                    timeone = ''
                if timetwo == '1970-01-01 00:00:00':
                    timetwo = ''
                data_list.append((timeone, row[1], row[2], row[3], timetwo, row[5], row[6]))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Teams Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Teams Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Teams Messages data available')

    db.close()
    