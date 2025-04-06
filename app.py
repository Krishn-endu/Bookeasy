from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import re

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techbrand.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50))
    price = db.Column(db.Float)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def validate_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(email=data['email'], password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Print debug information
        print(f"Login attempt for email: {email}")

        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"User not found for email: {email}")
            return jsonify({'message': 'Invalid credentials'}), 401

        if not check_password_hash(user.password, password):
            print(f"Invalid password for email: {email}")
            return jsonify({'message': 'Invalid credentials'}), 401

        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email
            }
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Server error', 'error': str(e)}), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Service.query
    
    if search:
        query = query.filter(
            (Service.name.ilike(f'%{search}%')) |
            (Service.description.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter_by(category=category)
    
    services = query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'category': s.category,
        'price': s.price
    } for s in services])

@app.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify({
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'category': service.category,
        'price': service.price
    })

@app.route('/api/services', methods=['POST'])
@token_required
def create_service(current_user):
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400

    new_service = Service(
        name=data['name'],
        description=data.get('description', ''),
        category=data.get('category', ''),
        price=data.get('price', 0.0)
    )
    
    db.session.add(new_service)
    db.session.commit()

    return jsonify({
        'message': 'Service created successfully',
        'service': {
            'id': new_service.id,
            'name': new_service.name,
            'description': new_service.description,
            'category': new_service.category,
            'price': new_service.price
        }
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)