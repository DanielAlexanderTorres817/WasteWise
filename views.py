from flask import Blueprint, render_template

views =Blueprint(__name__, "views")

@views.route("/")
def login():
    return render_template("login.html")