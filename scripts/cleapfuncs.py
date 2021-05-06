import codecs
import csv
import datetime
import os
import pathlib
import re
import sqlite3
import sys
from bs4 import BeautifulSoup
try:
    import simplekml
except:
    pass

class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''
    
    def __init__(self, output_folder):
        now = datetime.datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        self.report_folder_base = os.path.join(output_folder, 'CLEAPP_Reports_' + currenttime) # cleapp , cleappGUI, cleap_artifacts, report.py
        self.temp_folder = os.path.join(self.report_folder_base, 'temp')
        OutputParameters.screen_output_file_path = os.path.join(self.report_folder_base, 'Script Logs', 'Screen Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(self.report_folder_base, 'Script Logs', 'DeviceInfo.html')
        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

def sanitize_file_path(filename, replacement_char='_'):
    '''
    Removes illegal characters (for windows) from the string passed. Does not replace \ or /
    '''
    return re.sub(r'[*?:"<>|\'\r\n]', replacement_char, filename)

def sanitize_file_name(filename, replacement_char='_'):
    '''
    Removes illegal characters (for windows) from the string passed.
    '''
    return re.sub(r'[\\/*?:"<>|\'\r\n]', replacement_char, filename)

def get_next_unused_name(path):
    '''Checks if path exists, if it does, finds an unused name by appending -xx
       where xx=00-99. Return value is new path.
       If it is a file like abc.txt, then abc-01.txt will be the next
    '''
    folder, basename = os.path.split(path)
    ext = None
    if basename.find('.') > 0:
        basename, ext = os.path.splitext(basename)
    num = 1
    new_name = basename
    if ext != None:
        new_name += f"{ext}"
    while os.path.exists(os.path.join(folder, new_name)):
        new_name = basename + "-{:02}".format(num)
        if ext != None:
            new_name += f"{ext}"
        num += 1
    return os.path.join(folder, new_name)

def open_sqlite_db_readonly(path):
    '''Opens an sqlite db in read-only mode, so original db (and -wal/journal are intact)'''
    if is_platform_windows():
        if path.startswith('\\\\?\\UNC\\'): # UNC long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\?\\'):    # normal long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\'):       # UNC path
            path = "%5C%5C%3F%5C\\UNC" + path[1:]
        else:                               # normal path
            path = "%5C%5C%3F%5C" + path
    return sqlite3.connect (f"file:{path}?mode=ro", uri=True)

def does_column_exist_in_db(db, table_name, col_name):
    '''Checks if a specific col exists'''
    col_name = col_name.lower()
    try:
        db.row_factory = sqlite3.Row # For fetching columns by name
        query = f"pragma table_info('{table_name}');"
        cursor = db.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        for row in all_rows:
            if row['name'].lower() == col_name:
                return True
    except sqlite3.Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
        pass
    return False

def does_table_exist(db, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        cursor = db.execute(query)
        for row in cursor:
            return True
    except sqlite3.Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
    return False

class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None # static variable 
    progress_bar_total = 0
    progress_bar_handle = None

    @staticmethod
    def SetProgressBar(n):
        if GuiWindow.progress_bar_handle:
            GuiWindow.progress_bar_handle.UpdateBar(n)

def logfunc(message=""):
    with open(OutputParameters.screen_output_file_path, 'a', encoding='utf8') as a:
        print(message)
        a.write(message + '<br>' + OutputParameters.nl)

    if GuiWindow.window_handle:
        GuiWindow.window_handle.refresh()
        
def logdevinfo(message=""):
    with open(OutputParameters.screen_output_file_path_devinfo, 'a', encoding='utf8') as b:
        b.write(message + '<br>' + OutputParameters.nl)
        
""" def deviceinfoin(ordes, kas, vas, sources): # unused function
    sources = str(sources)
    db = sqlite3.connect(reportfolderbase+'Device Info/di.db')
    cursor = db.cursor()
    datainsert = (ordes, kas, vas, sources,)
    cursor.execute('INSERT INTO devinf (ord, ka, va, source)  VALUES(?,?,?,?)', datainsert)
    db.commit() """
    
def html2csv(reportfolderbase):
    #List of items that take too long to convert or that shouldn't be converted
    itemstoignore = ['index.html',
                    'Distribution Keys.html', 
                    'StrucMetadata.html',
                    'StrucMetadataCombined.html']
                    
    if os.path.isdir(os.path.join(reportfolderbase, '_CSV Exports')):
        pass
    else:
        os.makedirs(os.path.join(reportfolderbase, '_CSV Exports'))
    for root, dirs, files in sorted(os.walk(reportfolderbase)):
        for file in files:
            if file.endswith(".html"):
                fullpath = (os.path.join(root, file))
                head, tail = os.path.split(fullpath)
                if file in itemstoignore:
                    pass
                else:
                    data = open(fullpath, 'r', encoding='utf8')
                    soup=BeautifulSoup(data,'html.parser')
                    tables = soup.find_all("table")
                    data.close()
                    output_final_rows=[]

                    for table in tables:
                        output_rows = []
                        for table_row in table.findAll('tr'):

                            columns = table_row.findAll('td')
                            output_row = []
                            for column in columns:
                                    output_row.append(column.text)
                            output_rows.append(output_row)
        
                        file = (os.path.splitext(file)[0])
                        with codecs.open(os.path.join(reportfolderbase, '_CSV Exports',  file +'.csv'), 'a', 'utf-8-sig') as csvfile:
                            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
                            writer.writerows(output_rows)

def tsv(report_folder, data_headers, data_list, tsvname, source_file=None):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tsv_report_folder = os.path.join(report_folder_base, '_TSV Exports')
    
    if os.path.isdir(tsv_report_folder):
        pass
    else:
        os.makedirs(tsv_report_folder)

    if os.path.exists(os.path.join(tsv_report_folder, tsvname +'.tsv')):
        with codecs.open(os.path.join(tsv_report_folder, tsvname +'.tsv'), 'a', 'utf-8') as tsvfile:
            tsv_writer = csv.writer(tsvfile, delimiter='\t')
            for i in data_list:
                if source_file == None:
                    tsv_writer.writerow(i)
                else:
                    row_data = list(i)
                    row_data.append(source_file)
                    tsv_writer.writerow(tuple(row_data))
    else:    
        with codecs.open(os.path.join(tsv_report_folder, tsvname +'.tsv'), 'a', 'utf-8-sig') as tsvfile:
            tsv_writer = csv.writer(tsvfile, delimiter='\t')
            if source_file ==  None:
                tsv_writer.writerow(data_headers)
                for i in data_list:
                    tsv_writer.writerow(i)
            else:
                data_hdr = list(data_headers)
                data_hdr.append("source file")
                tsv_writer.writerow(tuple(data_hdr))
                for i in data_list:
                    row_data = list(i)
                    row_data.append(source_file)
                    tsv_writer.writerow(tuple(row_data))
            

def timeline(report_folder, tlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tl_report_folder = os.path.join(report_folder_base, '_Timeline')

    if os.path.isdir(tl_report_folder):
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
    else:
        os.makedirs(tl_report_folder)
        #create database
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb, isolation_level = 'exclusive')
        cursor = db.cursor()
        cursor.execute(
        """
        CREATE TABLE data(key TEXT, activity TEXT, datalist TEXT)
        """
            )
        db.commit()
    
    a = 0
    length = (len(data_list))
    while a < length: 
        modifiedList = list(map(lambda x, y: x + ': ' +  str(y), data_headers, data_list[a]))
        cursor.executemany("INSERT INTO data VALUES(?,?,?)", [(str(data_list[a][0]), tlactivity, str(modifiedList))])
        a += 1
    db.commit()
    db.close()
    
def kmlgen(report_folder, kmlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    kml_report_folder = os.path.join(report_folder_base, '_KML Exports')
    
    if os.path.isdir(kml_report_folder):
        latlongdb = os.path.join(kml_report_folder, '_latlong.db')
        db = sqlite3.connect(latlongdb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
        db.commit()
    else:
        os.makedirs(kml_report_folder)
        latlongdb = os.path.join(kml_report_folder, '_latlong.db')
        db = sqlite3.connect(latlongdb)
        cursor = db.cursor()
        cursor.execute(
        """
        CREATE TABLE data(key TEXT, latitude TEXT, longitude TEXT, activity TEXT)
        """
            )
        db.commit()
    
    kml = simplekml.Kml(open=1)
    
    a = 0
    length = (len(data_list))
    while a < length:
        modifiedDict = dict(zip(data_headers, data_list[a]))
        times = modifiedDict['Timestamp']
        lon = modifiedDict['Longitude']
        lat = modifiedDict['Latitude']
        if lat:
            pnt = kml.newpoint()
            pnt.name = times
            pnt.description = f"Timestamp: {times} - {kmlactivity}"
            pnt.coords = [(lon, lat)]
            cursor.execute("INSERT INTO data VALUES(?,?,?,?)", (times, lat, lon, kmlactivity))
        a += 1
    db.commit()
    db.close()
    kml.save(os.path.join(kml_report_folder, f'{kmlactivity}.kml'))

def usergen(report_folder, data_list_usernames):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    udb_report_folder = os.path.join(report_folder_base, '_Usernames DB')
    
    if os.path.isdir(udb_report_folder):
        usernames = os.path.join(udb_report_folder, '_usernames.db')
        db = sqlite3.connect(usernames)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
        db.commit()
    else:
        os.makedirs(udb_report_folder)
        usernames = os.path.join(udb_report_folder, '_usernames.db')
        db = sqlite3.connect(usernames)
        cursor = db.cursor()
        cursor.execute(
        """
        CREATE TABLE data(username TEXT, appname TEXT, artifactname text, html_report text, data TEXT)
        """
            )
        db.commit()
    
    a = 0
    length = (len(data_list_usernames))
    while a < length:
        user = data_list_usernames[a][0]
        app = data_list_usernames[a][1]
        artifact = data_list_usernames[a][2]
        html_report = data_list_usernames[a][3]
        data = data_list_usernames[a][4]
        cursor.execute("INSERT INTO data VALUES(?,?,?,?,?)", (user, app, artifact, html_report, data))
        a += 1
    db.commit()
    db.close()
    

def get_browser_name(file_name):
    if 'com.brave.browser' in file_name.lower():
        return 'Brave'
    elif 'com.opera.browser' in file_name.lower():
        return 'Opera'
    elif 'com.duckduckgo.mobile.android' in file_name.lower():
        return 'Duck Duck Go'
    else:
        return 'Chromebook'

def get_ldb_records(ldb_path, prefix=''):
    """Open a LevelDB at given path and return a list of records, optionally
    filtered by a prefix string. Key and value are kept as byte strings.
    This code was taken from the file utils.py from Ryan Benson's Hindsight project"""

    try:
        from scripts.lib.ccl_chrome_indexeddb import ccl_leveldb
    except ImportError as err:
        logfunc (str(err))
        logfunc (str(f' - Failed to import ccl_leveldb; unable to process {ldb_path}'))
        return []

    # The ldb key and value are both bytearrays, so the prefix must be too. We allow
    # passing the prefix into this function as a string for convenience.
    if isinstance(prefix, str):
        prefix = prefix.encode()

    try:
        db = ccl_leveldb.RawLevelDb(ldb_path)
    except Exception as e:
        logfunc (str(f' - Could not open {ldb_path} as LevelDB; {e}'))
        return []

    cleaned_records = []

    try:
        for record in db.iterate_records_raw():
            cleaned_record = record.__dict__

            if record.file_type.name == 'Ldb':
                cleaned_record['key'] = record.key[:-8]

            if cleaned_record['key'].startswith(prefix):
                cleaned_record['key'] = cleaned_record['key'][len(prefix):]
                cleaned_record['state'] = cleaned_record['state'].name
                cleaned_record['file_type'] = cleaned_record['file_type'].name

                cleaned_records.append(cleaned_record)

    except ValueError:
        logfunc (str(f' - Exception reading LevelDB: ValueError'))

    except Exception as e:
        logfunc (str(f' - Exception reading LevelDB: {e}'))

    db.close()
    return cleaned_records

def read_varint(source):
    ''' This code was taken from the file utils.py from Ryan Benson's Hindsight project '''
    result = 0
    bytes_used = 0
    for read in source:
        result |= ((read & 0x7F) << (bytes_used * 7))
        bytes_used += 1
        if (read & 0x80) != 0x80:
            return result, bytes_used

def clean_up_br(data_list):
    item_cleaned = []
    clean_list = []
    for s in data_list:
        for t in s:
            t=str(t)
            t = (t.replace("<br>", ""))
            item_cleaned.append(t) 
        clean_list.append(item_cleaned)
        item_cleaned =[]
    return clean_list    