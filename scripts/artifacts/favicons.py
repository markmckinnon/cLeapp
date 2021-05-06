import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_favicons(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Favicons'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        page_url,
        url,
        image_data,
        datetime(last_updated / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch"),
        datetime(last_requested / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        FROM icon_mapping, favicons, favicon_bitmaps
        WHERE icon_mapping.icon_id = favicon_bitmaps.icon_id and favicons.id = icon_mapping.icon_id
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        blobid = 0
        if usageentries > 0:
            report = ArtifactHtmlReport('Favicons')
            report.start_artifact_report(report_folder, 'Favicons')
            report.add_script()
            
            for row in all_rows:
                blob = row[2]
                blobid = blobid + 1
                writtento = f'{report_folder}/fav{blobid}.png'
                with open(f'{writtento}', 'wb') as file:
                    file.write(blob)
                blob_location = f'<a href="{writtento}"><img src="{writtento}"></a>'
                
                if row[3] == '1601-01-01 00:00:00':
                    updated = ''
                else:
                    updated = row[3]
                    
                if row[4] == '1601-01-01 00:00:00':
                    requested = ''
                else:
                    requested = row[4]
                
                if wrap_text:
                    data_list.append(((textwrap.fill(row[0], width=50)),(textwrap.fill(row[0], width=100)),blob_location,updated,requested))
                else:
                    data_list.append((row[0],row[1],blob_location,updated,requested))
            
            
            data_headers = ('Page URL','URL','Favicon','Last Updated','Last Requested')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Favicons'
            tsv(report_folder, data_headers, data_list, tsvname)
    
        else:
            identifier = file_found.split(os.sep)
            identifier = str(identifier[-3:])
            logfunc(f'No Favicons {identifier} Data available')