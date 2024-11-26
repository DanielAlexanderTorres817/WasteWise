from flask import Blueprint, render_template

views =Blueprint(__name__, "views")

@views.route("/")
def landing():
    return render_template("landing.html")

@views.route("/login")
def login():
    return render_template("login.html")

# @views.route("/dashboard")
# def home():
#     return render_template("dashboard.html")
