from flask import Flask, render_template, request, redirect, url_for, session
import database as db

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"

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
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")

        success, message = db.create_user(username, password)
        if success:
            return redirect(url_for("login"))
        else:
            return render_template("signup.html", error=message)

    return render_template("signup.html")


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
