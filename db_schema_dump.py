#!/usr/bin/env python
import os
import sys
import getopt
import subprocess
import getpass

def usage():
    print "Dump MySQL DB Schema to file(s)"
    print "Usage: db_schema_dump.py [OPTION]..."
    print " -u <db user> required"
    print " -h <db host> optional, default localhost"
    print " -d <db name> optional, default all except mysql meta"
    print " -l lock tables during export, optional, specific user privileges required"

def find_binary(bin_filename):
    """uses which to find env specific binaries
    @return path to binary OR False if not found or error returned"""
    which_proc = subprocess.Popen(["which", bin_filename], stdout=subprocess.PIPE)
    path,err = which_proc.communicate()
    if path == '' or err:
        return False
    else:
        return path.strip()
    
def write_mysql_schema_to_file(parameters):
    """uses mysqldump binary to pipe a supplied db name to a schema.ddl file out""" 
    try:
        db_schema_ret_code = subprocess.call(["%s --no-data %s -u '%s' %s -h '%s' %s > %s.%s.ddl" % parameters], shell=True)
        if db_schema_ret_code < 0:
            print >>sys.stderr, "Child was terminated by signal", db_schema_ret_code
        else:
            print "Wrote %s.%s.ddl" % (server, db_name)
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e
        

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:ph:d:", ["user", "pass", "host", "database", "help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    if len(opts) == 0:
        usage()
        sys.exit()

    user = ''
    passwd = ''
    server = 'localhost'
    db_name = ''
    lock_tables = False

    for o,val in opts:
        #print "o=%s, a=%s" % (o,a)
        if o == "-d":
            db_name = val
        elif o == "-u":
            user = val
        elif o == "-h":
            server = val
        elif o == "-l":
            lock_tables = True
        elif o == "--help":
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()
    
    if user == '':
        usage()
        sys.exit()
        
    # do it, do it
    passwd = getpass.getpass("Enter password: ")
    if passwd == '': 
        passwd_str = ''
    else:
        passwd_str = "--password='%s'" % passwd
        
    if lock_tables == True:
        lock_tables_str = ''
    else:
        lock_tables_str = '--lock-tables=false'
        
    mysql_bin_path = find_binary('mysql')
    if mysql_bin_path is False:
        mysql_bin_path = '/usr/bin/mysql'
    mysqldump_bin_path = find_binary('mysqldump')
    if mysqldump_bin_path is False:
        mysqldump_bin_path = '/usr/bin/mysqldump'    
        
    if db_name == '':
        # export all dem schemas
        dbs_list_proc = subprocess.Popen(["%s -u '%s' %s -e 'show databases' -h %s | awk -F' ' '{print $1}'" %
                                          (mysql_bin_path, user, passwd_str, server)], stdout=subprocess.PIPE, shell=True)
        dbs_list,err = dbs_list_proc.communicate()
        for db_name in dbs_list.splitlines():
            if db_name == 'Database' or db_name == 'mysql' or db_name == 'information_schema':
                continue
            else:
                write_mysql_schema_to_file((mysqldump_bin_path, lock_tables_str, user, passwd_str, server, db_name, server, db_name))

    else:
        write_mysql_schema_to_file((mysqldump_bin_path, lock_tables_str, user, passwd_str, server, db_name, server, db_name))
            