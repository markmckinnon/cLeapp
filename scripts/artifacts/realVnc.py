import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name

def get_realVnc(files_found, report_folder, seeker, wrap_text):
    data_list = []
    file_path = ""
    for file_found in files_found:
        file_found = str(file_found)
        file_parts = os.path.split(file_found)
        file_name = file_parts[1]
        file_path = file_parts[0]
        if file_found.lower().endswith('.vnc'):
            vncSettings = {}
            with open(file_found, "r") as vncfile:
                for line in vncfile:
                    vncline = line.split('=')
                    if len(vncline) == 2:
                         vncSettings[vncline[0]] = vncline[1].replace("\n", "")
            if len(vncSettings) > 0:
                vncSettings["FileName"] = file_name
                data_list.append(vncSettings)

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Real VNC Settings')
        report.start_artifact_report(report_folder, 'Real VNC Settings')
        report.add_script()
        all_data = []
        data_headers = ('fileName','Host', 'ConnTime', 'FriendlyName', 'UserName', 'ConnMethod', 'Uuid', 'BrowsedUuid')
        for vncSettingList in data_list:
            list_data = ((vncSettingList.get("FileName"), vncSettingList.get("Host"), vncSettingList.get("ConnTime"), vncSettingList.get("FriendlyName"), vncSettingList.get("UserName"), vncSettingList.get("ConnMethod"), vncSettingList.get("Uuid"), vncSettingList.get("BrowsedUuid")))
            all_data.append(list_data)
        report.write_artifact_data_table(data_headers, all_data, os.path.join(file_path, "*.vnc"), html_escape=False)
        report.end_artifact_report()

        tsvname = 'Real VNC Settings'
        tsv(report_folder, data_headers, all_data, tsvname)
    else:
        logfunc('No Real VNC Settings Report Data available')
