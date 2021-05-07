import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline


def get_croshCommands(files_found, report_folder, seeker, wrap_text):

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, "r") as f:
            readline = f.read()
            command_list = readline.split('\n')
            for command in command_list:
                data_list.append((command,))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Crosh Commands')
        report.start_artifact_report(report_folder, 'Crosh Commands')
        report.add_script()
        data_headers = ('Commands Executed',)
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsvname = 'Crosh Commands'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc('No Crosh Commands available')
