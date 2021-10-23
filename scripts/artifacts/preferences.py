import os
import json
import textwrap
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, get_browser_name


def date_from_webkit(webkit_timestamp):
    epoch_start = datetime.datetime(1601,1,1)
    delta = datetime.timedelta(microseconds=int(webkit_timestamp))
    timewk = (epoch_start + delta)
    return timewk

def get_preferences(files_found, report_folder, seeker, wrap_text):
    accounts_data_list = []
    arc_data_list =[]
    apps_data_list = []
    settings_list = []
    ext_data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, "rb") as f:
            data = json.load(f)
            
        for x, y in data.items():
            
            if x == 'account_info':
                for list in y:
                    account_id = list.get('account_id')
                    email = list.get('email')
                    full_name = list.get('full_name')
                    given_name = list.get('given_name')
                    hd = list.get('hd')
                    is_child_account = list.get('is_child_account')
                    locale = list.get('locale')
                    is_under_advanced_protection = list.get('is_under_advanced_protection')
                    last_downloaded_image_url_with_size = list.get('last_downloaded_image_url_with_size')
                    picture_url = list.get('picture_url')
                    
                    accounts_data_list.append((account_id, email, full_name, given_name, hd, is_child_account, locale, is_under_advanced_protection, last_downloaded_image_url_with_size, picture_url))
                    
            if x == 'arc': #Android Runtime Chrome OS
                apps = y.get('apps') 
                if apps:
                    for appskeys, appsvalues in apps.items():
                        lastlaunchtime = appsvalues.get('lastlaunchtime')
                        if lastlaunchtime not in ( 0, None, ''):
                            lastlaunchtime = date_from_webkit(lastlaunchtime)
                        
                        install_time = appsvalues.get('install_time')
                        if install_time not in ( 0, None, ''):
                            install_time = date_from_webkit(install_time)
                            
                        name = appsvalues.get('name')
                        package_name = appsvalues.get('package_name')
                        activity = appsvalues.get('activity')
                        launchable = appsvalues.get('launchable')
                        notifications_enabled = appsvalues.get('notifications_enabled')
                        suspended = appsvalues.get('suspended')
                        appid = appskeys
                        
                        arc_data_list.append((install_time,lastlaunchtime,name,package_name,activity,launchable, notifications_enabled,suspended,appid))
                        
                backup_restore = y.get('backup_restore')
                settings_list.append(('backup_restore', backup_restore))
            
                location_service = y.get('location_service')
                settings_list.append(('location_service', location_service))
            
                serialno = y.get('serialno')
                settings_list.append(('serialno', serialno))
            
                signedin = y.get('signedin')
                settings_list.append(('signedin', signedin))
            
                framework = y.get('framework')
                settings_list.append(('framework', framework))
            
                initial = y.get('initial')
                settings_list.append(('initial', initial))
            
                metrics = y.get('metrics')
                settings_list.append(('metrics', metrics))
            
                pai = y.get('pai')
                settings_list.append(('pai', pai))
            
                terms = y.get('terms')
                settings_list.append(('terms', terms))
            
                vpn = y.get('vpn')
                settings_list.append(('vpn', vpn))
            
                visible_external_storages = y.get('visible_external_storages')
                settings_list.append(('visible_external_storages ', visible_external_storages ))
            
            if x == 'app_list':
                local_state = y.get('local_state')
                for local_state_keys, local_state_values in local_state.items():
                    appid_lsv = local_state_keys
                    name_lsv = local_state_values.get('name')
                    
                    apps_data_list.append((name_lsv, appid_lsv))
                    
            if x == 'account_manager':
                account_manager = y
                settings_list.append(('account_manager', account_manager ))
                
            if x == 'account_tracker_service_last_update':
                account_tracker_service_last_update = y
                settings_list.append(('account_tracker_service_last_update', account_tracker_service_last_update ))
                
            if x == 'alternate_error_pages':
                alternate_error_pages = y
                settings_list.append(('alternate_error_pages', alternate_error_pages ))
                
            if x == 'android_sms':
                android_sms = y
                settings_list.append(('android_sms', android_sms ))
                
            if x == 'ash':
                ash = y
                settings_list.append(('ash', ash ))
                
            if x == 'countryid_at_install':
                countryid_at_install = y
                settings_list.append(('countryid_at_install', countryid_at_install ))
                
            if x == 'credentials_enable_autosignin':
                credentials_enable_autosignin = y 
                settings_list.append(('credentials_enable_autosignin', credentials_enable_autosignin ))
                
            if x == 'credentials_enable_service':
                credentials_enable_service = y
                settings_list.append(('credentials_enable_service', credentials_enable_service ))
                
            if x == 'download':
                download = y
                settings_list.append(('download', download ))
                
            if x == 'drivefs':
                drivefs = y
                settings_list.append(('drivefs', drivefs ))
                
            if x == 'extensions':
                last_chrome_version = y.get('last_chrome_version')
                logdevinfo(f'Last Chrome Version: {last_chrome_version}')
                settings_list.append(('last_chrome_version', last_chrome_version ))
                
                for i in data['extensions']['settings']:
                    
                    ext_id = i
                
                    if 'install_time' in data['extensions']['settings'][i]:
                        install_time = data['extensions']['settings'][i].get('install_time','')
                        install_time_formatted = datetime.datetime.utcfromtimestamp((int(install_time)/1000000) - 11644473600).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        install_time_formatted = ''
                    
                    if 'manifest' in data['extensions']['settings'][i]:
                        ext_name = data['extensions']['settings'][i]['manifest'].get('name','')
                        ext_description = data['extensions']['settings'][i]['manifest'].get('description','')
                        ext_version = data['extensions']['settings'][i]['manifest'].get('version','')
                        ext_author = data['extensions']['settings'][i]['manifest'].get('author','')
                        ext_homepage = data['extensions']['settings'][i]['manifest'].get('homepage_url','')
                        ext_permissions = data['extensions']['settings'][i]['manifest'].get('permissions','')
                    else:
                        ext_name = ''
                        ext_description = ''
                        ext_version = ''
                        ext_author = ''
                        ext_homepage = ''
                        ext_permissions = ''
                        
                    if 'state' in data['extensions']['settings'][i]:
                        ext_state = data['extensions']['settings'][i].get('state','')
                        
                        if ext_state == 0:
                            ext_state_status = 'Disabled'
                        elif ext_state == 1:
                            ext_state_status = 'Enabled'
                    
                    if 'was_installed_by_default' in data['extensions']['settings'][i]:
                        was_installed_by_default = str(data['extensions']['settings'][i].get('was_installed_by_default',''))
                        was_installed_by_default = was_installed_by_default.title()
                    else:
                        was_installed_by_default = ''
                        
                    if 'was_installed_by_oem' in data['extensions']['settings'][i]:
                        was_installed_by_oem = str(data['extensions']['settings'][i].get('was_installed_by_oem',''))
                        was_installed_by_oem = was_installed_by_oem.title()
                    else:
                        was_installed_by_oem = '' 
                        
                    if 'from_bookmark' in data['extensions']['settings'][i]:
                        from_bookmark = str(data['extensions']['settings'][i].get('from_bookmark',''))
                        from_bookmark = from_bookmark.title()
                    else:
                        from_bookmark = ''  
                        
                    if 'from_webstore' in data['extensions']['settings'][i]:
                        from_webstore = str(data['extensions']['settings'][i].get('from_webstore',''))
                        from_webstore = from_webstore.title()
                    else:
                        from_webstore = ''                      
                    
                    ext_data_list.append((install_time_formatted,ext_name,ext_description,ext_version,ext_id,ext_author,ext_homepage,ext_state_status,was_installed_by_default,was_installed_by_oem,from_bookmark,from_webstore,ext_permissions))
                
            if x == 'google':
                google = y
                settings_list.append(('google', google ))
                
            if x == 'homepage':
                homepage = y
                settings_list.append(('homepage', homepage ))
                
            if x == 'homepage_is_newtabpage':
                homepage_is_newtabpage = y
                settings_list.append(('homepage_is_newtabpage', homepage_is_newtabpage ))
                
            if x == 'intl':
                intl = y
                settings_list.append(('intl', intl ))
                
            if x == 'launcher':
                launcher = y
                settings_list.append(('launcher', launcher ))
                
            if x == 'pinned_tabs':
                pinned_tabs = y
                settings_list.append(('pinned_tabs', pinned_tabs ))
                
            if x == 'oobe':
                oobe = y
                settings_list.append(('oobe', oobe ))
                
            if x == 'session':
                session = y
                settings_list.append(('session', session ))
                
            if x == 'settings':
                settings = y.get('settings')
                settings_list.append(('settings', settings ))
                
            if x == 'spellcheck':
                spellcheck = y
                settings_list.append(('spellcheck', spellcheck ))
                
    if len(accounts_data_list) > 0:
        report = ArtifactHtmlReport('Accounts Data')
        report.start_artifact_report(report_folder, 'Accounts Data')
        report.add_script()
        data_headers = ('Account ID','Email','Full Name','Given Name','HD','Is Child Account','Locale','Is Under Adv. Protection','Last Image','Picture URL')
        report.write_artifact_data_table(data_headers, accounts_data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Preferences Accounts Data'
        tsv(report_folder, data_headers, accounts_data_list, tsvname)

    else:
        logfunc('No Preferences Accounts Data available')
    
    if len(arc_data_list) > 0:
        report = ArtifactHtmlReport('ARC App List')
        report.start_artifact_report(report_folder, 'ARC App List')
        report.add_script()
        data_headers = ('Install Time','Last Launch Time','Name','Package Name','Activity','Launchable','Notifications Enabled','Suspended','App ID')
        report.write_artifact_data_table(data_headers, arc_data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'ARC App List Data'
        tsv(report_folder, data_headers, arc_data_list, tsvname)
        
        tlactivity = 'ARC App List Data'
        timeline(report_folder, tlactivity, arc_data_list, data_headers)
        
    else:
        logfunc('No Preferences ARC App List Data available')
    
    if len(apps_data_list) > 0:
        report = ArtifactHtmlReport('App List')
        report.start_artifact_report(report_folder, 'App List')
        report.add_script()
        data_headers = ('Name','App ID')
        report.write_artifact_data_table(data_headers, apps_data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'App List Data'
        tsv(report_folder, data_headers, apps_data_list, tsvname)
        
    else:
        logfunc('No Preferences App List Data available')
    
    if len(settings_list) > 0:
        report = ArtifactHtmlReport('Preferences')
        report.start_artifact_report(report_folder, 'Preferences')
        report.add_script()
        data_headers = ('Key','Value')
        report.write_artifact_data_table(data_headers, settings_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Preferences'
        tsv(report_folder, data_headers, settings_list, tsvname)
        
    if len(ext_data_list) > 0:
        report = ArtifactHtmlReport('Extensions')
        report.start_artifact_report(report_folder, 'Extensions')
        report.add_script()
        data_headers = ('Install Time','Extension Name','Description','Version','Extension ID','Author','Homepage','State','Installed by Default','Installed by OEM','From Bookmark','From Webstore','Permissions')
        report.write_artifact_data_table(data_headers, ext_data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Extensions'
        tsv(report_folder, data_headers, ext_data_list, tsvname)
        
        tlactivity = 'Extensions'
        timeline(report_folder, tlactivity, ext_data_list, data_headers)   
        
    else:
        logfunc('No Preferences Extensions Data available')