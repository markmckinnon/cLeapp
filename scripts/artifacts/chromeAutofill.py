import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, does_column_exist_in_db, open_sqlite_db_readonly, get_browser_name

def get_chromeAutofill(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data': # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute(f'''
        select
            datetime(date_created, 'unixepoch'),
            name,
            value,
            datetime(date_last_used, 'unixepoch'),
            count
        from autofill
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} Autofill')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Autofill.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Date Created','Field','Value','Date Last Used','Count')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Autofill'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Autofill'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} Autofill data available')
        
        cursor.execute(f'''
        select
            datetime(date_modified, 'unixepoch'),
            autofill_profiles.guid,
            autofill_profile_names.first_name,
            autofill_profile_names.middle_name,
            autofill_profile_names.last_name,
            autofill_profile_emails.email,
            autofill_profile_phones.number,
            autofill_profiles.company_name,
            autofill_profiles.street_address,
            autofill_profiles.city,
            autofill_profiles.state,
            autofill_profiles.zipcode,
            datetime(use_date, 'unixepoch'),
            autofill_profiles.use_count
        from autofill_profiles
        inner join autofill_profile_emails ON autofill_profile_emails.guid = autofill_profiles.guid
        inner join autofill_profile_phones ON autofill_profiles.guid = autofill_profile_phones.guid
        inner join autofill_profile_names ON autofill_profile_phones.guid = autofill_profile_names.guid
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} Autofill - Profiles')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Autofill - Profiles.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Date Modified','GUID','First Name','Middle Name','Last Name','Email','Phone Number','Company Name','Address','City','State','Zip Code','Date Last Used','Use Count')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Autofill - Profiles'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Autofill - Profiles'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} Autofill - Profiles data available')
        
        db.close()
