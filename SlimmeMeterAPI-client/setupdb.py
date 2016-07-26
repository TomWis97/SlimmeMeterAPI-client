from mysql.connector import connection
import getpass
import random
import sys
print("--------- Database setup script for SlimmeMeterAPI-client ---------")
print("""This script will ask the following things:
    - Database host.
    - Administrative username.
    - Administrative user's password.
    - Database to create and use.
    - Database user to create and use.
    - Password for database user.

This script will create a new database and user with the same name.
After succes, the configuration file will be changed automatically.

Options:
    - overwrite: Overwrite current database. THIS WILL DELETE ALL CURRENT
                 DATA!
    - defaults:  Automatically accept default values.

    Usage:       $ python3 setupdb.py defaults overwrite 
""")

# Creating variables.
dbHost = ''
dbAdminUser = ''
dbAdminPassword = ''
dbName = ''
dbUsername = ''
dbPassword = ''

if not 'defaults' in sys.argv:
    dbHost = input("Database host [127.0.0.1]: ")
    dbAdminUser = input("Database administrative username: [root]")
    dbName = input("Database name [slimmemeter]: ")
    dbUsername = input("Database username [slimmemeter]: ")
    dbPassword = getpass.getpass(prompt='Database user password [automatically generated]: ')
else:
    print("\n'defaults' option detected. Using defaults.")

# Setting defaults.
if len(dbHost) == 0:
    dbHost = '127.0.0.1'

if len(dbAdminUser) == 0:
    dbAdminUser = 'root'

if len(dbName) == 0:
    dbName = 'slimmemeter'

if len(dbUsername) == 0:
    dbUsername = 'slimmemeter'

if len(dbPassword) == 0:
    allowedchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    passlen = 25
    for char in random.sample(allowedchars, passlen):
        dbPassword = dbPassword + char

if 'overwrite' in sys.argv:
    print("'overwrite' detected. The script will delete the current database!")

dbAdminPassword = getpass.getpass(prompt='Database administrative user password: ')

print("\n---------- DATA ----------",
"Database host:          %s" % dbHost,
"Administrator username: %s" % dbAdminUser,
"Administrator password: %s" % ('*' * len(dbAdminPassword) + " (" + str(len(dbAdminPassword)) + ")"),
"Database name:          %s" % dbName,
"Database username:      %s" % dbUsername,
"Database user password: %s" % dbPassword,
sep='\n')
print("--------------------------")

# Connecting to database.
# Yes this, doesn't do fancy error handling.
cnx = connection.MySQLConnection(user=dbAdminUser, password=dbAdminPassword, host=dbHost)
cursor = cnx.cursor()
# Checking if database exists.

query = ('SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA '
         'WHERE SCHEMA_NAME = %s')
cursor.execute(query, (dbName,))
result = cursor.fetchall()
if len(result) == 0:
    print("Database doesn't exist. Continuing.")
else:
    print("Database exists!")
    if 'overwrite' in sys.argv:
        print("Overwrite option detected. DELETING CURRENT DATABASE %s" % dbName)
        cursor.execute('DROP DATABASE {}'.format(dbName))
    else:
        raise ValueError("Database already exists! This script should only run on a new install.")

# Check if user already exists.
query = ('SELECT * FROM mysql.user WHERE user = %s')
cursor.execute(query, (dbUsername,))
result = cursor.fetchall()
if result:
    # User exists. Checking if password is correct.
    print("User already exists. Checking if password is correct.")
    currentPasswordHash = result[0][2].decode('UTF-8')
    # Generating password hash for entered password.
    query = ('SELECT PASSWORD(%s)')
    cursor.execute(query, (dbPassword,))
    passwordHash = cursor.fetchone()[0]
    if passwordHash == currentPasswordHash:
        print("Already entered password for database user is correct.")
    else:
        if 'overwrite' in sys.argv:
            print("Overwrite option detected. DELETING USER %s@%s" % (dbUsername, dbHost))
            cursor.execute('DROP USER %s@%s', (dbUsername, dbHost))
        else:
            raise ValueError("Password for database user is not correct.")
else:
    print("Database user doesn't exist already.")

# Creating database and user.
print("Creating database.")
cursor.execute('CREATE DATABASE {} DEFAULT CHARACTER SET \'utf8\''.format(dbName))
print("Creating user.")
cursor.execute('CREATE USER %s@%s IDENTIFIED BY %s', (dbUsername, dbHost, dbPassword))
print("Granting access to new database.")
cursor.execute('GRANT ALL ON {}.* TO %s@%s'.format(dbName), (dbUsername, dbHost))
print("Switching to database.")
cursor.execute('USE {}'.format(dbName))
print("Creating tables.")
cursor.execute('CREATE TABLE history (timestamp DATETIME NOT NULL, name VARCHAR(30) NOT NULL, value VARCHAR(1024) NOT NULL, PRIMARY KEY (timestamp, name))')
print("Done!")

