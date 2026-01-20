from flask import Flask, render_template, request, redirect, session, url_for
import threading
import database as db
from automation import get_state, run_automation_with_notification

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"

def logged_in():
    return session.get("logged_in", False)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_id = db.verify_user(username, password)
        if user_id:
            session["logged_in"] = True
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect("/")

    user_id = session["user_id"]
    user_config = db.get_user_config(user_id)
    state = get_state(user_id)

    return render_template(
        "dashboard.html",
        username=session["username"],
        user_id=user_id,
        config=user_config,
        state=state
    )

@app.route("/start", methods=["POST"])
def start():
    if not logged_in():
        return redirect("/")

    user_id = session["user_id"]
    config = db.get_user_config(user_id)
    state = get_state(user_id)

    if not state.running:
        state.running = True
        t = threading.Thread(
            target=run_automation_with_notification,
            args=(config, session["username"], state, user_id)
        )
        t.daemon = True
        t.start()

    return redirect("/dashboard")

@app.route("/stop", methods=["POST"])
def stop():
    user_id = session["user_id"]
    state = get_state(user_id)
    state.running = False
    db.set_automation_running(user_id, False)
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
