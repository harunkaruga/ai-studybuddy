#!/usr/bin/env python3
"""
Simplified version of AI Study Buddy for Render deployment
This version has minimal dependencies and should work reliably
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets

app = Flask(__name__)

# Simple configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'

# In-memory storage
flashcards_storage = []
users_storage = []
sessions_storage = []

# Simple CORS headers (no external dependencies)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def hash_password(password, salt=None):
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt, password_hash.hex()

def verify_password(password, stored_hash, stored_salt):
    """Verify password against stored hash"""
    _, computed_hash = hash_password(password, stored_salt)
    return computed_hash == stored_hash

def create_user_session(user_id):
    """Create a session for user"""
    session_token = secrets.token_urlsafe(32)
    session_data = {
        'user_id': user_id,
        'session_token': session_token,
        'expires_at': datetime.now() + timedelta(days=7)
    }
    sessions_storage.append(session_data)
    return session_token

def verify_session_token(session_token):
    """Verify session token and return user info"""
    for session in sessions_storage:
        if session['session_token'] == session_token and session['expires_at'] > datetime.now():
            for user in users_storage:
                if user['id'] == session['user_id']:
                    return {
                        'user_id': user['id'],
                        'username': user['username'],
                        'email': user['email']
                    }
    return None

def create_fallback_flashcards(notes, num_cards):
    """Create simple flashcards when AI fails"""
    sentences = notes.split('.')
    flashcards = []
    
    for i in range(min(num_cards, len(sentences))):
        if sentences[i].strip():
            question = f"What is the key point about: {sentences[i][:50]}..."
            answer = sentences[i].strip()
            flashcards.append({
                "question": question,
                "answer": answer
            })
    
    return flashcards

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if username or email already exists
        for user in users_storage:
            if user['username'] == username or user['email'] == email:
                return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create new user
        user_id = str(uuid.uuid4())
        salt, password_hash = hash_password(password)
        
        new_user = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'salt': salt,
            'created_at': datetime.now().isoformat()
        }
        
        users_storage.append(new_user)
        
        return jsonify({'message': 'User registered successfully!', 'user_id': user_id}), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user
        user = None
        for u in users_storage:
            if u['username'] == username:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash'], user['salt']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create session
        session_token = create_user_session(user['id'])
        
        return jsonify({
            'message': 'Login successful!',
            'user': {
                'user_id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'session_token': session_token
            }
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Remove session
        sessions_storage[:] = [s for s in sessions_storage if s['session_token'] != session_token]
        
        return jsonify({'message': 'Logout successful!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/profile')
def get_profile():
    """Get user profile"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = verify_session_token(session_token)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'user_id': user['user_id'],
        'username': user['username'],
        'email': user['email']
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate flashcards from study notes"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        notes = data.get('notes', '')
        subject = data.get('subject', 'General')
        num_cards = data.get('num_cards', 5)
        
        if not notes.strip():
            return jsonify({'error': 'Please provide study notes'}), 400
        
        # Check authentication
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = verify_session_token(session_token)
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Generate simple flashcards
        flashcards = create_fallback_flashcards(notes, num_cards)
        
        # Save to storage
        for card in flashcards:
            card_id = str(uuid.uuid4())
            card_data = {
                'id': card_id,
                'user_id': user['user_id'],
                'question': card['question'],
                'answer': card['answer'],
                'subject': subject,
                'created_at': datetime.now().isoformat()
            }
            flashcards_storage.append(card_data)
        
        return jsonify({
            'flashcards': flashcards,
            'message': f'Successfully generated {len(flashcards)} flashcards!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/flashcards')
def get_flashcards():
    """Get user's flashcards"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = verify_session_token(session_token)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get only user's flashcards
    user_flashcards = [card for card in flashcards_storage if card.get('user_id') == user['user_id']]
    
    return jsonify({'flashcards': user_flashcards})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'deployment': 'render-simple',
        'cors_enabled': True
    })

@app.route('/debug')
def debug_info():
    """Debug endpoint"""
    return jsonify({
        'app_name': 'AI Study Buddy (Simple)',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'users_count': len(users_storage),
        'sessions_count': len(sessions_storage),
        'flashcards_count': len(flashcards_storage),
        'cors_enabled': True,
        'endpoints': [
            '/',
            '/auth/register',
            '/auth/login',
            '/auth/logout',
            '/auth/profile',
            '/generate',
            '/flashcards',
            '/health',
            '/debug'
        ]
    })

@app.route('/status')
def get_status():
    """Get application status"""
    return jsonify({
        'database_available': False,
        'openai_configured': False,
        'mode': 'simple-demo',
        'message': 'Simple demo mode - running without external dependencies',
        'auth_required': True,
        'features': {
            'flashcard_generation': True,
            'user_registration': True,
            'user_login': True,
            'save_flashcards': True,
            'export_flashcards': False,
            'save_sessions': False
        }
    })

if __name__ == '__main__':
    print("🚀 Starting AI Study Buddy (Simple Version)")
    print("⚠️  This version runs without external dependencies")
    print("🌐 Application will be available at: http://localhost:5000")
    print("-" * 50)
    
    # Production configuration for Render
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
