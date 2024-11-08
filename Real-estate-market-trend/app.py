from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User, Property
from forms import RegistrationForm, LoginForm
from utils import fetch_json, fetch_xml, fetch_excel, fetch_from_api, fetch_html, validate_and_transform, fetch_csv
from sqlalchemy.exc import IntegrityError
import json



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Registration successful.')
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)

@app.route('/')
def mainn():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, role="Viewer")  # Default role
        db.session.add(user)
        db.session.commit()
        flash('Registration successful.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')  # Add chart rendering here

@app.route('/logout')
def logout():
    # Clear session data to log the user out
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))



# Fetch and store data in the database
@app.route('/fetch_data')
def fetch_data():
    data_sources = [
        fetch_json("sample_real_estate_data.json"),
        fetch_xml("sample_real_estate_data.xml"),
        fetch_excel("sample_real_estate_data.xlsx"),
        fetch_csv("sample_real_estate_data.csv"),
        fetch_html("sample_real_estate_data.html")
    ]

    for source_df in data_sources:
        source_df = validate_and_transform(source_df)
        for _, row in source_df.iterrows():
            try:
                property_entry = Property(
                    property_id=row['Property_ID'],
                    location=row['Location'],
                    price=row['Price'],
                    bedrooms=row['Bedrooms'],
                    bathrooms=row['Bathrooms'],
                    square_feet=row['Square_Feet'],
                    year_built=row['Year_Built'],
                    property_type=row['Property_Type'],
                    listing_status=row['Listing_Status']
                )
                db.session.add(property_entry)
            except IntegrityError:
                db.session.rollback()
    db.session.commit()
    flash("Data fetched and stored successfully.")
    return redirect(url_for('dashboard'))

@app.route('/data/price_over_time')
def price_over_time():
    # Query database for housing prices over time (example grouping by year)
    data = db.session.query(Property.year_built, db.func.avg(Property.price)).group_by(Property.year_built).all()
    result = {"labels": [str(year) for year, _ in data], "data": [price for _, price in data]}
    return jsonify(result)

@app.route('/data/property_type_distribution')
def property_type_distribution():
    # Query database for property type distribution
    data = db.session.query(Property.property_type, db.func.count(Property.property_type)).group_by(Property.property_type).all()
    result = {"labels": [ptype for ptype, _ in data], "data": [count for _, count in data]}
    return jsonify(result)

@app.route('/data/sales_pattern')
def sales_pattern():
    # Query database for sales status
    data = db.session.query(Property.listing_status, db.func.count(Property.listing_status)).group_by(Property.listing_status).all()
    result = {"labels": [status for status, _ in data], "data": [count for _, count in data]}
    return jsonify(result)

@app.route('/data/price_vs_square_feet')
def price_vs_square_feet():
    # Query database for price vs. square feet data
    data = db.session.query(Property.square_feet, Property.price).all()
    result = {"data": [{"x": sqft, "y": price} for sqft, price in data]}
    return jsonify(result)

@app.route('/data/region_sales_heatmap')
def region_sales_heatmap():
    # Placeholder data for regional sales heatmap - this assumes a region column exists
    data = db.session.query(Property.location, db.func.count(Property.location)).group_by(Property.location).all()
    result = {"labels": [location for location, _ in data], "data": [count for _, count in data]}
    return jsonify(result)

@app.route('/create_admin')
def create_admin():
    # Check if the admin user already exists
    existing_admin = User.query.filter_by(username="admin").first()
    if existing_admin:
        flash("Admin user already exists.")
        return redirect(url_for('login'))

    # Create a new admin user
    admin_user = User(username="admin", password="admin", is_admin=True, role="Admin")
    db.session.add(admin_user)
    db.session.commit()
    flash("Admin user created successfully.")
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    # Only allow access if the user is an admin
    if not session.get('is_admin'):
        flash("You do not have permission to access this page.")
        return redirect(url_for('dashboard'))

    # Retrieve all users to display on the dashboard
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/change_user_role', methods=['POST'])
def change_user_role():
    if not session.get('is_admin'):
        flash("You do not have permission to perform this action.")
        return redirect(url_for('dashboard'))

    user_id = request.form.get('user_id')
    new_role = request.form.get('new_role')

    user = User.query.get(user_id)
    if user:
        user.role = new_role
        db.session.commit()
        flash(f"Role for user {user.username} changed to {new_role}.")
    else:
        flash("User not found.")

    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
