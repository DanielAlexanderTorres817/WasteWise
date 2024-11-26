from flask import Blueprint, render_template

views =Blueprint(__name__, "views")

@views.route("/")
def login():
    return render_template("login.html")

@views.route("/landing")
def home():
    return render_template("landing.html")

# @views.route("/home")
# def home():
#     return render_template("home.html")
