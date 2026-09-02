import sqlite3

## connect to sqlite database
connection = sqlite3.connect('students.db')


##create a cursor object to insert records, create tables
cursor=connection.cursor()

## create the table
table_info="""
CREATE table STUDENTS(
NAME VARCHAR(20),
CLASS VARCHAR(2),
SECTION CHAR(1),
MARKS INT)
"""

cursor.execute(table_info)


## Insert data into table students

cursor.execute("""INSERT INTO students VALUES("Lisa","10","C",86)""") 
cursor.execute("""INSERT INTO students VALUES("Ayush","11","B",80)""") 
cursor.execute("""INSERT INTO students VALUES("Mayank","9","B",75)""") 
cursor.execute("""INSERT INTO students VALUES("kavya","12","D",88)""") 
cursor.execute("""INSERT INTO students VALUES("Khushi","10","C",90)""") 

## Display the data from the table students

print("The inserted records are : ")
data=cursor.execute("""SELECT * FROM students""")

for row in data:
    print(row)

## Commit your changes in the database
connection.commit()
connection.close()