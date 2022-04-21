#!/usr/bin/python
import os, sys, datetime, tarfile, os.path
from pymongo import MongoClient
from utils import get_meta
from bson.json_util import dumps


def create_folder_backup(dbname):
    dt = datetime.datetime.now()
    directory = ('backups/bk_%s_%s-%s-%s__%s_%s' % (dbname,dt.month,dt.day,dt.year, dt.hour, dt.minute))
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def run_backup(mongoUri, dbname):
    try:
        client = MongoClient(mongoUri)
        client.server_info() # will throw an exception
    except:
        print(f'Cannot connect with {mongoUri}')
        exit()
    db = client[dbname]
    collections = db.list_collection_names()
    files_to_compress = []
    directory = create_folder_backup(dbname)
    for collection in collections:
        db_collection = db[collection]
        cursor = db_collection.find({})
        filename = ('%s/%s.json' %(directory,collection))
        files_to_compress.append(filename)
        with open(filename, 'w') as file:
            file.write('[')
            for document in cursor:
                file.write(dumps(document))
                file.write(',')
            file.write(']')
    tar_file = ('%s.tar.gz' % (directory)) 
    make_tarfile(tar_file,files_to_compress)

def make_tarfile(output_filename, source_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for filename in source_dir:
        tar.add(filename)
    tar.close()

if __name__ == '__main__':
    meta = get_meta()
    if( len(meta) == 0 ):
        print('Cannot read META data')
        exit() 
    env_vars = meta['env'][0]
    DB_CONNECT_URL = env_vars['database_url']
    DB_NAME        = env_vars['database_name'] 
    try:
        run_backup(DB_CONNECT_URL, DB_NAME)
        print('[*] Successfully performed backup')
    except Exception as e:
        print('[-] An unexpected error has occurred')
        print('[-] '+ str(e) )
        print('[-] EXIT')
