from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User, EnergyUsage
from forms import RegistrationForm, LoginForm
from utils import fetch_json, fetch_xml, fetch_excel, fetch_from_api, fetch_html, validate_and_transform, fetch_csv
from sqlalchemy.exc import IntegrityError
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def main():
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
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/fetch_data')
def fetch_data():
    data_sources = [
        fetch_json("energy_usage_data.json"),
        fetch_xml("energy_usage_data.xml"),
        fetch_excel("energy_usage_data.xlsx"),
        fetch_csv("energy_usage_data.csv"),
        fetch_html("energy_usage_data.html")
    ]

    for source_df in data_sources:
        source_df = validate_and_transform(source_df)
        for _, row in source_df.iterrows():
            try:
                energy_entry = EnergyUsage(
                    device_id=row['Device_ID'],
                    location=row['Location'],
                    energy_consumption_kwh=row['Energy_Consumption_kWh'],
                    carbon_emissions_kgco2e=row['Carbon_Emissions_kgCO2e'],
                    date=row['Date']
                )
                db.session.add(energy_entry)
            except IntegrityError:
                db.session.rollback()
    db.session.commit()
    flash("Data fetched and stored successfully.")
    return redirect(url_for('dashboard'))

@app.route('/data/energy_over_time')
def energy_over_time():
    data = db.session.query(EnergyUsage.date, db.func.avg(EnergyUsage.energy_consumption_kwh)).group_by(EnergyUsage.date).all()
    result = {"labels": [str(date) for date, _ in data], "data": [consumption for _, consumption in data]}
    return jsonify(result)

@app.route('/data/carbon_emissions_distribution')
def carbon_emissions_distribution():
    data = db.session.query(EnergyUsage.location, db.func.avg(EnergyUsage.carbon_emissions_kgco2e)).group_by(EnergyUsage.location).all()
    result = {"labels": [location for location, _ in data], "data": [emissions for _, emissions in data]}
    return jsonify(result)

# Admin Dashboard Route
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


if __name__ == '__main__':
    app.run(debug=True)
