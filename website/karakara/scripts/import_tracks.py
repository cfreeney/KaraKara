import os
import json
import urllib
import re
#import io
from bs4 import BeautifulSoup
import traceback

from ..lib.misc import get_fileext, random_string

from ..model.model_tracks import Track, Tag, Attachment, Lyrics, _attachment_types

from ..model         import init_DBSession, DBSession
from ..model.actions import get_tag
import transaction

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

version = "0.0"

file_component_separator = r'[ .\\/\[\]]'

def sep(text):
    return r'%s%s\d?%s' % (file_component_separator, text, file_component_separator)
def or_sep(*args):
    return r'|'.join(args)

tag_extractors = {
    'opening' : re.compile(or_sep('open','intro','opening','op'), re.IGNORECASE),
    'ending'  : re.compile(or_sep('end' ,'outro','ending' ,'ed'), re.IGNORECASE),
    'anime'   : re.compile(r'anime', re.IGNORECASE),
}


#-------------------------------------------------------------------------------
# Import from URL
#-------------------------------------------------------------------------------
def walk_url(uri):
    webpage = urllib.request.urlopen(uri)
    soup = BeautifulSoup(webpage.read())
    webpage.close()
    for href in [link.get('href') for link in soup.find_all('a')]:
        if href.endswith('/'):
            log.warn("directory crawling from urls is not implmented yet: %s" % href)
        elif href.endswith('.json'):
            absolute_filename = uri + href #AllanC - todo - this is not absolute if dir's are crawled!
            with urllib.request.urlopen(absolute_filename) as file:
                import_json_data(file, absolute_filename)


#-------------------------------------------------------------------------------
# Import from local filesystem
#-------------------------------------------------------------------------------
def walk_local(uri):
    for root, dirs, files in os.walk(uri):
        for json_filename in [f for f in files if get_fileext(f)=='json']:
            absolute_filename = os.path.join(root         , json_filename)
            #relative_path = root.replace(uri,'')
            #relative_filename = os.path.join(relative_path, json_filename)
            with open(absolute_filename, 'r') as file:
                import_json_data(file, absolute_filename)


#-------------------------------------------------------------------------------
# Process JSON leaf
#-------------------------------------------------------------------------------
def import_json_data(source, location=''):
    """
    source should be a filetype object for a json file to import
    it shouldnt be relevent that it is local or remote
    """
    
    def get_data():
        try:
            if hasattr(source,'read'):
                data = source.read()
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            return json.loads(data)
        except Exception as e:
            log.warn('Failed to process %s' % location)
            traceback.print_exc()
    
    data = get_data()
    if not data:
        return
    
    if 'description.json' in location:
        try:
            folder = data['name']
            log.info('Importing %s' % folder)
            
            track = Track()
            track.id       = data['videos'][0]['encode-hash']
            track.source   = ''
            track.duration = data['videos'][0]['length']
            track.title    = data['name']
            
            # Add Attachments
            for attachment_type in _attachment_types.enums:
                for attachment_data in data.get("%ss"%attachment_type,[]):
                    attachment = Attachment()
                    attachment.type     = attachment_type
                    attachment.location = os.path.join(folder,  attachment_data.get('url'))
                    track.attachments.append(attachment)
            
            # Add Lyrics
            for subtitle in data.get('subtitles',[]):
                lyrics = Lyrics()
                lyrics.language = subtitle.get('language','eng')
                lyrics.content  = "\n".join(subtitle.get('lines',[]))
                track.lyrics.append(lyrics)
            
            # Attempt to get Tags from source filename
            # Add known tags (by regexing source filename/path)
            #for tag, regex in tag_extractors.items():
            #    if regex.search(track.source):
            #        track.tags.append(get_tag(tag))
            
            # Import Media Processed Tags
            try:
                with open(os.path.join(os.path.dirname(location),'tags.txt'), 'r') as tag_file:
                    for tag in tag_file:
                        track.tags.append(get_tag(tag))
            except Exception as e:
                log.warn('Unable to imports tags')
            
            # AllanC TODO: if there is a duplicate track.id we may still want to re-add the attachments rather than fail the track entirely
            
            DBSession.add(track)
            transaction.commit()
        except Exception as e:
            log.warn('Unable to process %s because %s' % (location, ''))


#-------------------------------------------------------------------------------
# Import - URI crawl method selector
#-------------------------------------------------------------------------------

def import_media(uri):
    """
    Recursivly traverse uri location searching for .json files to import
    should be able to traverse local file system and urls
    """
    if (uri.startswith('http')):
        walk_url(uri)
    else:
        walk_local(uri)


#-------------------------------------------------------------------------------
# Command Line
#-------------------------------------------------------------------------------

def get_args():
    import argparse
    # Command line argument handling
    parser = argparse.ArgumentParser(
        description="""Import media to local Db""",
        epilog=""""""
    )
    parser.add_argument('source_uri'  , help='uri of track media data')
    parser.add_argument('--config_uri', help='config .ini file for logging configuration', default='development.ini')
    parser.add_argument('--version', action='version', version=version)

    return parser.parse_args()

def main():
    args = get_args()
    
    # Setup Logging and Db from .ini
    from pyramid.paster import get_appsettings, setup_logging
    #setup_logging(args.config_uri)
    logging.basicConfig(level=logging.INFO)
    settings = get_appsettings(args.config_uri)
    init_DBSession(settings)
    
    import_media(args.source_uri)
    
    
if __name__ == "__main__":
    main()