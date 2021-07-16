import sqlite3


def connect():
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS patdb(id INTEGER PRIMARY KEY, title TEXT, amount TEXT, status TEXT)")
    conn.commit()
    conn.close()
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS patdone(id INTEGER PRIMARY KEY, patdbID INTEGER, name TEXT, time TEXT)")
    conn.commit()
    conn.close()
   
def insert(title,amount,status="awaiting start"):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("INSERT INTO patdb VALUES (NULL,?,?,?)",(title,amount,status))
    conn.commit()
    conn.close()

def view():
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM patdb")
    rows=cur.fetchall()
    conn.close()
    return rows

def search(title="",amount=""):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM patdb WHERE title=? OR amount=?",(title,amount))
    rows=cur.fetchall()
    conn.close()
    return rows
     
def getCurrentPatID(title,amt,status):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("SELECT rowid FROM patdb WHERE title=? AND amount=? AND status=? LIMIT 1 ",(title,amt,status))
    temp = cur.fetchone()
    #print("ROWID " ,temp)
    conn.commit()
    conn.close()
    return temp[0]


def addPatDone(currentPatdbId,name,time):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("INSERT INTO patdone VALUES (NULL,?,?,?)",(currentPatdbId,name,time))
    print("Added to patdone database")
    conn.commit()
    conn.close()

def getPatDoneList(temp):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("SELECT name, time FROM patdone WHERE patdbID=?",(temp,))
    rows=cur.fetchall()
    conn.close()
    #print("ROWS GETPATDONELIST: ", rows)
    return rows

    
def deleteSelected(title,amt,status):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("DELETE FROM patdb WHERE rowid = (SELECT rowid FROM patdb WHERE title=? AND amount=? AND status=? LIMIT 1 )",(title,amt,status))
    conn.commit()
    conn.close() 

def delete(id):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("DELETE FROM patdb WHERE id=?",(id,))
    conn.commit()
    conn.close() 
    
def update(status, id):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("UPDATE patdb SET status=? WHERE id=?",(status,id))
    conn.commit()
    conn.close()
        
def getAllRowIDFromPatdb():
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("SELECT rowid FROM patdb")
    temp = cur.fetchall()
    conn.commit()
    conn.close()
    return temp

def getAllpatdbIDFromPatdone():
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("SELECT patdbID FROM patdone")
    temp = cur.fetchall()
    conn.commit()
    conn.close()
    return temp

def deleteFromPatdone(patdbID):
    conn=sqlite3.connect("patdb.db")
    cur=conn.cursor()
    cur.execute("DELETE FROM patdone WHERE patdbID=?",(patdbID,))
    conn.commit()
    conn.close()
    
connect()    
