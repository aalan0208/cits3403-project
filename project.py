from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random
import time
import secrets
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizlet.db"  # SQLite database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# only works with gmail !!!!!!
# Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "citsproject3403@gmail.com"  # Replace with your email
app.config["MAIL_PASSWORD"] = "rlxh pqhp zsyo kmib"  # Replace with your email password
mail = Mail(app)


# User model
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    verification_token = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    quizzes = db.relationship("Quiz", backref="creator", lazy=True)


# Quiz model
class Quiz(db.Model):
    __tablename__ = "Quiz"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    time_limit = db.Column(db.Integer, nullable=False)  # Adding time_limit here
    creator_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)


# Question model
class Question(db.Model):
    __tablename__ = "Question"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("Quiz.id"), nullable=False)
    quiz = db.relationship("Quiz", backref=db.backref("questions", lazy=True))


# Result model
class Result(db.Model):
    __tablename__ = "Result"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("Quiz.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)


def setup_database():
    with app.app_context():
        db.create_all()


@app.route("/")
def root():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if not user:
            # If no user is found, print the message and flash the error
            print("No user found with that email.")
            flash("No user found with that email.", "error")
        else:
            # If a user is found, proceed with password and verification checks
            if check_password_hash(user.password, password):
                if user.is_verified:
                    session["user_id"] = user.id
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("dashboard"))
                else:
                    flash(
                        "Email not verified. Please check your email to verify your account.",
                        "error",
                    )
            else:
                flash("Invalid email or password. Please try again.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        confirm_email = request.form["confirm_email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if email != confirm_email:
            flash("Emails do not match. Please try again.", "error")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for("signup"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists! Please log in.", "error")
            return redirect(url_for("login"))

        try:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            verification_token = secrets.token_urlsafe(16)
            new_user = User(
                email=email,
                password=hashed_password,
                verification_token=verification_token,
            )
            db.session.add(new_user)
            db.session.commit()

            try:
                verification_link = url_for(
                    "verify_email", token=verification_token, _external=True
                )
                msg = Message(
                    "Email Verification",
                    sender="citsproject3403@gmail.com",
                    recipients=[email],
                )
                msg.body = f"Please click the following link to verify your email: {verification_link}"
                mail.send(msg)
                print("Verification email sent successfully")
            except Exception as e:
                print(f"Failed to send verification email: {e}")

            flash(
                "Account created successfully! Please check your email to verify your account.",
                "success",
            )
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/verify_email/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        flash("Email verified successfully! You can now log in.", "success")
        return redirect(url_for("login"))
    else:
        flash("Invalid or expired verification link.", "error")
        return redirect(url_for("signup"))


@app.route("/reset_pass", methods=["GET", "POST"])
def reset_pass():
    if request.method == "POST":
        email = request.form["email"]
        confirm_email = request.form["confirm_email"]

        if email != confirm_email:
            flash("Email addresses do not match. Please try again.", "error")
            return redirect(url_for("reset_pass"))

        user = User.query.filter_by(email=email).first()

        if user:
            reset_token = secrets.token_urlsafe(16)
            user.reset_token = reset_token
            db.session.commit()

            try:
                reset_link = url_for(
                    "reset_password_token", token=reset_token, _external=True
                )
                msg = Message(
                    "Password Reset Request",
                    sender="citsproject3403@gmail.com",
                    recipients=[email],
                )
                msg.body = f"Please click the following link to reset your password: {reset_link}"
                mail.send(msg)
                print("Password reset email sent successfully")
            except Exception as e:
                print(f"Failed to send password reset email: {e}")

            flash("Password reset link has been sent to your email.", "success")
        else:
            flash("Email not found. Please try again.", "error")
        return redirect(url_for("login"))

    return render_template("UsernamePassReset.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        password = request.form["password"]

        user.password = generate_password_hash(password, method="pbkdf2:sha256")
        user.reset_token = None
        db.session.commit()
        flash("Password reset successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_pass.html", token=token)


@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        quizzes = user.quizzes
        return render_template("main.html", user=user, quizzes=quizzes)
    else:
        flash("You are not logged in. Please log in to access the dashboard.", "error")
        print("User not logged in, redirecting to login.")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        grade = request.form["grade"]
        subject = request.form["subject"]
        query = request.form["query"]
        quizzes = Quiz.query.filter(
            Quiz.grade == grade, Quiz.subject == subject, Quiz.title.ilike(f"%{query}%")
        ).all()
        return render_template("search.html", quizzes=quizzes)
    return render_template("search.html")


@app.route("/main", methods=["GET", "POST"])
def return_to_main():
    return render_template("main.html")


@app.route("/create_quiz", methods=["GET", "POST"])
def create_quiz():
    if request.method == "POST":
        title = request.form["Title"]
        grade = request.form["Grade"]
        subject = request.form["Subject"]
        time_limit = request.form["Time"]
        user_id = session["user_id"]

        quiz = Quiz(
            title=title,
            grade=grade,
            subject=subject,
            time_limit=time_limit,
            creator_id=user_id,
        )
        db.session.add(quiz)
        db.session.commit()

        return redirect(url_for("dashboard"))
    return render_template("createQuiz.html")


@app.route("/quiz_entry/<int:quiz_id>", methods=["GET", "POST"])
def quiz_entry(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if request.method == "POST":
        session["quiz_id"] = quiz_id
        session["time_limit"] = int(request.form["time"]) * 60
        session["start_time"] = time.time()
        return redirect(url_for("quiz_page"))
    return render_template("quiz_entry.html", quiz=quiz)


@app.route("/quiz_page", methods=["GET"])
def quiz_page():
    quiz_id = session.get("quiz_id")
    if not quiz_id:
        return redirect(url_for("login"))

    quiz = Quiz.query.get(quiz_id)
    questions = quiz.questions
    random.shuffle(questions)

    time_limit = session.get("time_limit", 0)
    return render_template(
        "quiz_page.html", quiz=quiz, questions=questions, time_limit=time_limit
    )


@app.route("/result", methods=["GET", "POST"])
def result():
    end_time = time.time()
    start_time = session.get("start_time")
    time_limit = session.get("time_limit")

    if end_time - start_time > time_limit:
        return render_template("result.html", message="Time is up! Quiz closed.")

    if request.method == "POST":
        quiz_id = session.get("quiz_id")
        quiz = Quiz.query.get(quiz_id)
        questions = quiz.questions

        total_questions = len(questions)
        total_score = 0

        for question in questions:
            user_answer = request.form.get(str(question.id))
            if user_answer == question.correct_answer:
                total_score += 1

        percentage_score = (total_score / total_questions) * 100

        return render_template(
            "result.html",
            total_score=total_score,
            total_questions=total_questions,
            percentage_score=percentage_score,
        )

    return render_template("result.html", message="Quiz submitted successfully.")


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
