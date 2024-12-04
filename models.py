from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(80), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)  

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comments = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(100), nullable=False)
    cleanliness = db.Column(db.String(50), nullable=False)
    busyness = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.Text)

    def __repr__(self):
        return f'<Survey {self.facility_name}>'

class Restroom(db.Model):
    __tablename__ = 'restrooms'  # Optional: explicitly name the table
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
    facility_name = db.Column(db.String(200), nullable=False)
    location_type = db.Column(db.String(100))
    operator = db.Column(db.String(100))
    status = db.Column(db.String(50))
    open = db.Column(db.String(50))
    hours_of_operation = db.Column(db.String(100))
    accessibility = db.Column(db.String(50))
    restroom_type = db.Column(db.String(50))
    changing_stations = db.Column(db.String(100))
    additional_notes = db.Column(db.Text)
    website = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_1 = db.Column(db.String(100))  # This could store point data as text for now
    
    def __repr__(self):
        return f"<Restroom {self.facility_name}>"

   
