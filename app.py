import csv
from flask import Flask, jsonify, render_template, request, flash
from views import views
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import db, Restroom, Feedback, Survey
from flask import redirect, url_for

app = Flask(__name__)

app.register_blueprint(views, url_prefix = "/")
app.secret_key = "WASTEWISE LOL" #change later please

#DATABASE CODE HERE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # SQLite database file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable unnecessary overhead

db.init_app(app)

with app.app_context():
    db.create_all()
    #print("success!")

# Load CSV into a DataFrame
df = pd.read_csv('Public_Restrooms_20241201.csv')

with app.app_context():
    for _, row in df.iterrows():
        restroom = Restroom(
            facility_name=row['Facility Name'],
            location_type="Restroom", 
            operator=row['Operator'],
            status=row['Status'],
            open=row['Open'],
            hours_of_operation=row['Hours of Operation'],
            accessibility=row['Accessibility'],
            restroom_type=row['Restroom Type'],
            changing_stations=row['Changing Stations'],
            additional_notes=row['Additional Notes'],
            website=row['Website'],
            latitude=row['Latitude'],
            longitude=row['Longitude'],
            location_1=row['Location']
        )
        db.session.add(restroom)
    db.session.commit()
    print("Public restrooms data loaded successfully!")


    
@app.route('/show_restrooms')
def show_restrooms():
    # Query all restrooms from the database
    restrooms = Restroom.query.all()
    
    # Create a list to store formatted restroom details with HTML and CSS
    restroom_list = []
    for restroom in restrooms:
        restroom_list.append(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f9f9f9;">
                <h3 style="color: #2c3e50;">{restroom.facility_name}</h3>
                <p><strong style="color: #34495e;">Location:</strong> {restroom.location_type}</p>
                <p><strong style="color: #34495e;">Status:</strong> {restroom.status}</p>
                <p><strong style="color: #34495e;">Hours of Operation:</strong> {restroom.hours_of_operation}</p>
                <p><strong style="color: #34495e;">Website:</strong> <a href="{restroom.website}" target="_blank" style="color: #3498db; text-decoration: none;">{restroom.website}</a></p>
                <p><strong style="color: #34495e;">Accessibility:</strong> {restroom.accessibility}</p>
                <p><strong style="color: #34495e;">Restroom Type:</strong> {restroom.restroom_type}</p>
                <p><strong style="color: #34495e;">Changing Stations:</strong> {restroom.changing_stations}</p>
                <p><strong style="color: #34495e;">Additional Notes:</strong> {restroom.additional_notes}</p>
            </div>
        """)
    
    # Join the list into a single HTML string
    return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #ecf0f1;
                        margin: 0;
                        padding: 20px;
                    }}
                    h3 {{
                        margin: 0;
                        color: #2980b9;
                    }}
                    p {{
                        font-size: 14px;
                        color: #2c3e50;
                    }}
                    a {{
                        color: #3498db;
                    }}
                    .container {{
                        max-width: 900px;
                        margin: 0 auto;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 style="color: #2c3e50;">Public Restrooms</h2>
                    {''.join(restroom_list)}
                </div>
            </body>
        </html>
    """

@app.route('/map')
def show_map():
    print('before')
    # List to hold restroom data
    locations = []

    # Open the CSV file and read it
    with open('Public_Restrooms_20241201.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            locations.append({
                'facility_name': row.get('Facility Name', 'Unknown name'),
                'latitude': float(row['Latitude']) if row['Latitude'] else 0,
                'longitude': float(row['Longitude']) if row['Longitude'] else 0,
                'location_type': row.get('Location Type', 'Unknown type')
            })

    print('after')
    print(locations[0])

    # Render the map page, passing locations as JSON-compatible data
    return render_template('map.html', locations=locations)

@app.route('/get_markers', methods=['POST'])
def get_markers():
    data = request.json
    north = data["north"]
    south = data["south"]
    east = data["east"]
    west = data["west"]
    filter_type = data.get("filter", "all")

    # Query database for markers within bounds
    query = Restroom.query.filter(
        Restroom.latitude.between(south, north),
        Restroom.longitude.between(west, east)
    )

    # Apply filter if specified
    if filter_type == "restroom":
        query = query.filter(Restroom.location_type.ilike("restroom"))
    elif filter_type == "trash bin":
        query = query.filter(Restroom.location_type.ilike("trash bin"))

    # Debugging logs
    print(f"Filter type: {filter_type}, Query: {query}")

    markers = query.all()

    print(f"Returned {len(markers)} markers")  # Debugging log

    return jsonify([
        {
            "facility_name": marker.facility_name,
            "latitude": marker.latitude,
            "longitude": marker.longitude,
            "location_type": marker.location_type,
            "address": marker.location_1,
            "status": marker.status,
            "hours_of_operation": marker.hours_of_operation,
            "accessibility": marker.accessibility,
            "restroom_type": marker.restroom_type,
            "changing_stations": marker.changing_stations,
            "additional_notes": marker.additional_notes,
            "website": marker.website
        }
        for marker in markers
    ])

