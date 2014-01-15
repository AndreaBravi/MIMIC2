# -*- coding: utf-8 -*-
"""
Setup.sh and import.sh for MIMIC2 rewritten in Python (for windows usage)
"""

import tarfile as tar
from getpass import getpass
import os


# Check if PostgreSQL is installed 
print '\n---Script started!\n'
if os.environ['PATH'].find("PostgreSQL") == -1:
    postgresql_dir = raw_input("Provide path to pg_env.bat: ") 
    if os.path.exists(postgresql_dir):
        os.environ["PATH"] += os.pathsep + postgresql_dir + os.sep + "bin"
    else:
        raise Exception("PostreSQL database not installed, or not in the specified path")    
        exit()
        

# Make a directory for storage of MIMIC2
database_dir = postgresql_dir + os.sep + "data" + os.sep + "mimic2v26_dat"
if not os.path.exists(database_dir):
    os.makedirs(database_dir)
    

# Create a directory for saving the tarballs after processing (for reuse)
importer_dir = raw_input("\nProvide path to MIMIC Importer: ")
tarballs_dir = importer_dir + os.sep + 'tarballs'
flatfiles_dir = importer_dir + os.sep + 'raw_tarballs'
if not os.path.exists(flatfiles_dir):
    os.makedirs(flatfiles_dir)


# Extract data from tarballs
print '\n---Extracting tarballs'
os.chdir(tarballs_dir)
tarball_list = os.listdir(tarballs_dir)
n_tarball = len(tarball_list)
for num, filename in enumerate(tarball_list):
    name = filename.split('-')[2].split('.')[0]    
    if not os.path.exists(flatfiles_dir + os.sep + name):
        print 'Processing file', filename, '(%d/%d)' % (num + 1, n_tarball)
        with tar.open(filename) as f:
            f.extractall(flatfiles_dir)


# Create user
username = os.environ['USERNAME']
print '\n---Creating user', username
os.system('createuser.exe --superuser --createdb --username postgres' \
          ' --no-createrole --pwprompt "%s"' % (username))
password = getpass('Repeat password for ' + username + ': ')
os.environ["PGPASSWORD"] = password
             
             
# Create database             
print '\n---Creating database MIMIC2'
os.system('createdb.exe MIMIC2 "%s"' % (username))


# Assign database_dir to the tablespace
print '\n---Assigning tablespace'
os.system('psql -q -c "CREATE TABLESPACE MIMIC2V26_DAT ' \
          'LOCATION \'%s\';" MIMIC2 "%s"' % (database_dir.replace("\\","/"), username))


# Load table schema
print '\nLoading table schema'
os.system('psql -q -f "%s\\Definitions\\POSTGRES\\' \
          'schema_mimic2v26.sql" MIMIC2 "%s"' % (flatfiles_dir.replace("\\","/"), username))


# Load table definitions
print '\nLoading table definitions'
tab_def_dir = flatfiles_dir + os.sep + 'Definitions'
for filename in os.listdir(tab_def_dir):
    if filename.endswith(".txt"):
        file_path = (tab_def_dir + os.sep + filename).replace("\\","/")
        table_name = filename.split('.')[0]
        os.system('psql -q -c "\\COPY MIMIC2V26.%s FROM \'%s\''\
                  'WITH DELIMITER \',\' CSV HEADER;" MIMIC2 "%s"' \
                  % (table_name, file_path, username))


# Load the subject-specific data
print '\nLoading subject-specific data'
n_folder = len(os.listdir(flatfiles_dir))
for num, folder in enumerate(os.listdir(flatfiles_dir)):
    print 'Processing folder %s (%d/%d)' % (folder, num + 1, n_folder)
    if folder != 'Definitions':
        folder_path = flatfiles_dir + os.sep + folder
        for subfolder in os.listdir(folder_path):
            print '- Subject', subfolder
            subfolder_path = folder_path + os.sep + subfolder
            for filename in os.listdir(subfolder_path):
                file_path = (subfolder_path + os.sep + filename).replace("\\","/")
                table_name = filename.split('.')[0].split('-')[0]
                os.system('psql -q -c "\\COPY MIMIC2V26.%s FROM \'%s\''\
                          'WITH DELIMITER \',\' CSV HEADER;" MIMIC2 "%s"' \
                          % (table_name, file_path, username))


print 'Done creating the MIMIC II Database!'
    
    
"""After running the MIMIC Importer successfully, you can safely remove the
MIMIC-Importer directory, and all its contents, if you wish to reclaim the
storage space it used.  It is also advisable to drop the PostgreSQL superuser
privileges assigned to your role (since it is easy to damage your database if
you work with superuser privileges).  To do this, acquire root and then
postgres privileges (as in step 4 in Appendix B), then run the command:
    psql -c "ALTER ROLE username WITH NOSUPERUSER;"
substituting your login name for "username".  If you wish to use the MIMIC
Importer to load more data later, restore the PostgreSQL superuser privileges
by acquiring root and postgres privileges again, and run:
    psql -c "ALTER ROLE username WITH SUPERUSER;"
"""
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   