from flask import Flask
from views import views
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.register_blueprint(views, url_prefix = "/")
app.secret_key = "WASTEWISE"

#DATABASE CODE HERE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # SQLite database file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable unnecessary overhead


db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run(debug=True, port = 5000)

