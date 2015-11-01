#!/usr/bin/env python

from scriptine.shell import sh
import yaml 

config = yaml.safe_load(open("config.yml"))

def clean_log():
    LOGFILE = config['rsync']['log_file']
    sh('/bin/cat /dev/null > %s' %LOGFILE)
    sh('/usr/bin/echo Starting backup at `date` > %s' %LOGFILE) 
if __name__ == '__main__':
    clean_log()

