from flask import Flask, render_template, request, redirect, url_for, session, flash
import database as db  # your db.py file

app = Flask(__name__)
app.secret_key = "Jam-Shahrukh"  # needed for flash messages

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")  # if you have confirm password

        if not username or not password or not confirm:
            flash("⚠️ All fields are required!")
            return redirect(url_for("signup"))

        if password != confirm:
            flash("❌ Passwords do not match!")
            return redirect(url_for("signup"))

        success, msg = db.create_user(username, password)
        if success:
            flash(f"✅ {msg} Please login now!")
            return redirect(url_for("login"))  # redirect to login page
        else:
            flash(f"❌ {msg}")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = db.verify_user(username, password)
        if user_id:
            session["logged_in"] = True
            session["user_id"] = user_id
            session["username"] = username
            flash(f"✅ Welcome back, {username}!")
            return redirect(url_for("home"))
        else:
            flash("❌ Invalid username or password!")

    return render_template("login.html")


@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_config = db.get_user_config(session["user_id"])
    return render_template("home.html", user_config=user_config)


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_config = db.get_user_config(session["user_id"])
    return render_template("dashboard.html", user_config=user_config)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))





