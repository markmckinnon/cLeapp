import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_eventlog(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    for file_found in files_found:
        file_found = str(file_found)
    
        with open(file_found, "r") as filefrom:
            for line in filefrom:
                ll = line.split('|')
                
                timestamp = ll[1]
                eventorder = ll[0]
                notice = ll[2]
                
                try:
                    detail = ll[3]
                except:
                    detail = ''
                    
                try:
                    extra = ll[4]
                except:
                    extra = ''
                    
                    
                data_list.append((timestamp, eventorder, notice, detail, extra))
        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('Chrome OS Event Log')
            report.start_artifact_report(report_folder, 'Chrome OS Event Log')
            report.add_script()
            data_headers = ('Timestamp','Event Order', 'Notice', 'Detail', 'More Detail')   
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Chrome OS Event Log'
            tsv(report_folder, data_headers, data_list, tsvname)
    
        else:
            logfunc('No Chrome OS Event Log Data available')