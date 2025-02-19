from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
# CORS(app)  # Enable CORS for cross-origin requests

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///careercraft.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    resumes = db.relationship('Resume', backref='user', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class CareerAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    industry = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    goals = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.JSON)

class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Resume Builder API
@app.route('/api/resume', methods=['POST'])
def create_resume():
    data = request.json
    try:
        new_resume = Resume(
            user_id=data['user_id'],
            content={
                'name': data['name'],
                'email': data['email'],
                'summary': data['summary'],
                'skills': data['skills'],
                'experience': data.get('experience', [])
            }
        )
        db.session.add(new_resume)
        db.session.commit()
        return jsonify({'message': 'Resume created successfully', 'id': new_resume.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Career Guidance API
@app.route('/api/career-assessment', methods=['POST'])
def career_assessment():
    data = request.json
    try:
        assessment = CareerAssessment(
            industry=data['industry'],
            experience_level=data['experience_level'],
            goals=data['goals']
            
        )
        
        # Here you would typically add AI processing logic
        # For demonstration, we'll return mock recommendations
        recommendations = {
            'courses': ["Advanced Python Programming", "Career Development Strategies"],
            'skills': ["Leadership", "Cloud Computing"],
            'timeline': ["3 months: Technical Skills", "6 months: Soft Skills"]
        }
        
        assessment.recommendations = recommendations
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Contact Form API
@app.route('/api/contact', methods=['POST'])
def handle_contact():
    data = request.json
    try:
        new_contact = ContactSubmission(
            name=data['name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message']
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({'message': 'Message received successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Statistics Endpoint
@app.route('/api/stats')
def get_stats():
    stats = {
        'resumes_created': Resume.query.count(),
        'users_registered': User.query.count(),
        'assessments_completed': CareerAssessment.query.count()
    }
    return jsonify(stats), 200

if __name__ == '__main__':
    app.run(debug=True)