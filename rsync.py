#!/usr/bin/env python

from scriptine import log, path
from scriptine.shell import sh
import yaml 

config = yaml.safe_load(open("config.yml"))

def rsync():
    """
    Sync everything from config['dirs'] to config['backup_dir']
    
    """
    for DIRS in config['dirs']:
        
        # check/fix paths in BACKUP_DIR - remove trailing slash
        BACKUP_DIR = config['rsync']['backup_dir']
        if not config['rsync']['backup_dir'][-1] == '/':
            pass
        else:
            BACKUP_DIR = config['rsync']['backup_dir'][:-1] 
        
        # check/fix paths in DIRS - add colon before dir and trailing slash in the end
	if DIRS[-1] == '/':
            REAL_DIR = DIRS
            pass
        else:
            REAL_DIR = DIRS + '/'
        if REAL_DIR[0] == ':': 
            pass 
        else:
            REAL_DIR = ':' + REAL_DIR
        # ensure that backup_dirs exist
        for dirname in config['dirs']:
            outdir = path( BACKUP_DIR + dirname)
            if not outdir.exists():
                log.mark('Creating backup_dirs %s' % outdir)
                outdir.makedirs()

        # check/fix USER - add trailing @ to the username
        USER = config['rsync']['user']
        if config['rsync']['user'][-1] == '@':
            pass
        else: 
            USER = USER + '@'
	
        log.mark('Starting rsync.....')
        sh('/usr/bin/rsync %s %s%s%s %s%s &>>%s' % (config['rsync']['args'], USER, config['rsync']['server'], REAL_DIR, config['rsync']['backup_dir'][:-1], REAL_DIR[1:], config['rsync']['log_file']))
if __name__ == '__main__':
    rsync()

