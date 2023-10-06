from flask import Flask, redirect, render_template, flash, session, request
from models import connect_db, db, User, Feedback
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)

toolbar = DebugToolbarExtension()


# def redirector():
#     if 'user_id' not in session:


@app.route("/")
def redirect_home():
    db.create_all()
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = RegisterForm()

    if "user_id" in session:
        username = session["user_id"]
        flash("You are already logged in!", "danger")
        return redirect(f"/users/{username}")

    if form.validate_on_submit():
        print("************SUCCESS*************")
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password_check = form.password_check.data
        if password != password_check:
            flash("Passwords must match!", "danger")
            return render_template("register.html", form=form)
        user = User.register(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken. Please pick another")
            return render_template("register.html", form=form)
        session["user_id"] = user.username
        flash(f"Welcome {user.first_name}!", "success")
        return redirect(f"/users/{user.username}")
    return render_template("register.html", form=form)


@app.route("/secret")
def show_secret():
    if "user_id" not in session:
        flash("You are not authorized to view this page!", "danger")
        return redirect("/register")
    username = session["user_id"]
    return redirect(f"/users/{username}")
    # return render_template("secret.html")


@app.route("/login", methods=["GET", "POST"])
def login_user():
    form = LoginForm()

    if "user_id" in session:
        username = session["user_id"]
        flash("You are already logged in!", "danger")
        return redirect(f"/users/{username}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("login.html", form=form)


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    flash("You have been logged out!", "success")
    return redirect("/")


@app.route("/users/<username>")
def show_user_details(username):
    if "user_id" in session:
        if username == session["user_id"]:
            user = User.query.get_or_404(username)
            # reversed so updates and new posts show at the top (kinda like a recent posts)
            feedback = reversed(Feedback.query.filter_by(username=username).all())
            return render_template("user_details.html", user=user, feedback=feedback)
    flash("You are not authorized to view this page!", "danger")
    return redirect("/")


@app.route("/users/<username>/delete")
def delete_user(username):
    if "user_id" in session:
        if username == session["user_id"]:
            session.pop("user_id")
            user = User.query.get_or_404(username)
            db.session.delete(user)
            db.session.commit()
            return redirect("/")
    flash("You are not authorized to complete this action!", "danger")
    return redirect("/")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    if "user_id" in session:
        if username == session["user_id"]:
            form = FeedbackForm()
            if form.validate_on_submit():
                feedback = Feedback(
                    title=form.title.data, content=form.content.data, username=username
                )
                db.session.add(feedback)
                db.session.commit()
                return redirect(f"/users/{username}")
            return render_template("add_feedback.html", form=form)
    flash("You are not authorized to view this page!", "danger")
    return redirect("/")


@app.route("/feedback/<id>/update", methods=["GET", "POST"])
def update_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if "user_id" in session:
        if feedback.username == session["user_id"]:
            form = FeedbackForm(obj=feedback)
            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data
                db.session.commit()
                return redirect(f"/users/{feedback.username}")
            else:
                return render_template("update_feedback.html", form=form)
    flash("You are not authorized to view this page!", "danger")
    return redirect("/")


@app.route("/feedback/<id>/delete", methods=["POST"])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if "user_id" in session:
        if feedback.username == session["user_id"]:
            db.session.delete(feedback)
            db.session.commit()
            flash("Successfully deleted feedback", "success")
            return redirect(f"/users/{session['user_id']}")
    flash("You are not authorized to complete this action!", "danger")
    return redirect("/")
