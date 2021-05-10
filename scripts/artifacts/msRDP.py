import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_msRDP(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('RDPConnection.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            select  
            username,
            password,
            servername,
            servername_friendly,
            screenshot_table_id,
            screenshot_data
            from credential_table, connection_table, screenshot_table
            where credential_table.credential_table_id = connection_table.credential_id
            and screenshot_table.screenshot_table_id = connection_table.connection_table_id 
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Microsoft RDP')
            report.start_artifact_report(report_folder, 'Microsoft RDP')
            report.add_script()
            
            for row in all_rows:
                blob = row[5]
                blobid = row[4]
                writtento = os.path.join(report_folder,blobid + '.png')
                with open(f'{writtento}', 'wb') as file:
                    file.write(blob)
                blob_location = f'<a href="{writtento}"><img src="{writtento}"></a>'
                
                data_list.append((row[0], row[1], row[2], row[3], row[4], blob_location,))
            
            
            
            data_headers = ('Username','Password','Servername','Servername Friendly','Screenshot ID','Screenshot')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Microsoft RDP'
            tsv(report_folder, data_headers, data_list, tsvname)
    
        else:
            logfunc('No Microsoft RDP Data available')