import sqlite3
import bcrypt


def connectDB(name="app.db"):
    return sqlite3.connect(name, check_same_thread=False)


def DbInit(conn):
    cursor = conn.cursor()

    cursor.execute('''  CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,    
            Email TEXT NOT NULL UNIQUE ,
            password TEXT NOT NULL,
            imageurl TEXT NOT NULL           
            )
        '''
    )
    conn.commit()



def AddUser(conn , email , username , password , imageurl):
    cursor = conn.cursor()
    hashedPassword = bcrypt.hashpw(password.encode() , bcrypt.gensalt())
    hashedPassword=hashedPassword.decode()
    query = f''' INSERT INTO users (username , Email , password , imageurl)  VALUES (?,?,?,? ) '''
    cursor.execute(query,(username,email,hashedPassword,imageurl))
    conn.commit()


def getUser_username(conn, username):
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = ? "
    cursor.execute(query,(username,))
    return cursor.fetchone()

def getUser(conn , username):
    cursor= conn.cursor()
    query=f''' SELECT * FROM users WHERE username=?'''
    cursor.execute(query,(username,))
    return cursor.fetchone()

# -------------------------------------------------------------------------------
# Admin

def Admin_getAllUsers(conn):
    cursor = conn.cursor()
    query = ''' SELECT * FROM users '''
    cursor.execute(query)
    return cursor.fetchall()


def deleteUser(conn , id):
    cursor = conn.cursor()
    query = "DELETE FROM users WHERE id=? "
    cursor.execute(query, (id,))
    conn.commit()



# -------------------------------------------------------------------------------
# Posts

def postsDB(conn):
    cursor = conn.cursor()
    cursor.execute(
        ''' CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Caption TEXT NOT NULL,
        imageurl TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        userid INTEGER NOT NULL,
        FOREIGN KEY (userid) REFERENCES users (id)
        )   
    '''
    )
    conn.commit()


def addPost(conn , caption , imageurl , userid):
    cursor = conn.cursor()
    query =" INSERT INTO posts (Caption,imageurl,userid) VALUES (?,?,?)  "
    cursor.execute(query,(caption , imageurl , userid))
    conn.commit()


def getAllPosts(conn):
    cursor=conn.cursor()
    query = "SELECT users.imageurl, users.username, posts.imageurl, posts.timestamp, posts.Caption , posts.id FROM posts JOIN users ON posts.userid = users.id WHERE posts.userid IS NOT NULL"
    cursor.execute(query)
    return cursor.fetchall()

def getUserPosts(conn,userid):
    cursor=conn.cursor()
    query = "SELECT users.imageurl , users.username , posts.imageurl , posts.timestamp , posts.Caption FROM posts JOIN users ON posts.userid = users.id WHERE posts.userid=?"
    cursor.execute(query,(userid,))
    return cursor.fetchall()

def deletePost(conn,id):
    cursor = conn.cursor()
    query = "DELETE FROM posts WHERE id=? "
    cursor.execute(query, (id,))
    conn.commit()



def getSPost(conn, postid):
    cursor = conn.cursor()
    query = '''SELECT * FROM posts WHERE id =?'''
    cursor.execute(query, (postid,))
    return cursor.fetchone()


# ---------------------------------------------------------------------
# Comments

def CommentDB(conn):
    cursor=conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()


def addComment(conn , userid, post_id , text):
    cursor = conn.cursor()
    query='''INSERT INTO comments (user_id,post_id,text) VALUES (?,?,?) '''
    cursor.execute(query,(userid,post_id,text))
    conn.commit()


def getcomment(conn , postid):
    cursor=conn.cursor()
    query = '''  SELECT  users.imageurl, users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = ?'''
    cursor.execute(query,(postid,))
    return cursor.fetchall()

# --------------------------------------------------------------
# search

def searchUsers(conn, username):
    cursor=conn.cursor()
    query = '''SELECT users.imageurl,users.username,posts.imageurl, posts.timestamp, posts.Caption, posts.id,posts.userid
        FROM posts
        JOIN users ON posts.userid = users.id
        WHERE users.username = ?'''
    cursor.execute(query,(username,))
    return cursor.fetchall()

