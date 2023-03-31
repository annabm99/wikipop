from market import app # Importing the app
from flask import render_template, redirect, url_for, flash, session # Import package to read templates
from market.models import User, Search # Import from the database
from market.forms import RegisterForm, LoginForm, SearchForm # Import register form from the forms file
from market import db # Import database to edit it
from flask_login import login_user, logout_user
from market import process
import json
import wikipedia

# HOMEPAGE
@app.route("/") # Root url
@app.route("/home") # Root url
def home_page():
    return render_template("home2.html") # Flask function that redirects to html file (it has to be imported previously)

# DYNAMIC ROUTE
@app.route("/about/<username>")
def about_page(username):
    return f"<h1>This is the about page of {username}</h1>"

@app.route("/input")
def input_page():
    name = "Anna"
    return render_template('input.html', item=name)
    # Whatever is put into name will be sent to the html jinja, and it will be displayed on the webpage


@app.route("/search_history")
def history_page():
    search = Search.query.all() # Refers to the Item table from the database, which will be displayed on the page
    return render_template("search_history.html", items=search)

@app.route("/new_search", methods=["GET", "POST"])
def search_page():
    form = SearchForm()
    if form.validate_on_submit():
        word = form.word.data
        session["word"] = word
        try:
            summary, num, length, ref, links = process.summary(word)
            session["summary"] = summary
            session["num"] = num
            session["length"] = length
            session["ref"] = ref
            session["links"] = links
            return redirect (url_for("result_page", word=word, summary=summary, num=num, length=length, ref=ref, links=links))
        except wikipedia.exceptions.DisambiguationError as e:
            options = (e.options)
            session["options"] = options
            return redirect (url_for("options_page" , word=word, options=options))
        except wikipedia.exceptions.PageError:
            flash(f"The word you typed in does not have an entry in Wikipedia, please try with a different word")
            return redirect (url_for("search_page"))
    if form.errors != {}: # if form.errors is not empty, check for errors
        for err_msg in form.errors.values(): # go through error messages
            # Instead of printing to the terminal, flash prints to the user interface so users can be aware of errors
            flash(f"There was an error with your request: {err_msg}")
    return render_template("search.html", form=form)
    
@app.route("/search_options", methods=["GET", "POST"])
def options_page():
    options = session["options"]
    word = session["word"]
    form = SearchForm()
    if form.validate_on_submit():
        word = form.word.data
        session["word"] = word
        try:
            summary, num, length, ref, links = process.summary(word)
            session["summary"] = summary
            session["length"] = length
            session["num"] = num
            session["ref"] = ref
            session["links"] = links
            return redirect (url_for("result_page", word=word, summary=summary, num=num, length=length, ref=ref, links=links))
        except wikipedia.exceptions.DisambiguationError as e:
            options = (e.options)
            session["options"] = options
            return redirect (url_for("options_page" , word=word, options=options))
    return render_template("options.html", word=word, options=options, form=form)

@app.route("/results",  methods=["GET", "POST"])
def result_page():
    word = session["word"]
    summary = session["summary"]
    num = session["num"]
    length=session["length"]
    links = session["links"]
    ref = session["ref"]
    process.make_graph(word, links)
    Search_to_create = Search(word=word) # this will go to password_setter
    db.session.add(Search_to_create)
    db.session.commit()
    return render_template("results.html", word = word, summary = summary, num = num, length = length, ref = ref, links = links)


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"]) # This route can support get and post requests
def register_page():
    form = RegisterForm() # Referring to register form in the forms.py file
    # This will only be executed if the user clicks on the validate button from the form:
    if form.validate_on_submit():
        # Referencing the database User table (and columns) to create new users with the information provided by the user
        User_to_create = User(username=form.username.data,
                            email_address=form.email_address.data,
                            password = form.password1.data) # this will go to password_setter
        db.session.add(User_to_create)
        db.session.commit()
        # If they create a user, redirect to the market page
        return redirect(url_for("search_page"))
    if form.errors != {}: # if form.errors is not empty, check for errors
        for err_msg in form.errors.values(): # go through error messages
            # Instead of printing to the terminal, flash prints to the user interface so users can be aware of errors
            flash(f"There was an error in creating the user: {err_msg}", category='danger')
    # Display fields of the form, through register.html file
    return render_template("register.html", form=form)

# Login page
@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists and password is correct
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f"Success! You are logged in as: {attempted_user.username}", category="success")
            return redirect (url_for("search_page"))
        else:
            flash("Username and password do not match! Please try again.", category="danger")
    return render_template("login.html", form = form)

# Logout option
@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been logged out!", category = "info")
    return redirect(url_for("home_page"))