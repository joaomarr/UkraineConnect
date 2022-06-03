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

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    photo_filename = db.Column(db.String)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Text, nullable=False)
    long = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)


@app.route("/")
@login_required
def home():
    """Show all messages"""
    posts = db.session.query(Posts).all()
    user = db.session.query(Users).filter_by(user_id=session["user_id"]).first()
    return render_template("home.html", posts=posts, user=user)

@app.route("/login", methods=["POST", "GET"])
def login():
    """Introduction and login page"""
    session.clear()
    posts = Posts.query.all()

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

        user = db.session.query(Users).filter_by(email=email).first()

        if not check_password_hash(user.hash, password):
            message = {'text': "Invalid username and/or password", 'category': "danger"}
            return render_template("login.html", posts=posts, message=message)

        session["user_id"] = user.user_id

        return redirect("/")

    else:
        return render_template("login.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register the user"""
    posts = Posts.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            message = {'text': "Must provide requested fields", 'category': "warning"}
            return render_template("register.html", posts=posts, message=message)

        hash = generate_password_hash(password)

        if not db.session.query(Users).filter_by(email=email).first():
            try:
                user = Users(name=name, email=email, hash=hash)
                db.session.add(user)
                db.session.commit()
            except:
                message = {'text': "Something gone wrong", 'category': "danger"}
                return render_template("register.html", posts=posts, message=message)
        else:
            message = {'text': 'You already have an account, <a href="/login">sign in</a>.', 'category': "danger"}
            return render_template("register.html", posts=posts, message=message)

        session["user_id"] = db.session.query(Users).filter_by(email=email).first().user_id

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    """Post user comments"""
    user = db.session.query(Users).filter_by(user_id=session["user_id"]).first()
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
            post = Posts(user_id=session["user_id"], text=text, title=title, lat=lat, long=long)
            db.session.add(post)
            db.session.commit()
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

            user = db.session.query(Users).filter_by(user_id=session['user_id']).first()
            user.photo_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                db.session.commit()
                message = {'text': "Your profile image was changed successfuly!", 'category': 'success'}
                user = db.session.query(Users).filter_by(user_id=session["user_id"]).first()
                return render_template("profile.html", user=user, message=message)
            except:
                message = {'text': "Something gone wrong!", 'category': 'success'}
                user = db.session.query(Users).filter_by(user_id=session["user_id"]).first()
                return render_template("profile.html", user=user, message=message)

    else:
        user = db.session.query(Users).filter_by(user_id=session["user_id"]).first()
        return render_template("profile.html", user=user)

@app.route("/getPosts", methods=["POST"])
def get_posts():
    posts = {}
    postsData = db.session.query(Posts).all()

    for postData in postsData:
        user_id = postData.user_id
        post_id = postData.id

        posts[post_id] = {
            'long': postData.long, 
            'lat': postData.lat,
            'title': postData.title,
            'text': postData.text,
            'postDate': str(postData.date),
            'postId': postData.id,
        }
    
        user_info = db.session.query(Users).filter_by(user_id=user_id).first()

        posts[post_id]['userName'] = user_info.name
        posts[post_id]['userPhotoFilename'] = user_info.photo_filename

        if "user_id" in session:
            if user_info.user_id == session["user_id"]:
                posts[post_id]["isFromUser"] = True
            else:
                posts[post_id]["isFromUser"] = False
            if db.session.query(Likes).filter_by(user_id=session["user_id"], post_id=post_id).first():   
                posts[post_id]["liked"] = True
            else:
                posts[post_id]["liked"] = False

        posts[post_id]["likes"] = db.session.query(Likes).filter_by(post_id=post_id).count()

    return json.dumps(posts)


@app.route("/editProfile", methods=["POST"])
@login_required
def editProfile():
    name = request.form.get('name')
    email = request.form.get('email')

    user = db.session.query(Users).filter_by(user_id=session["user_id"]).first()
    user_name = user.name
    user_email = user.email

    if name == user_name and email == user_email:
        return render_template("profile.html", user=user)

    email_already_taken = db.session.query(Users).filter_by(email=email).first()
    
    if name != user_name and email != user_email:
        user.name = name
        user.email = email

        if email_already_taken:
            message = {'text': "This email is already taken", 'category': 'warning'}
            return render_template("profile.html", user=user, message=message)

        try:
            db.session.commit()
            message = {'text': "Your name and email have been successfully changed!", 'category': 'success'}
            return render_template("profile.html", user=user, message=message)
        except:
            message = {'text': "Something gone wrong!", 'category': 'success'}
            return render_template("profile.html", user=user, message=message)

    if name != user_name:
        user.name = name
        try:
            db.session.commit()
            message = {'text': "Your name was changed successfully changed!", 'category': 'success'}
            print(db.session.query(Users).filter_by(user_id=session["user_id"]).first().name)
            return render_template("profile.html", user=user, message=message)
        except:
            message = {'text': "Something gone wrong!", 'category': 'success'}
            return render_template("profile.html", user=user, message=message)

    if email != user_email:
        if email_already_taken:
            message = {'text': "This email is already taken", 'category': 'warning'}
            return render_template("profile.html", user=user, message=message)

        user.email = email
        try:
            db.session.commit()
            message = {'text': "Your email was changed successfully changed!", 'category': 'success'}
            return render_template("profile.html", user=user, message=message)
        except:
            message = {'text': "Something gone wrong!", 'category': 'success'}
            return render_template("profile.html", user=user, message=message)


@socketio.on("submitLike")
def submitLike(data):
    id = data["id"]
    try:
        db.session.query(Users).filter_by(user_id=session["user_id"])
        db.session.query(Posts).filter_by(id=id)
    except:
        return print('not logged or not valid post')

    dataUser = {}
    dataUser["id"] = id

    print(db.session.query(Likes).filter_by(post_id=id, user_id=session["user_id"]).first())

    if db.session.query(Likes).filter_by(post_id=id, user_id=session["user_id"]).first() == None:
        like = Likes(post_id=id, user_id=session["user_id"])
        db.session.add(like)
        db.session.commit()
        dataUser["liked"] = False
        socketio.emit("showLike", dataUser)
    else:
        like = db.session.query(Likes).filter_by(post_id=id, user_id=session["user_id"]).first()
        db.session.delete(like)
        db.session.commit()
        dataUser["liked"] = True
        socketio.emit("showLike", dataUser)

@socketio.on("deletePost")
def deletePost(data):
    post_id = data["post_id"]
    user_id = db.session.query(Posts).filter_by(id=post_id).first().user_id

    if user_id == session["user_id"]:
        data["id"] = post_id
        try:
            post = db.session.query(Posts).filter_by(id=post_id, user_id=session["user_id"]).first()
            db.session.delete(post)
            db.session.commit()
            if db.session.query(Likes).filter_by(post_id=post_id).all():
                likes = db.session.query(Likes).filter_by(post_id=post_id).all()
                for like in likes:
                    db.session.delete(like)
                db.session.commit()
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