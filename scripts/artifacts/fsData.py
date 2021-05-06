import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_fsData(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "r") as filefrom:
            for line in filefrom:
                if ':' in line:
                    ll = line.split(':')
                    key = ll[0]
                    value = ll[1]
                    
                    if key == 'Last mount time':
                        logdevinfo(f'File System Last Mount Time: {value}')
                    if key == 'Last write time':
                        logdevinfo(f'File System Last Write Time: {value}')
                    if key == 'Mount count':
                        logdevinfo(f'File System Mount Count: {value}')
                    if key == 'Filesystem OS type':
                        logdevinfo(f'Filesystem OS Type: {value}')
                        
                    data_list.append((key, value))
                else:
                    data_list.append((line, ''))
        
    if len(data_list) > 0:
        report = ArtifactHtmlReport('File System Data')
        report.start_artifact_report(report_folder, 'File System Data')
        report.add_script()
        data_headers = ('Key','Value')   
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'File System Data'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc('No File System Data available')