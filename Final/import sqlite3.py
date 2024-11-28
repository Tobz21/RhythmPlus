import sqlite3

player,chart,score,grade,accuracy,combo,rank='James1',0,1200,3,88.88,1200,5
conn = sqlite3.connect('players.db')
cursor=conn.cursor()
cursor.execute("INSERT INTO Scores(player,chart,score,grade,accuracy,combo,rank) VALUES(?,?,?,?,?,?,?)",[player,chart,score,grade,accuracy,combo,rank])
player,chart,score,grade,accuracy,combo,rank='James1',0,900,2,83.88,1100,4
cursor.execute("INSERT INTO Scores(player,chart,score,grade,accuracy,combo,rank) VALUES(?,?,?,?,?,?,?)",[player,chart,score,grade,accuracy,combo,rank])
player,chart,score,grade,accuracy,combo,rank='James1',2,130,2,89.8,300,2
cursor.execute("INSERT INTO Scores(player,chart,score,grade,accuracy,combo,rank) VALUES(?,?,?,?,?,?,?)",[player,chart,score,grade,accuracy,combo,rank])
conn.commit()
conn.close()