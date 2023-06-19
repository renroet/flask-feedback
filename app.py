from flask import Flask, redirect, request, render_template, jsonify, flash,session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Review
from forms import UserForm, SignIn, Feedback
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import text
from sqlalchemy import exc

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.debug = True

app.config['SECRET_KEY'] = 'not-so-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

bcrypt = Bcrypt()

@app.route('/')
def redirect_register():
    """Redirect to /register."""
    return redirect('/register')


@app.route('/register')
def show_register():
    """Show a form that when submitted will register/create a user. This form should accept a username, password, email, first_name, and last_name."""  

    """Make sure you are using WTForms and that your password input hides the characters that the user is typing!"""

    form = UserForm()
    
    return render_template('index.html', form=form)


@app.route('/register', methods=["POST"])
def register():
    """Process the registration form by adding a new user. Then redirect to /secret"""
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = bcrypt.generate_password_hash(pwd).decode('utf-8')
        new_user = User(username=username, password=password,email=email,  first_name=first_name, last_name=last_name)
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            
            return redirect(f'/users/{new_user.username}')
        except exc.IntegrityError:
            raise
    
    return redirect('/register')


@app.route('/login')
def show_loging():
    """Show a form that when submitted will login a user. This form should accept a username and a password."""

    """Make sure you are using WTForms and that your password input hides the characters that the user is typing!"""

    form = SignIn()

    return render_template('login.html', form=form)


@app.route('/login', methods=["POST"])
def login():
    """Show a form that when submitted will login a user. This form should accept a username and a password."""

    """Make sure you are using WTForms and that your password input hides the characters that the user is typing!"""

    """Process the login form, ensuring the user is authenticated and going to /secret if so."""

    form = SignIn()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = authenticate(username, pwd)
        if user:
            session['user'] = user.username
            return redirect(f'/users/{user.username}')

    return redirect ('/login')


@app.route('/users/<username>')
def show_secret(username):
    """Return the text “You made it!” (don’t worry, we’ll get rid of this soon)"""
    if session.get('user'):
        user = User.query.get(username)
        feedback = user.reviews
        
        return render_template('secret.html', user=user, feedback=feedback)
    
    flash('You must be logged in to view page', 'error')
    return redirect('/login')




def authenticate(username, pwd):
    user = User.query.get(username)
    if user:
        checked = bcrypt.check_password_hash(user.password, pwd)
        if checked:
            return user
    return False


@app.route('/logout')
def logout():
    session.pop('user')

    return redirect('/login')

@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    if session.get('user'):
        review = Review.query.get(feedback_id)
        user = review.user
        form = Feedback(obj=review)
        if form.validate_on_submit():
            review.title = form.title.data
            review.content = form.content.data
            db.session.commit()
            print(f'******************{review.username}**********')
            return redirect(f'/users/{review.username}')
        return render_template('update_feedback.html', form=form, review=review)
    flash('You must be logged in to view page', 'error')
    return redirect('/login')

@app.route('/feedback/<feedback_id>/delete', methods=["GET", "DELETE"])
def delete_feedback(feedback_id):
    if session.get('user'):
        review = Review.query.get(feedback_id)
        db.session.delete(review)
        db.session.commit()
        return redirect(f'/users/{review.username}')
    flash('You must be logged in to view page', 'error')
    return redirect('/login')

@app.route('/users/<username>/delete')
def delete_user(username):
    if session.get('user'):
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('user')
        return redirect('/login')
    flash('You must be logged in to view page', 'error')
    return redirect('/login')

@app.route('/users/<username>/feedback/add')
def show_add_feedback(username):
    if session.get('user'):
        form = Feedback()
        return render_template('feedback.html', form=form)
    flash('You must be logged in to view page', 'error')
    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=["POST"])
def feedback_add(username):
    if session.get('user'):
        form = Feedback()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            username = username
            new_feedback = Review(title=title, content=content,username=username)
            db.session.add(new_feedback)
            db.session.commit()
            print(f'********************************{username}*************')
            return redirect(f'/users/{username}')

        return render_template('feedback.html', form=form)
    flash('You must be logged in to view page', 'error')
    return redirect('/login') 