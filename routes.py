from flask import request, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Opportunity
from app import app
import secrets

ALLOWED_CATEGORIES = ['Internship', 'Volunteer', 'Job', 'Training']

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([full_name, email, password, confirm_password]):
        return jsonify({'error': 'All fields required'}), 400
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be 8+ characters'}), 400
    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    hashed_pw = generate_password_hash(password, method='sha256')
    new_admin = Admin(full_name=full_name, email=email, password_hash=hashed_pw)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Account created'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember_me', False)

    user = Admin.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    login_user(user, remember=remember)
    return jsonify({'status': 'success', 'message': 'Logged in'}), 200


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = Admin.query.filter_by(email=email).first()
    if user:
        token = secrets.token_urlsafe(32)
        print(f"Reset link: http://localhost:5000/reset/{token}")
    return jsonify({'status': 'success', 'message': 'Reset link sent if email exists'}), 200


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success'}), 200


@app.route('/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()
    output = []
    for op in ops:
        output.append({
            'id': op.id,
            'name': op.name,
            'category': op.category,
            'duration': op.duration,
            'start_date': op.start_date,
            'description': op.description,
            'skills': op.skills,
            'max_applicants': op.max_applicants,
        })
    return jsonify({'status': 'success', 'data': output}), 200


@app.route('/opportunities', methods=['POST'])
@login_required
def add_opportunity():
    data = request.get_json()
    if data.get('category') not in ALLOWED_CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400

    new_op = Opportunity(
        name=data.get('name'),
        duration=data.get('duration'),
        start_date=data.get('start_date'),
        description=data.get('description'),
        skills=data.get('skills'),
        category=data.get('category'),
        max_applicants=data.get('max_applicants'),
        admin_id=current_user.id
    )
    db.session.add(new_op)
    db.session.commit()
    return jsonify({'status': 'success', 'id': new_op.id}), 201


@app.route('/opportunities/<int:id>', methods=['GET'])
@login_required
def get_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'status': 'success', 'data': {
        'id': op.id,
        'name': op.name,
        'category': op.category,
        'duration': op.duration,
        'description': op.description,
        'skills': op.skills,
        'max_applicants': op.max_applicants
    }}), 200


@app.route('/opportunities/<int:id>/edit', methods=['POST', 'PUT'])
@login_required
def edit_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json()
    op.name = data.get('name', op.name)
    op.duration = data.get('duration', op.duration)
    op.category = data.get('category', op.category)
    op.description = data.get('description', op.description)
    op.skills = data.get('skills', op.skills)
    op.max_applicants = data.get('max_applicants', op.max_applicants)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Updated'}), 200


@app.route('/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(op)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Deleted'}), 200