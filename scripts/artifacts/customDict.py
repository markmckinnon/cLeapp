import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_customDict(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    for file_found in files_found:
        file_found = str(file_found)
    
        with open(file_found, "r") as filefrom:
            for line in filefrom:
                if 'checksum_v1 =' in line:
                    pass
                else:
                    data_list.append((line,))
        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('Custom Dictionary')
            report.start_artifact_report(report_folder, 'Custom Dictionary')
            report.add_script()
            data_headers = ('Value',)   
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Custom Dictionary'
            tsv(report_folder, data_headers, data_list, tsvname)
    
        else:
            logfunc('No Custom Dictionary Data available')