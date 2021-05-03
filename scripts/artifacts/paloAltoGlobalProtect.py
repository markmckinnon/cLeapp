import os
import textwrap
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_paloAltoGlobalProtect(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        data_list = []
        file_found = str(file_found)
        if 'pan_gp_hrpt.xml' in file_found.lower():
            tree = ET.parse(file_found)
            root = tree.getroot()
            for elem in root.iter():
                if elem.text is not None and '\t' not in elem.text and '\n' not in elem.text:
                    data_list.append((elem.tag, elem.text))
        
            if len(data_list) > 0:
                report = ArtifactHtmlReport('Palo Alto Global Protect Hip Report')
                report.start_artifact_report(report_folder, 'Palo Alto Global Protect Hip Report')
                report.add_script()
                data_headers = ('Key','Value')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()

                tsvname = 'Palo Alto Global Protect Hip Report'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc('No Palo Alto Global Protect Hip Report Data available')

        if 'pan_gp_event.log' in file_found.lower():
           with open(file_found, "r") as logfile:
               for line in logfile:
                   logline = line.split("[")
                   data_list.append((logline[0], "[" + logline[1]))

                   if len(data_list) > 0:
                       report = ArtifactHtmlReport('Palo Alto Global Protect Event Log')
                       report.start_artifact_report(report_folder, 'Palo Alto Global Protect Event Log')
                       report.add_script()
                       data_headers = ('Date/Time', 'Event Message')
                       report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                       report.end_artifact_report()

                       tsvname = 'Palo Alto Global Protect Event Log'
                       tsv(report_folder, data_headers, data_list, tsvname)

                   else:
                       logfunc('No Palo Alto Global Protect Event Log Data available')

