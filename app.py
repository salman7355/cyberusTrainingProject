from flask import Flask, render_template, request, redirect, url_for,flash,session
import appDB
import re
import hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
connection = appDB.connectDB()
app.secret_key="dskjbfdbgesoglkjdsd3493hrpeffe;l"
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])

@app.route("/")
def hello_world():
    if 'username' in session:
        if session['username'] == 'Admin':
            users = appDB.Admin_getAllUsers(connection)
            return render_template('adminScreen.html', users=users)
    return redirect(url_for("login"))


@app.route("/register" , methods=['POST' , 'GET'])
@limiter.limit("5 per minute")
def register():
    errorMessage = ''
    imageErrorMessage=''
    validExt=["jpeg", "jpg", "png"]
    if request.method=="POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        userImage  = request.files['image']

        checkUser = appDB.getUser_username(connection,username)
        if checkUser:
            errorMessage = "User Already Exists"
        else:
            imageurl = f"static/uploads/usersPP/{userImage.filename}"
            userImage.save(imageurl)

            # Password Validation
            lengthbool = False
            symbolBool = False
            upperBool = False
            imageBool = False
            passBool   = False

            # password length check
            if len(password) >= 8:
                lengthbool = True
            
            # password symbol check
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                symbolBool = True    
            
            # password uppercase check
            if any(char.isupper() for char in password):
                upperBool = True

            if lengthbool and symbolBool and upperBool:   
                passBool = True
            else:
                errorMessage ='Password must be more than 8 characters and at least one symbol and one Uppercase letter' 

            # Profile Picture Validation
            filename = userImage.filename
            extension = filename.rsplit('.',1)[1].lower() 
            if not extension in validExt:
                imageErrorMessage='Please Enter Valid Image'
            else:
                imageBool=True    

            if passBool and imageBool:
                appDB.AddUser(connection,email,username, password , imageurl)
                return redirect(url_for('login'))
    return render_template("register.html" , errorMessage=errorMessage , imageErrorMessage=imageErrorMessage)

@app.route("/login" , methods=['POST' , 'GET'])
@limiter.limit("5 per minute")
def login():
    errorMessage=''
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        user = appDB.getUser(connection, username)
        if user :
            if hash.is_password_match(password, user[3]):
                session['username']=user[1]
                session['userId']=user[0]
                session['image']=user[4]
                session['email']=user[2]
                if session['username'] == 'Admin':
                    return redirect(url_for("hello_world"))
                return redirect(url_for("posts"))
            else:
                return render_template("login.html", errorMessage="Please Check Your UserName and Your Password")  
        else:
            return render_template("login.html", errorMessage="Please Check Your UserName and Your Password")  
    return render_template("login.html", errorMessage=errorMessage)

@app.route("/posts" , methods=["POST" , "GET"])
def posts():
    search=''
    validExt = ["jpeg", "jpg", "png", "gif"]
    if 'username' in  session:
        if request.method == 'POST' and 'caption' in request.form and 'post' in request.files:
            caption = request.form['caption']
            userPost = request.files['post']
            

            filename = userPost.filename
            extension = filename.rsplit('.',1)[1].lower() 

            if not extension in validExt:
                return redirect(url_for('logout'))            
            else:
                imageurl = f"static/uploads/Posts/{userPost.filename}"
                userPost.save(imageurl)
                appDB.addPost(connection,caption,imageurl, session['userId'])
        if request.method == 'POST' and  'search' in request.form:
            search = request.form['search']
            
        searchedPosts = appDB.searchUsers(connection,search)    
        print(searchedPosts)
        x= len(searchedPosts)

        if not x > 0:
            posts = appDB.getAllPosts(connection)
        else:        
            posts = searchedPosts
        return render_template('posts.html', posts=posts , username=session['username'] , Userimage=session['image'] , email=session['email'])
    return "Login to enter this page"

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/my_profile')
def my_profile():
    userPosts = appDB.getUserPosts(connection,session['userId'])
    return render_template("profile.html", userPosts=userPosts , username=session['username'] , Userimage=session['image'] , email=session['email'])

@app.route("/delete_user/<string:id>" , methods=['POST',"GET"])
def delete_user(id):
    if 'username' in session and session['username'] == 'Admin':
        appDB.deleteUser(connection, id)
        return redirect(url_for("hello_world"))
    else:
        return "You are not authorized to access this page."
    
@app.route("/allPosts")
def allposts():
    if 'username' in session and session['username'] == 'Admin':
        posts = appDB.getAllPosts(connection)
        return render_template("AdminView.html", posts=posts)
    else:
        return "You are not authorized to access this page."

@app.route("/post/<string:id>" , methods=['POST',"GET"])
def postid(id):
    if 'username' in session:
        if request.method=="POST":
            text = request.form['commentText']
            appDB.addComment(connection,session['userId'] , id , text)
            return redirect(url_for('postid' , id=id))
        post = appDB.getSPost(connection,id)
        comments=appDB.getcomment(connection,id)
        print("--------------------------------------")
        print(post)
        print("--------------------------------------")
        return render_template("Posttt.html" , comments=comments , post=post)
    else:
        return "Login to access this page"    


@app.route("/delete_post/<string:id>" , methods=['POST',"GET"])
def delete_post(id):
    if 'username' in session and session['username'] == 'Admin':
        appDB.deletePost(connection, id)
        return redirect(url_for("allposts"))
    else:
        return "You are not authorized to access this page."

if __name__ == "__main__":
    appDB.DbInit(connection)
    appDB.postsDB(connection)
    appDB.CommentDB(connection)
    app.run(debug=True)