@app.route('/list')
def facility_list():
    # Fetch all facilities from the database
    facilities = Restroom.query.limit(100).all()

    # Render the facility list template with the fetched data
    return render_template('facility_list.html', facilities=facilities)

@app.route('/manage_facilities')
def manage_facilities():
    per_page = 100  # Number of facilities per page
    page = request.args.get('page', 1, type=int)  # Current page number

    # Fetch facilities with all relevant details, sorted by ID (newest first)
    facilities = Restroom.query.order_by(Restroom.id.desc()).paginate(page=page, per_page=per_page)

    return render_template('manage_facilities.html', facilities=facilities)




@app.route('/delete-restroom/<int:id>', methods=['POST'])
def delete_restroom(id):
    facility = Restroom.query.get_or_404(id)
    db.session.delete(facility)
    db.session.commit()
    flash('Facility deleted successfully!')
    return redirect(url_for('manage_facilities'))


@app.route('/add_facility', methods=['GET', 'POST'])
def add_facility():
    if request.method == 'POST':
        # Retrieve data from the form
        facility_name = request.form.get('facility_name')
        location_type = request.form.get('location_type')
        address = request.form.get('address')
        status = request.form.get('status')
        hours_of_operation = request.form.get('hours_of_operation')
        accessibility = request.form.get('accessibility')
        restroom_type = request.form.get('restroom_type')
        changing_stations = request.form.get('changing_stations')
        operator = request.form.get('operator')
        website = request.form.get('website')
        additional_notes = request.form.get('additional_notes')

        # Create a new facility
        new_facility = Restroom(
            facility_name=facility_name,
            location_type=location_type,
            location_1=address,
            status=status,
            hours_of_operation=hours_of_operation,
            accessibility=accessibility,
            restroom_type=restroom_type,
            changing_stations=changing_stations,
            operator=operator,
            website=website,
            additional_notes=additional_notes
        )
        db.session.add(new_facility)
        db.session.commit()
        flash('Facility added successfully!')
        return redirect(url_for('manage_facilities'))

    return render_template('add_facility.html')


@app.route('/edit_facility/<int:id>', methods=['GET', 'POST'])
def edit_facility(id):
    facility = Restroom.query.get_or_404(id)

    if request.method == 'POST':
        # Update facility details with form data
        facility.facility_name = request.form.get('facility_name')
        facility.location_type = request.form.get('location_type')
        facility.location_1 = request.form.get('address')
        facility.status = request.form.get('status')
        facility.hours_of_operation = request.form.get('hours_of_operation')
        facility.accessibility = request.form.get('accessibility')
        facility.restroom_type = request.form.get('restroom_type')
        facility.changing_stations = request.form.get('changing_stations')
        facility.operator = request.form.get('operator')
        facility.website = request.form.get('website')
        facility.additional_notes = request.form.get('additional_notes')

        db.session.commit()
        flash('Facility updated successfully!')
        return redirect(url_for('manage_facilities'))

    return render_template('edit_facility.html', facility=facility)





@app.route('/search')
def facility_search():
    search_query = request.args.get('search', '')  # Get the search query from the URL
    limit = 100

    # If a search query is provided, filter facilities
    if search_query:
        facilities = Restroom.query.filter(
            Restroom.facility_name.ilike(f"%{search_query}%")
        ).limit(limit).all()
    else:
        facilities = Restroom.query.limit(limit).all()

    # If the request is from AJAX, return only the table rows
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/facility_rows.html', facilities=facilities)

    # Render the full search page for normal requests
    return render_template('facility_search.html', facilities=facilities, search_query=search_query)

@app.route('/survey')
def survey():
    return render_template('restroom_survey.html')

@app.route('/submit-survey', methods=['POST'])
def submit_survey():
    # Process form data
    facility_name = request.form['facility_name']
    cleanliness = request.form.get('cleanliness')
    busyness = request.form.get('busyness')
    comments = request.form.get('comments')

    # Save the data to a database or log it
    new_survey = Survey(facility_name=facility_name, cleanliness=cleanliness, busyness=busyness, comments=comments)

    # Add and commit to the database
    db.session.add(new_survey)
    db.session.commit()

    # Render a success message
    return render_template('survey_submitted.html')

    # return redirect(url_for('view_surveys'))

# Route to view surveys
@app.route('/view_survey')
def view_survey():
    # Query all surveys ordered by facility name alphabetically
    surveys = Survey.query.order_by(Survey.facility_name).all()
    return render_template('view_survey.html', surveys=surveys)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    comments = request.form.get('comments')
    if comments:
        feedback_entry = Feedback(comments=comments)
        db.session.add(feedback_entry)
        db.session.commit()
    return render_template('feedback_submitted.html')

@app.route('/feedback_list')
def feedback_list():
    feedback_entries = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('feedback_list.html', feedback_entries=feedback_entries)

if __name__ == "__main__":
    app.run(debug=True, port = 5000)

