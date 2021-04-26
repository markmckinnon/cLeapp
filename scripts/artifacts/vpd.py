import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_vpd(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    for file_found in files_found:
        file_found = str(file_found)
    
        with open(file_found, "r") as filefrom:
            for line in filefrom:
                ll = line.split('"="')
                key = ll[0].replace('"','')
                value = ll[1].replace('"','')
                
                if key == 'mlb_serial_number':
                    logdevinfo(f'MLB Serial Number: {value}')
                if key == 'serial_number':
                    logdevinfo(f'Serial Number: {value}')
                if key == 'region':
                    logdevinfo(f'Region: {value}')
                if key == 'customization_id':
                    logdevinfo(f'Customization ID: {value}')
                if key == 'rlz_brand_code':
                    logdevinfo(f'RLZ Brand Code: {value}')
                if key == 'ActivateDate':
                    logdevinfo(f'Activate Date: {value}')
                if key == 'model_name':
                    logdevinfo(f'Model Name: {value}')
                if key == 'initial_timezone':
                    logdevinfo(f'Initial Timezone: {value}')
                if key == 'keyboard_layout':
                    logdevinfo(f'Keyboard Layout: {value}')
                    
                data_list.append((key, value))
        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('Vital Product Data')
            report.start_artifact_report(report_folder, 'Vital Product Data')
            report.add_script()
            data_headers = ('Key','Value')   
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Vital Product Data'
            tsv(report_folder, data_headers, data_list, tsvname)
    
        else:
            logfunc('No Vital Product Data available')