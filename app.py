from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define mentor time slots
mentor_time_slots = {
    "Chandra Sir": ["12pm-1pm", "1pm-2pm", "2pm-3pm", "3pm-4pm", "4pm-5pm", "5pm-6pm", "6pm-7pm"],
    "Tushar Sir": ["11am-12pm", "12pm-1pm", "1pm-2pm"],
    "Amir Sir": ["3pm-4pm", "4pm-5pm", "5pm-6pm"]
}

# Blocked company list
blocked_companies = ["ABC", "bcd"]

# File path for booking data storage
data_file_path = 'data/bookings.json'


def load_booking_data():
    """Load booking data from the JSON file."""
    try:
        with open(data_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_booking_data(data):
    """Save booking data to the JSON file."""
    with open(data_file_path, 'w') as file:
        json.dump(data, file, indent=4)


def generate_unique_code():
    """Generate a unique code for booking."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def get_next_8_days():
    """Get a list of the next 8 days from the current date."""
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(8)]


@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_booking_data()
    dates = get_next_8_days() # Get the next 8 days dynamically
    mentors = list(mentor_time_slots.keys())

    if request.method == 'POST':
        user_name = request.form['user_name']
        technology = request.form['technology']
        company_name = request.form['company_name']
        round_name = request.form['round_name']
        mentor = request.form['mentor']
        date = request.form['date']
        time_slot = request.form['time']
        invite_link = request.form['invite_link']

        # Check for blocked company
        if company_name in blocked_companies:
            flash("This company is blocked.")
            return redirect(url_for('index'))

        # Check if all fields are filled
        if not (user_name and technology and company_name and round_name and mentor and date and time_slot and invite_link):
            flash("All fields are required!")
            return redirect(url_for('index'))

        # Load data and check the booking status
        bookings = load_booking_data()

        if round_name == 'Final':
            # Check for available slots or slots booked with '1st' round
            if mentor not in bookings:
                bookings[mentor] = {}
            if date not in bookings[mentor]:
                bookings[mentor][date] = {}

            if time_slot in bookings[mentor][date]:
                slot = bookings[mentor][date][time_slot]
                if slot.get('status') == 'Available':
                    # Add new booking for 'Final' round
                    bookings[mentor][date][time_slot] = {
                        'user': user_name,
                        'company': company_name,
                        'round': round_name,
                        'invite_link': invite_link,
                        'status': 'Booked'
                    }
                elif slot.get('status') == 'Booked' and slot.get('round') == '1st':
                    # Update existing booking to 'Final' round
                    bookings[mentor][date][time_slot].update({
                        'user': user_name,
                        'company': company_name,
                        'round': round_name,
                        'invite_link': invite_link,
                        'status': 'Booked'
                    })
                else:
                    flash("This slot is not available for 'Final' round booking.")
                    return redirect(url_for('index'))
            else:
                # Book a new slot if it doesn't exist
                bookings[mentor][date][time_slot] = {
                    'user': user_name,
                    'company': company_name,
                    'round': round_name,
                    'invite_link': invite_link,
                    'status': 'Booked'
                }
        else:
            # Add new booking for any round except 'Final'
            if mentor not in bookings:
                bookings[mentor] = {}
            if date not in bookings[mentor]:
                bookings[mentor][date] = {}
            
            if time_slot in bookings[mentor][date]:
                flash("This slot is already booked!")
                return redirect(url_for('index'))

            unique_code = generate_unique_code()
            bookings[mentor][date][time_slot] = {
                'user': user_name,
                'round': round_name,
                'invite_link': invite_link,
                'unique_code': unique_code,
                'status': 'Booked'
            }
            flash(f"Booking successful! Your unique code: {unique_code}")

        save_booking_data(bookings)
        return redirect(url_for('index'))

    return render_template('index.html', dates=dates, mentors=mentors, mentor_time_slots=mentor_time_slots, data=data)


@app.route('/cancel', methods=['POST'])
def cancel_booking():
    data = load_booking_data()
    unique_code = request.form['unique_code']

    for mentor in data:
        for date in data[mentor]:
            for time_slot in data[mentor][date]:
                if data[mentor][date][time_slot].get("unique_code") == unique_code:
                    del data[mentor][date][time_slot]
                    save_booking_data(data)
                    flash("Booking canceled successfully!")
                    return redirect(url_for('index'))

    flash("Invalid unique code or booking not found!")
    return redirect(url_for('index'))


@app.route('/available_slots', methods=['GET'])
def available_slots():
    """Fetch available time slots for a selected mentor and date."""
    mentor = request.args.get('mentor')
    date = request.args.get('date')

    data = load_booking_data()
    available_slots = []
    
    if mentor in mentor_time_slots:
        all_slots = set(mentor_time_slots[mentor])
        booked_slots = set(data.get(mentor, {}).get(date, {}).keys())
        available_slots = list(all_slots - booked_slots)
        booked_slots_info = {
            slot: details for slot, details in data.get(mentor, {}).get(date, {}).items()
            if details['status'] == 'Booked' and details['round'] == '1st'
        }
        available_slots.extend(booked_slots_info.keys())

    return jsonify({'available_slots': available_slots})


if __name__ == '__main__':
    app.run(debug=True)
