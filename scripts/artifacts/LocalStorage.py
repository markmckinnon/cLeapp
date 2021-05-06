import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.cleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, \
     open_sqlite_db_readonly, get_browser_name, get_ldb_records, read_varint


def parse_ls_ldb_record(record):
    """ This code was taken from the file chrome.py from Ryan Benson's Hindsight project
    From https://cs.chromium.org/chromium/src/components/services/storage/dom_storage/local_storage_impl.cc:
    // LevelDB database schema
    // =======================
    //
    // Version 1 (in sorted order):
    //   key: "VERSION"
    //   value: "1"
    //
    //   key: "META:" + <url::Origin 'origin'>
    //   value: <LocalStorageOriginMetaData serialized as a string>
    //
    //   key: "_" + <url::Origin> 'origin'> + '\x00' + <script controlled key>
    //   value: <script controlled value>
    """
    parsed = {
        'seq': record['seq'],
        'state': record['state'],
        'origin_file': record['origin_file']
    }

    if record['key'].startswith('META:'.encode('utf-8')):
        parsed['record_type'] = 'META'
        parsed['origin'] = record['key'][5:].decode()
        parsed['key'] = record['key'][5:].decode()

        # From https://cs.chromium.org/chromium/src/components/services/storage/dom_storage/
        #   local_storage_database.proto:
        # message LocalStorageOriginMetaData
        #   required int64 last_modified = 1;
        #   required uint64 size_bytes = 2;
        # TODO: consider redoing this using protobufs
        if record['value'].startswith(b'\x08'):
            ptr = 1
            last_modified, bytes_read = read_varint(record['value'][ptr:])
            size_bytes, _ = read_varint(record['value'][ptr + bytes_read:])
            parsed['value'] = f'Last modified: {last_modified}; size: {size_bytes}'
        return parsed

    elif record['key'] == b'VERSION':
        return

    elif record['key'].startswith(b'_'):
        parsed['record_type'] = 'entry'
        try:
            parsed['origin'], parsed['key'] = record['key'][1:].split(b'\x00', 1)
            parsed['origin'] = parsed['origin'].decode()

            if parsed['key'].startswith(b'\x01'):
                parsed['key'] = parsed['key'].lstrip(b'\x01').decode()

            elif parsed['key'].startswith(b'\x00'):
                parsed['key'] = parsed['key'].lstrip(b'\x00').decode('utf-16')

        except Exception as e:
            logfunc(str("Origin/key parsing error: {}".format(e)))
            return

        try:
            if record['value'].startswith(b'\x01'):
                parsed['value'] = record['value'].lstrip(b'\x01').decode('utf-8', errors='replace')

            elif record['value'].startswith(b'\x00'):
                parsed['value'] = record['value'].lstrip(b'\x00').decode('utf-16', errors='replace')

            elif record['value'].startswith(b'\x08'):
                parsed['value'] = record['value'].lstrip(b'\x08').decode()

            elif record['value'] == b'':
                parsed['value'] = ''

        except Exception as e:
            logfunc(str(f'Value parsing error: {e}'))
            return

    for item in parsed.values():
        assert not isinstance(item, bytes)

    return parsed


def get_local_storage(ls_path, wrap_text):
    ''' This code was taken from the file utils.py from Ryan Benson's Hindsight project '''
    results = []

#    logfunc ('Local Storage:')
#    logfunc (f' - Reading from {ls_path}')

    local_storage_listing = os.listdir(ls_path)
#    logfunc (f' - {len(local_storage_listing)} files in Local Storage directory')
    filtered_listing = []

    # Chrome v61+ used leveldb for LocalStorage, but kept old SQLite .localstorage files if upgraded.
    ls_ldb_path = ls_path
    ls_ldb_records = get_ldb_records(ls_ldb_path)
#    logfunc (f' - Reading {len(ls_ldb_records)} Local Storage raw LevelDB records; beginning parsing')
    for record in ls_ldb_records:
        ls_item = parse_ls_ldb_record(record)
        if ls_item and ls_item.get('record_type') == 'entry':
#                results.append(Chrome.LocalStorageItem(
            if wrap_text:
                results.append((ls_item['origin'], ls_item['key'], textwrap.fill(ls_item['value'], width=50),
                            ls_item['seq'], ls_item['state'], str(ls_item['origin_file'])))
            else:
                results.append((ls_item['origin'], ls_item['key'], ls_item['value'],
                            ls_item['seq'], ls_item['state'], str(ls_item['origin_file'])))

#    self.artifacts_counts['Local Storage'] = len(results)
#    logfunc (f' - Parsed {len(results)} items from {len(filtered_listing)} files')
#    self.parsed_storage.extend(results)
    return results

def get_LocalStorage(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'CURRENT': # skip -journal and other files
            continue
        path_name = os.path.dirname(file_found)
        browser_name = get_browser_name(file_found)

        data_list = get_local_storage(path_name, wrap_text)

        usageentries = len(data_list)
        if usageentries > 0:
            description = 'Local Storage key:value pairs report. See path for data provenance.'
            report = ArtifactHtmlReport(f'{browser_name} Local Storage')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Local Storage.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path), description)
            report.add_script()
            data_headers = ('Origin','Key','Value','seq','state', 'origin_file')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Local Storage'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Local Storage'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            logfunc(f'{browser_name} Local Storage parsed')
        else:
            pass
    
        
            