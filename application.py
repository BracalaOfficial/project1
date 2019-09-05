import os

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return render_template('index.html', session=(session.get('username') is None))

    if request.method == 'POST':
        un = request.form.get('user')
        ps = request.form.get('pass')

        existUser = db.execute("SELECT COUNT(*) FROM users WHERE username = :username",
            {'username': un}).fetchone().count

        if existUser == 1:
            user = db.execute("SELECT * FROM users WHERE username = :username",
                {'username': un}).fetchone()

            if user.password == ps:
                session['username'] = [un]

                flash(f"You are successfully logged in account {un}!", 'smess')
                return redirect(url_for('search'))# return render_template('index.html', session=(session.get('username') is None))

            else:
                flash("Wrong password", 'emess')
                return redirect(url_for('login'))

        else:
            flash(f"Account with {un} username dosen't exist!", 'emess')
            return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        if session.get('username'):
            flash(f"You are already logged in as {session.get('username')[0]}", 'emess')
            return redirect(url_for('index'))
        if session.get('username') is None:
            return render_template('login.html', session=(session.get('username') is None))

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/', code=302)

@app.route("/registration", methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        if session.get('username') is None:
            return render_template('signup.html', session=(session.get('username') is None))
        else:
            flash(f"You are already logged in as {session.get('username')[0]}", 'emess')
            return redirect(url_for('index'))

    if request.method == 'POST':
        bannedChars = '1234567890`~!@#$%^&*()_-=+[]{ }:;"\',.<>/\\'

        firstName = request.form.get('firstname')
        lastName = request.form.get('lastname')
        username = request.form.get('user')
        cpass = request.form.get('createpass')
        rpass = request.form.get('repeatpass')

        for sign in firstName:
            if sign in bannedChars:
                flash("Fist name must contain letters only!", 'emess')
                return redirect(url_for('signup'))

        for sign in lastName:
            if sign in bannedChars:
                flash("Last name must contain letters only", 'emess')
                return redirect(url_for('signup'))

        users = db.execute("SELECT username FROM users").fetchall()

        for user in users:
            if user.username == username:
                flash(f"Account with username {username} alredy exist!", 'emess')
                return redirect(url_for('signup'))

        if cpass != rpass:
            flash("Passwords must be matched!", 'emess')
            return redirect(url_for('signup'))

        db.execute("INSERT INTO users (username, password, firstname, lastname) VALUES (:username, :password, :firstname, :lastname)",
            {'username': username, 'password': cpass, 'firstname': firstName, 'lastname': lastName})

        db.commit()

        session['username'] = [username]
        flash(f"Welcome {firstName}! You are successfully created account!", 'smess')
        return redirect(url_for('search'))

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        if session.get('username'):
            return render_template('search.html', session=(session.get('username') is None))
        else:
            flash("You need to log in!", 'emess')
            return redirect(url_for('login'))

    if request.method == "POST":
        dataSearch = request.form.get('searchdata')
        noresults = False
    
        books = db.execute(f"SELECT * FROM books WHERE title LIKE '%{dataSearch}%' OR author LIKE '%{dataSearch}%' OR isbn LIKE '%{dataSearch}%' ORDER BY title").fetchall()

        if len(books) == 0:
            noresults = True

        return render_template('search.html', session=(session.get('username') is None), books=books, noresults=noresults)

@app.route("/search/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
    if session.get('username'):
        binfo = db.execute("SELECT * FROM books WHERE isbn = :isbn", {'isbn': isbn}).fetchone()
        uinfo = db.execute("SELECT * FROM users WHERE username = :username", {'username': session.get('username')[0]}).fetchone()
        treviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {'book_id': binfo.id}).fetchall()
        isThisUserPostedReview = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id = :book_id AND user_id = :user_id", 
            {'book_id': binfo.id, 'user_id': uinfo.id}).fetchone()
        allusers = db.execute("SELECT * FROM users").fetchall()

        itupr = isThisUserPostedReview.count

        reviews = []

        for treview in treviews:
            for user in allusers:
                if treview.user_id == user.id:
                    reviews.append(Review(user.username, user.firstname, user.lastname, treview.comment))


        if request.method == "GET":
            return render_template('book.html', session=(session.get('username') is None), binfo=binfo, reviews=reviews, itupr=itupr)
        if request.method == "POST":
            comment = request.form.get('comment')
            db.execute("INSERT INTO reviews (book_id, user_id, comment) VALUES (:book_id, :user_id, :comment)",
                {'book_id': binfo.id, 'user_id': uinfo.id, 'comment': comment})
            db.commit()

            flash(f"Thank you {uinfo.firstname} for reviewing book {binfo.title}!", 'sess')
            return redirect(f'/search/book/{ binfo.isbn }')         
    else:
        flash("You need to log in!")
        return redirect(url_for('login'))

class Review(object):
    def __init__(self, uName, fName, lName, com):
        self.username = uName
        self.firstname = fName
        self.lastname = lName
        self.comment = com