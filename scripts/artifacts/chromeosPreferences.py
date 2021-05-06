import os
import textwrap
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, usergen

def get_chromeosPreferences(files_found, report_folder, seeker, wrap_text):
    data_list =[]
    preferences_dict = {}
    user_accounts = []
    for file_found in files_found:
        file_found = str(file_found)
    
        with open(file_found, "rb") as filefrom:
            xdata = filefrom.read()
            preferences_dict = json.loads(xdata)

        account_info = preferences_dict['account_info']
        for account in account_info:
            account_keys = account.keys()
            for key in account_keys:
                if key == "account_id":
                    user_accounts.append((account[key], 'ChromeOS', ''))
                data_list.append((key, account[key]))

        if len(data_list) > 0:
            report = ArtifactHtmlReport('ChromsOS Preferences')
            report.start_artifact_report(report_folder, 'ChromsOS Preferences')
            report.add_script()
            data_headers = ('Key', 'Value')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()

            usergen(report_folder,user_accounts)

            tsvname = 'ChromsOS Preferences'
            tsv(report_folder, data_headers, data_list, tsvname)
    
        else:
            logfunc('No ChromsOS Preferences Data available')