from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random
import time
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizlet.db'  # SQLite database URI
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    db.UniqueConstraint('email')
# Quiz model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    grade = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('quizzes', lazy=True))

# Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    quiz = db.relationship('Quiz', backref=db.backref('questions', lazy=True))

# Result model
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
    db.ForeignKeyConstraint(['user_id'], ['user.id'])
    db.ForeignKeyConstraint(['quiz_id'], ['quiz.id'])

try:
    with db.session.begin_nested():
        db.session.add(new_user)
        db.session.commit()
except IntegrityError:
    db.session.rollback()

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        User = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html')
# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        confirm_email = request.form['confirm_email']  # Add confirm email field
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if emails match
        if email != confirm_email:
            flash('Emails do not match. Please try again.', 'error')
            return redirect(url_for('signup'))

            # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists! Please log in.', 'error')
            return redirect(url_for('login'))

        try:
            # Create a new user
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('signup'))

        return render_template('signup.html')

# Main route (serves as homepage as well)
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        quizzes = user.quizzes
        return render_template('main.html', user=user, quizzes=quizzes)
    else:
        flash('You are not logged in. Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Homepage route
@app.route('/homepage')
def homepage():
    return redirect(url_for('dashboard'))

# Search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        grade = request.form['grade']
        subject = request.form['subject']
        query = request.form['query']
        quizzes = Quiz.query.filter(Quiz.grade == grade, Quiz.subject == subject, Quiz.title.ilike(f'%{query}%')).all()
        return render_template('search.html', quizzes=quizzes)
    return render_template('search.html')

# Add quiz route
@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        title = request.form['title']
        grade = request.form['grade']
        subject = request.form['subject']
        questions = request.form.getlist('question')
        answers = request.form.getlist('answer')
        correct_answers = request.form.getlist('correct_answer')
        if len(questions) != len(answers) or len(answers) != len(correct_answers):
            return render_template('add_quiz.html', message='Number of questions, answers, and correct answers should match')
        user_id = session['user_id']
        quiz = Quiz(title=title, grade=grade, subject=subject, creator_id=user_id)
        db.session.add(quiz)
        db.session.commit()
        for i in range(len(questions)):
            question = Question(question_text=questions[i], correct_answer=correct_answers[i], quiz_id=quiz.id)
            db.session.add(question)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('createQuiz.html')

# Quiz entry route
@app.route('/quiz_entry/<int:quiz_id>', methods=['GET', 'POST'])
def quiz_entry(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if request.method == 'POST':
        session['quiz_id'] = quiz_id
        session['time_limit'] = int(request.form['time']) * 60  # Store time limit in seconds
        session['start_time'] = time.time()  # Store start time
        return redirect(url_for('quiz_page'))
    return render_template('quiz_entry.html', quiz=quiz)

# Quiz page route
@app.route('/quiz_page', methods=['GET'])
def quiz_page():
    quiz_id = session.get('quiz_id')
    if not quiz_id:
        return redirect(url_for('login'))  # Redirect if quiz ID is not in session

    quiz = Quiz.query.get(quiz_id)
    questions = quiz.questions
    random.shuffle(questions)

    time_limit = session.get('time_limit', 0)
    return render_template('quiz_page.html', quiz=quiz, questions=questions, time_limit=time_limit)

# Result page route
@app.route('/result', methods=['GET', 'POST'])
def result():
    end_time = time.time()  # Get current time
    start_time = session.get('start_time')
    time_limit = session.get('time_limit')

    if end_time - start_time > time_limit:  # If time elapsed exceeds time limit
        return render_template('result.html', message='Time is up! Quiz closed.')

    if request.method == 'POST':
        quiz_id = session.get('quiz_id')
        quiz = Quiz.query.get(quiz_id)
        questions = quiz.questions

        total_questions = len(questions)
        total_score = 0

        for question in questions:
            # Get the user's answer from the submitted form
            user_answer = request.form.get(str(question.id))

            # Check if the user's answer matches the correct answer
            if user_answer == question.correct_answer:
                total_score += 1  # Increment score for correct answer

        # Calculate percentage score
        percentage_score = (total_score / total_questions) * 100

        return render_template('result.html', total_score=total_score, total_questions=total_questions, percentage_score=percentage_score)

    # Render the result page for GET requests
    return render_template('result.html', message='Quiz submitted successfully.')
