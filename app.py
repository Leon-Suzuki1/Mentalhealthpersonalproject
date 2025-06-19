from flask import Flask, request, jsonify
from auth import load_users, save_users, hash_password, check_password
from tracker import get_email_prefix, load_data, save_data, calculate_streak
import json
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- User Endpoints ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    gender = data.get('gender')
    coping_mechanisms = data.get('coping_mechanisms')
    if not all([email, password, age, gender, coping_mechanisms]):
        return jsonify({'error': 'Missing required fields'}), 400
    users = load_users()
    for user in users:
        if user['email'] == email:
            return jsonify({'error': 'Email already exists'}), 409
    hashed_password = hash_password(password)
    new_user = {
        'email': email,
        'password': hashed_password,
        'age': age,
        'gender': gender,
        'coping_mechanisms': coping_mechanisms
    }
    users.append(new_user)
    save_users(users)
    return jsonify({'message': 'Signup and onboarding complete!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    users = load_users()
    for user in users:
        if user['email'] == email:
            if 'password' not in user:
                return jsonify({'error': 'User account is incomplete'}), 400
            if check_password(user['password'], password):
                user_copy = user.copy()
                del user_copy['password']
                return jsonify({'message': 'Login successful!', 'user': user_copy}), 200
            else:
                return jsonify({'error': 'Incorrect password'}), 401
    return jsonify({'error': 'User not found'}), 404

# --- Entry Endpoints ---
@app.route('/entries', methods=['POST'])
def add_entry():
    data = request.json
    email = data.get('email')
    highlight = data.get('highlight')
    lowlight = data.get('lowlight')
    happiness = data.get('happiness')
    major_event = data.get('major_event')
    if not all([email, highlight, lowlight, happiness, major_event]):
        return jsonify({'error': 'Missing required fields'}), 400
    user_email_prefix = get_email_prefix(email)
    entry = {
        'timestamp': datetime.now().isoformat(),
        'highlight': highlight,
        'lowlight': lowlight,
        'happiness': happiness,
        'major_event': major_event
    }
    entries = load_data(user_email_prefix)
    entries.append(entry)
    save_data(entries, user_email_prefix)
    return jsonify({'message': 'Entry saved successfully!'}), 201

@app.route('/entries', methods=['GET'])
def get_entries():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Missing email parameter'}), 400
    user_email_prefix = get_email_prefix(email)
    entries = load_data(user_email_prefix)
    return jsonify({'entries': entries}), 200

@app.route('/streak', methods=['GET'])
def get_streak():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Missing email parameter'}), 400
    user_email_prefix = get_email_prefix(email)
    streak = calculate_streak(user_email_prefix)
    return jsonify({'streak': streak}), 200

if __name__ == '__main__':
    app.run(debug=True) 