from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from helpers import login_required, get_oblasts
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
import datetime
import requests
import json
import os


# Configure application
app = Flask(__name__)
app.secret_key = 'ukraineconnect'
socketio = SocketIO(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://jcbbzhfcombkdo:394fb3d023eba39a9ad5727189c8bc1f07c6af10cc257e6b4ac0960820363401@ec2-3-234-131-8.compute-1.amazonaws.com:5432/d38ao6p1p1btdb"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/profilephotos"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

if __name__ == '__main__':
    socketio.run(app)
Session(app)

db = SQLAlchemy(app)

class users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    photo_filename = db.Column(db.String)

class posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

class likes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

@app.route("/")
@login_required
def home():
    """Show all messages"""
    posts = db.engine.execute("SELECT * FROM posts")
    user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
    return render_template("home.html", posts=posts, user=user)


@app.route("/login", methods=["POST", "GET"])
def login():
    """Introduction and login page"""
    session.clear()
    posts = db.engine.execute("SELECT * FROM posts")

    if request.method == "POST":
        """Login confirmation"""

        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            message = {'text': "Must provide email", 'category': "warning"}
            return render_template("login.html", posts=posts, message=message)

        elif not password:
            message = {'text': "Must provide password", 'category': "warning"}
            return render_template("login.html", posts=posts, message=message)

        rows = db.engine.execute("SELECT * FROM users WHERE email=?", email)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            message = {'text': "Invalid username and/or password", 'category': "danger"}
            return render_template("login.html", posts=posts, message=message)

        flash("You're logged in")
        session["user_id"] = rows[0]["user_id"]

        return redirect("/")

    else:
        return render_template("login.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register the user"""
    posts = db.engine.execute("SELECT * FROM posts")
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            message = {'text': "Must provide requested fields", 'category': "warning"}
            return render_template("register.html", posts=posts, message=message)

        hash = generate_password_hash(password)

        if not db.engine.execute("SELECT * FROM users WHERE email=?", email):
            try:
                db.engine.execute("INSERT INTO users (name, email, hash) VALUES (?, ?, ?)", name, email, hash)
            except:
                message = {'text': "Something gone wrong", 'category': "danger"}
                return render_template("register.html", posts=posts, message=message)
        else:
            message = {'text': 'You already have an account, <a href="/login">sign in</a>.', 'category': "danger"}
            return render_template("register.html", posts=posts, message=message)

        session["user_id"] = db.engine.execute("SELECT user_id FROM users WHERE email=?" ,email)[0]["user_id"]

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    """Post user comments"""
    user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
    if request.method == "POST":

        adress = str(request.form.get("adress"))
        number = str(request.form.get("number"))
        city = str(request.form.get("city"))
        oblast = str(request.form.get("oblast"))
        zipcode = str(request.form.get("zipcode"))
        title = str(request.form.get("title"))
        text = str(request.form.get("text"))

        if not adress or not city or not oblast or not title or not text:
            message = {'text': 'Please, fill all the required fields', 'category': 'warning'}
            return render_template("post.html", message=message, oblasts=get_oblasts(), user=user)

        location = adress + ' ' + number + ' ' + city + ' ' + ' ' + zipcode;

        parameters = {
        "key": "D8vHFz1EnMylphGmYZfxlJPppbJGjfzJ",
        "location": location
        }

        response = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params=parameters).text
        data = json.loads(response)['results'][0]['locations'][0]
        lat = data['latLng']['lat']
        long = data['latLng']['lng']

        if data['adminArea1'] != 'UA':
            message = {'text': 'Please, the adress must be in Ukraine', 'category': 'danger'}
            return render_template("post.html", message=message, oblasts=get_oblasts(), user=user)

        try:
            db.engine.execute('INSERT INTO posts (user_id, text, title, lat, long) VALUES (?, ?, ?, ?, ?)', session['user_id'], text, title, lat, long)
        except:
            message = {'text': 'Something gone wrong', 'category': 'danger'}
            return render_template("post.html", message=message, oblasts=get_oblasts(), user=user)

        message = {'text': "Your post was published!", 'category': "success"}
        return render_template("post.html", message=message, oblast=get_oblasts(), user=user)

    else:
        return render_template("post.html", oblasts=get_oblasts(), user=user)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if request.files:
            file = request.files['file']
            filename = str(session["user_id"]) + "." + "png"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.engine.execute("UPDATE users SET photo_filename=? WHERE user_id=?", os.path.join(app.config['UPLOAD_FOLDER'], filename), session["user_id"])
            message = {'text': "Your profile image was changed successfuly!", 'category': 'success'}
            user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
            return redirect("/profile")

    else:
        user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
        return render_template("profile.html", user=user)

@app.route("/getPosts", methods=["POST"])
def get_posts():
    posts = {}
    postsData = db.engine.execute("SELECT * FROM posts")

    for postData in postsData:
        user_id = postData['user_id']
        post_id = postData['id']
        posts[post_id] = postData

        user_info = db.engine.execute("SELECT user_id, name, photo_filename FROM users WHERE user_id=?", user_id)[0]

        posts[post_id]['userName'] = user_info['name']
        posts[post_id]['userPhotoFilename'] = user_info['photo_filename']

        if "user_id" in session:
            if user_info["user_id"] == session["user_id"]:
                posts[post_id]["isFromUser"] = True
            else:
                posts[post_id]["isFromUser"] = False
            if db.engine.execute("SELECT * FROM likes WHERE user_id=? AND post_id=?", session["user_id"], post_id):
                posts[post_id]["liked"] = True
            else:
                posts[post_id]["liked"] = False

        posts[post_id]["likes"] = db.engine.execute("SELECT COUNT(*) FROM likes WHERE post_id=?", post_id)[0]["COUNT(*)"]

    return json.dumps(posts)


@app.route("/editProfile", methods=["POST"])
@login_required
def editProfile():
    name = request.form.get('name')
    email = request.form.get('email')

    user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
    user_name = user['name']
    user_email = user['email']

    if name == user_name and email == user_email:
        user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
        return render_template("profile.html", user=user)

    if name != user_name and email != user_email:
        db.engine.execute("UPDATE users SET name=?, email=? WHERE user_id=?", name, email, session['user_id'])
        user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
        message = {'text': "Your name and email have been successfully changed!", 'category': 'success'}
        return render_template("profile.html", user=user, message=message)

    if name != user_name:
        db.engine.execute("UPDATE users SET name=? WHERE user_id=?", name, session['user_id'])
        user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
        message = {'text': "Your name was changed successfully!", 'category': 'success'}
        return render_template("profile.html", user=user, message=message)

    if email != user_email:
        db.engine.execute("UPDATE users SET email=? WHERE user_id=?", email, session['user_id'])
        user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
        message = {'text': "Your email was changed successfully!", 'category': 'success'}
        return render_template("profile.html", user=user, message=message)


@socketio.on("submitLike")
def submitLike(data):
    id = data["id"]
    try:
        user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
        post = db.engine.execute("SELECT * FROM posts WHERE id=?", id)[0]
    except:
        return print('not logged or not valid post')

    dataUser = {}
    dataUser["id"] = id

    if db.engine.execute("SELECT * FROM likes WHERE user_id=? AND post_id=?", session["user_id"], id):
        db.engine.execute("DELETE FROM likes WHERE user_id=? AND post_id=?", session["user_id"], id)
        dataUser["liked"] = True
        socketio.emit("showLike", dataUser)
    else:
        db.engine.execute("INSERT INTO likes (user_id, post_id) VALUES(?,?)", session["user_id"], post['id'])
        dataUser["liked"] = False
        socketio.emit("showLike", dataUser)

@socketio.on("deletePost")
def deletePost(data):
    posts = db.engine.execute("SELECT * FROM posts")
    user = db.engine.execute("SELECT * FROM users WHERE user_id=?", session['user_id'])[0]
    post_id = data["post_id"]
    user_id = db.engine.execute("SELECT user_id FROM posts WHERE id=?", post_id)[0]['user_id']

    if user_id == session["user_id"]:
        data["id"] = post_id
        try:
            db.engine.execute("DELETE FROM posts WHERE user_id=? AND id=?", user_id, post_id)
            if db.engine.execute("SELECT * FROM likes WHERE post_id=?", post_id):
                db.engine.execute("DELETE FROM likes WHERE post_id=?", post_id)
        except:
            return
        return socketio.emit("postDeleted")
    else:
        return

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")