import json
import mysql.connector

configs = json.load(open('config.json'))

mydb = mysql.connector.connect(
  host=configs['mysql-db']['host'],
  user=configs['mysql-db']['user'],
  password=configs['mysql-db']['password']
)

mycursor = mydb.cursor()

try:
    mycursor.execute("CREATE DATABASE " + configs['mysql-db']['database'])
except mysql.connector.Error as err:
    # if error is "database exists" then good to go
    if err.errno != 1007:
        print("Something went wrong while trying to create database: {}".format(err))

mydb = mysql.connector.connect(
  host=configs['mysql-db']['host'],
  user=configs['mysql-db']['user'],
  password=configs['mysql-db']['password'],
   database = configs['mysql-db']['database']
)

mycursor = mydb.cursor()

# create table with date, day, name, event name, time
try:
    mycursor.execute(f"CREATE TABLE {configs['mysql-db']['table']} (id INT AUTO_INCREMENT PRIMARY KEY, ddate DATE, day VARCHAR(255), name VARCHAR(255), event VARCHAR(255), time VARCHAR(255))")
except mysql.connector.Error as err:
    if err.errno != 1050:
        print("Something went wrong while trying to create table: {}".format(err))
    else:
        if input(f"this action will clear the table {configs['mysql-db']['table']} in your {configs['mysql-db']['database']} database in your mysql server, proceed anyway? [y/n]") == 'y':
            # drop table
            mycursor.execute(f"DROP TABLE {configs['mysql-db']['table']}")
            # recreate table
            mycursor.execute(f"CREATE TABLE {configs['mysql-db']['table']} (id INT AUTO_INCREMENT PRIMARY KEY, ddate DATE, day VARCHAR(255), name VARCHAR(255), event VARCHAR(255), time VARCHAR(255))")

print('database setup complete')
