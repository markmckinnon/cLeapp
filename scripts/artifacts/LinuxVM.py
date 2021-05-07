import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline


def get_linuxVM(files_found, report_folder, seeker, wrap_text):

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.img'):
            data_list.append((file_found,))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Linux VM')
        report.start_artifact_report(report_folder, 'Linux VM')
        report.add_script()
        data_headers = ('Linux Virtual Machine Location',)
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsvname = 'Linux VM'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc('No Linux VM available')
