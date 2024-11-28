import pygame,sys,time, os, csv,pygame_menu,sqlite3; #imports modules listed

conn = sqlite3.connect('test.db')

conn.execute('''CREATE TABLE COMPANY
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         AGE            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SALARY         REAL);''')

conn.execute('''CREATE TABLE COMPANY2
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         AGE            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SALARY         REAL);''')
conn.commit()
conn.close()