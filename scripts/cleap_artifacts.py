

# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.accounts_ce import get_accounts_ce
from scripts.artifacts.accounts_ce_authtokens import get_accounts_ce_authtokens
from scripts.artifacts.accounts_de import get_accounts_de
from scripts.artifacts.Cast import get_Cast
from scripts.artifacts.chrome import get_chrome
from scripts.artifacts.chromeDownloads import get_chromeDownloads
from scripts.artifacts.chromeCookies import get_chromeCookies
#from scripts.artifacts.chromeAutofill import get_chromeAutofill
from scripts.artifacts.chromeLoginData import get_chromeLoginData
from scripts.artifacts.chromeBookmarks import get_chromeBookmarks
from scripts.artifacts.chromeOmnibox import get_chromeOmnibox
from scripts.artifacts.chromeSearchTerms import get_chromeSearchTerms
from scripts.artifacts.chromeTopSites import get_chromeTopSites
from scripts.artifacts.chromeWebsearch import get_chromeWebsearch
from scripts.artifacts.chromeNetworkActionPredictor import get_chromeNetworkActionPredictor
from scripts.artifacts.customDict import get_customDict
from scripts.artifacts.providerDownloader import get_providerDownloaders
from scripts.artifacts.eventlog import get_eventlog
from scripts.artifacts.favicons import get_favicons
from scripts.artifacts.fsData import get_fsData
from scripts.artifacts.gmsDownloads import get_gmsDownloads
from scripts.artifacts.gmsPluscontacts import get_gmsPluscontacts
from scripts.artifacts.preferences import get_preferences
from scripts.artifacts.recentactivity import get_recentactivity
from scripts.artifacts.teams import get_teams
from scripts.artifacts.vpd import get_vpd
from scripts.artifacts.paloAltoGlobalProtect import get_paloAltoGlobalProtect
from scripts.artifacts.LocalStorage import get_LocalStorage
from scripts.artifacts.firefox import get_firefox
from scripts.artifacts.firefoxDownloads import get_firefoxDownloads
from scripts.artifacts.firefoxCookies import get_firefoxCookies
from scripts.artifacts.contacts import get_contacts

from scripts.cleapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex_term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

tosearch = {
# Accounts
    'accounts_ce': ('Accounts', '**/system_ce/*/accounts_ce.db'),
#    'accounts_ce_authtokens':('Accounts', '**/accounts_ce.db'),
    'accounts_de': ('Accounts', '**/system_de/*/accounts_de.db'),
    'Cast':('Android GMS', '*/com.google.android.gms/databases/cast.db'),
# Browsers 
    'chrome':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeDownloads':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeCookies':('Browser', ('**/mount/user/Cookies*',  '**/chronos/LockScreenAppsProfile/Cookies*', '**/chronos/Default/Cookies*', '**/com.brave.browser/app_chrome/Default/Cookies*', '**/com.opera.browser/app_opera/Cookies*')),
    'chromeLoginData':('Browser', ('**/mount/user/Login Data*', '**/chronos/LockScreenAppsProfile/Login Data*', '**/chronos/Default/Login Data*', '**/com.brave.browser/app_chrome/Default/Login Data*', '**/com.opera.browser/app_opera/Login Data*')),
#    'chromeAutofill':('Browser', ('**/mount/user/Web Data*', '**/chronos/LockScreenAppsProfile/Web Data*', '**/chronos/Default/Web Data*', '**/com.brave.browser/app_chrome/Default/Web Data*')),
    'chromeSearchTerms':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeWebsearch':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
#   'chromium_bookmarks':('Browser', '**/mount/user/Bookmarks'),
    'chromeTopSites':('Browser', ('**/mount/user/Top Sites*', '**/chronos/LockScreenAppsProfile/Top Sites*', '**/chronos/Default/Top Sites*', '**/com.brave.browser/app_chrome/Default/Top Sites*', '**/com.opera.browser/app_opera/Top Sites*')),
    'chromeNetworkActionPredictor':('Browser', ('*/mount/user/Network Action Predictor*','*/chronos/LockScreenAppsProfile/Network Action Predictor*', '*/chronos/Default/Network Action Predicator*', '**/com.brave.browser/app_chrome/Default/Network Action Predicator*')),
    'chromeOmnibox':('Browser', ('*/mount/user/Shortcuts*','*/chronos/LockScreenAppsProfile/Shortcuts*', '*/chronos/Default/Shortcuts*', '**/com.brave.browser/app_chrome/Default/Shortcuts*')),
    'customDict':('User Settings', '*/mount/user/Custom Dictionary.txt'),
    'eventlog':('Logs', '*/var/log/eventlog.txt'),
    'favicons':('Browser', ('*/mount/user/Favicons*','*/chronos/LockScreenAppsProfile/Favicons*', '*/chronos/Default/Favicons*')),
    'fsData':('Settings', '*/filesystem-details.txt'),
    'gmsPluscontacts':('Android GMS', '*/data/com.google.android.gms/databases/pluscontacts.db*'),
    'gmsDownloads':('Android GMS', '*/data/com.google.android.gms/databases/downloads.db*'),
    'preferences':('Preferences', '*/mount/user/Preferences'),
    'recentactivity':('Recent Activity', '*/system_ce/*'),
    'teams':('Teams', '*/com.microsoft.teams/databases/SkypeTeams.db*'),
    'vpd':('Settings', '*/vpd/full-v2.txt'),
    'providerDownloaders':('Downloads', '*/com.android.providers.downloads/databases/downloads.db*'),
    'paloAltoGlobalProtect':('VPNs', ('*/com.paloaltonetworks.globalprotect/files/pan_gp_event.log', '*/com.paloaltonetworks.globalprotect/files/pan_gp_hrpt.xml')),
    # For Level db put the location of the CURRENT File in and the directory will get processed
    'LocalStorage':('LevelDb', '**/Local Storage/leveldb/**'),
    'firefox':('Browser', '**/org.mozilla.firefox/files/places.sqlite*'),
    'firefoxDownloads':('Browser', '**/org.mozilla.firefox/files/places.sqlite*'),
    'firefoxCookies':('Browser', '**/org.mozilla.firefox/databases/mozac_downloads_database*'),
    'contacts':('Contacts', ('**/com.android.providers.contacts/databases/contact*', '**/com.android.providers.contacts/databases/profile*')),
}

slash = '\\' if is_platform_windows() else '/'

def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base, output_type):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
            
            wrap_text: whether the text data will be wrapped or not using textwrap.  Useful for tools that want to parse the data.
    '''
    logfunc('{} [{}] artifact executing'.format(artifact_name, artifact_func))
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        return
    try:
        method = globals()['get_' + artifact_func]
        method(files_found, report_folder, seeker, output_type)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    logfunc('{} [{}] artifact completed'.format(artifact_name, artifact_func))
    