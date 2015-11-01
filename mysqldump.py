#!/usr/bin/env python

from scriptine import log, path
from scriptine.shell import sh
import yaml 
import datetime
import time
config = yaml.safe_load(open("config.yml"))

def mysqldump():
    for DB in config['databases']:
        # check/fix paths in BACKUP_DIR  - remove trailing slash
        BACKUP_DIR = config['rsync']['backup_dir']
        if not BACKUP_DIR[-1] == '/':
            pass
        else:
            BACKUP_DIR = config['rsync']['backup_dir'][:-1] 

        # check/fix paths in mysql_backup_dir - add leading slash
        MYSQL_DIR = config['mysql']['backup_dir']
	if MYSQL_DIR[0] == '/':
            pass
        else:
            MYSQL_DIR = '/' + MYSQL_DIR
        
        # check/fix paths in mysql_backup_dir - add trailing slash
        if MYSQL_DIR[-1] == '/':
            pass
        else: 
            MYSQL_DIR = MYSQL_DIR + '/'

        # fix paths in DATETIME - add trailing slash
        DATETIME = time.strftime("%d-%m-%Y")
        DATETIME = DATETIME + '/'
        REAL_DIR = BACKUP_DIR + MYSQL_DIR + DATETIME
        
        # ensure that backup_dirs exist
        outdir = path(REAL_DIR)
        if not outdir.exists():
            log.mark('Creating mysql dir %s' % outdir)
            outdir.makedirs()
    
        sh('/usr/bin/echo Dumping %s >> %s' % (DB, config['rsync']['log_file']))
        sh('/usr/bin/mysqldump -h %s -u %s -p%s %s | gzip -9 > %s%s.sql.gz' % (config['mysql']['server'], config['mysql']['user'], config['mysql']['password'], DB, REAL_DIR, DB))
        sh('/usr/bin/echo Done >> %s' %config['rsync']['log_file'])

if __name__ == '__main__':
    mysqldump()

