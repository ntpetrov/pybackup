#!/usr/bin/env python

"""
Name: mYbackup version 0.8
Author: Nikolay Petrov ntpetrov@gmail.com
Date: 30.09.2015
---------------------
Future improvements:
Clean code
Better variable handling
Better logging capabilities
"""
import MySQLdb
import subprocess
import time
import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Variables
DB_HOST = "MYSQL_HOST"
DB_USER = "MYSQL_USER"
DB_PASS = "MYSQL_PASS"
DATETIME = time.strftime("%m%d%Y")
ROOT_BACKUP_PATH = "/backup"
MYS_BACKUP_PATH = "/mysql/"
DB_BACKUP_PATH = ROOT_BACKUP_PATH + MYS_BACKUP_PATH
DB_BACKUP_DIR = DB_BACKUP_PATH + DATETIME
FILEPATH = ['/var/www/', '/var/vmail/','/root/']
BSERVER = "IP_ADDRESS_OF_SERVER"
LOGFILE = "/var/log/mYbackup.log"

def main ():

	# Prepare for logging
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	handler = logging.FileHandler(LOGFILE)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\n\r')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	# Clean the logfile
	def cleanlog():
		args = "cat /dev/null" " > " + LOGFILE + ""
		command_process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		command_output = command_process.communicate()
	        logger.info(command_output)
	cleanlog()

	# Creating DB_BACKUP_DIR
	def create_mys_dir():
		logger.info('# Creating backup dir %s #' % DB_BACKUP_DIR)
	        args = "mkdir -p " + DB_BACKUP_DIR + ""
        	command_process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	        command_output = command_process.communicate()
	        logger.info(command_output)
	create_mys_dir()

	# Clean old databases
	def clean_old_db():
		args = "find " + DB_BACKUP_PATH + " -type d -mtime +2 -exec /bin/rm -rf {} \; &>/dev/null"
		command_process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		command_output = command_process.communicate()
	        logger.info(command_output)
	clean_old_db()
	
	# Mail notfication
	def send_message():
		msg = MIMEMultipart('alternative')
		s = smtplib.SMTP('MAIL_SERVER', 25)
		s.login('EMAIL_ADDRESS','EMAIL_PASS')

		toEmail, fromEmail = 'EMAIL@DOMAIN.COM', 'EMAIL@DOMAIN.COM'
		msg['Subject'] = 'New backup was generated'
		msg['From'] = fromEmail
		body = 'To see the output check the attached file'

		filename = "/var/log/mYbackup.log"
		f = file(filename)
		attachment = MIMEText(f.read())
		attachment.add_header('Content-Disposition', 'attachment', filename=filename)
		msg.attach(attachment)

		content = MIMEText(body, 'plain')
		msg.attach(content)
		s.sendmail(fromEmail, toEmail, msg.as_string())
	
	# Function rsync files
	def rsync(files):
	        for folder in FILEPATH:
	                args = "rsync -avze ssh --exclude tmp/ --exclude temp/ --exclude cache/ root@" + BSERVER + ":" + folder + " " + ROOT_BACKUP_PATH + folder + ""
			command_process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			command_output = command_process.communicate()
			logger.info(command_output)
	rsync(FILEPATH)
	
	# Show files
	def new_files():
	       	args = "find " + ROOT_BACKUP_PATH + " -type f -mmin -20 "
	        command_process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	        command_output = command_process.communicate()
	       	logger.info('# Synced files #')
	        logger.info(command_output)
	new_files()
	
	def mysql_conn():
		# MySQL Connection
		connection = MySQLdb.connect(
		                host = DB_HOST,
	        	        user = DB_USER,
	                	passwd = DB_PASS)
		cursor = connection.cursor()
		cursor.execute("SHOW databases ")

		# Populating my_db_list with databases
		my_db_list = []
		for (database,) in cursor:
			if database not in ["innodb", "information_schema", "mysql", "performance_schema", "tmp"]:
				my_db_list.append(database)

		# Function for dumping databases into DB_BACKUP_DIR
		def mysqldump(dblist):
			for database in dblist:
                		args = "mysqldump -h" + DB_HOST + " -u" + DB_USER + " -p" + DB_PASS + " " + database + " | " "gzip -9 " " > " + DB_BACKUP_DIR + "/" + database + ".sql.gz"
				command_process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				command_output = command_process.communicate()
				logger.info('# Dumping database %s #' % database)
				logger.info(command_output)
		mysqldump(my_db_list)
		
	mysql_conn()
	def fix_new_lines():
		subprocess.call(r"sed -i 's/\\n/\n/g' " + LOGFILE, shell=True)
	fix_new_lines()
	send_message()
	

if __name__ == "__main__":
	main()
