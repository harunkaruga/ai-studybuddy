#!/usr/bin/env python3
"""
Demo version of AI Study Buddy Flashcard Generator
This version runs without MySQL for testing purposes.
"""

from flask import Flask, render_template, request, jsonify
import openai
import json
import os
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
from config import Config

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
openai.api_key = Config.OPENAI_API_KEY

# In-memory storage for demo
flashcards_storage = []
sessions_storage = []
users_storage = []
sessions_storage_auth = []

# Simple user management for demo
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
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    
    session_data = {
        'id': session_id,
        'user_id': user_id,
        'session_token': session_token,
        'expires_at': expires_at
    }
    sessions_storage_auth.append(session_data)
    return session_token

def verify_session_token(session_token):
    """Verify session token and return user info"""
    for session in sessions_storage_auth:
        if session['session_token'] == session_token and session['expires_at'] > datetime.now():
            # Find user
            for user in users_storage:
                if user['id'] == session['user_id']:
                    return {
                        'user_id': user['id'],
                        'username': user['username'],
                        'email': user['email']
                    }
    return None

def generate_flashcards(notes, num_cards=5):
    """Generate flashcards using OpenAI API"""
    try:
        prompt = f"""
        Create {num_cards} educational flashcards from the following study notes. 
        For each flashcard, provide a clear question and a comprehensive answer.
        Format the response as a JSON array with 'question' and 'answer' fields.
        
        Study Notes:
        {notes}
        
        Generate {num_cards} flashcards that cover the key concepts and important details.
        """
        
        response = openai.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an educational assistant that creates effective flashcards from study materials."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=Config.OPENAI_MAX_TOKENS,
            temperature=Config.OPENAI_TEMPERATURE
        )
        
        # Parse the response
        content = response.choices[0].message.content
        try:
            # Look for JSON array in the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                flashcards = json.loads(json_str)
                return flashcards
            else:
                return create_fallback_flashcards(notes, num_cards)
        except json.JSONDecodeError:
            return create_fallback_flashcards(notes, num_cards)
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return create_fallback_flashcards(notes, num_cards)

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

def save_flashcards_demo(flashcards, subject="General", user_id=None):
    """Save flashcards to in-memory storage"""
    saved_ids = []
    for card in flashcards:
        card_id = str(uuid.uuid4())
        card_data = {
            'id': card_id,
            'user_id': user_id,
            'question': card['question'],
            'answer': card['answer'],
            'subject': subject,
            'created_at': datetime.now().isoformat()
        }
        flashcards_storage.append(card_data)
        saved_ids.append(card_id)
    return saved_ids

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
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
        sessions_storage_auth[:] = [s for s in sessions_storage_auth if s['session_token'] != session_token]
        
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
        
        # Generate flashcards
        flashcards = generate_flashcards(notes, num_cards)
        
        # Save to in-memory storage with user context
        card_ids = save_flashcards_demo(flashcards, subject, user['user_id'])
        
        return jsonify({
            'flashcards': flashcards,
            'card_ids': card_ids,
            'message': f'Successfully generated {len(flashcards)} flashcards!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/flashcards')
def get_flashcards():
    """Get user's flashcards from in-memory storage"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = verify_session_token(session_token)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get only user's flashcards
    user_flashcards = [card for card in flashcards_storage if card.get('user_id') == user['user_id']]
    
    return jsonify({'flashcards': user_flashcards})

@app.route('/save-session', methods=['POST'])
def save_session():
    """Save a study session"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = verify_session_token(session_token)
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        session_name = data.get('session_name', 'Study Session')
        flashcard_ids = data.get('flashcard_ids', [])
        
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'user_id': user['user_id'],
            'session_name': session_name,
            'flashcard_ids': flashcard_ids,
            'created_at': datetime.now().isoformat()
        }
        
        sessions_storage.append(session_data)
        
        return jsonify({'session_id': session_id, 'message': 'Session saved successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/<format>')
def export_flashcards(format):
    """Export user's flashcards in different formats"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = verify_session_token(session_token)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get only user's flashcards
    user_flashcards = [card for card in flashcards_storage if card.get('user_id') == user['user_id']]
    
    if format == 'json':
        return jsonify({'flashcards': user_flashcards})
    elif format == 'pdf':
        return jsonify({'flashcards': user_flashcards, 'format': 'pdf'})
    else:
        return jsonify({'error': 'Unsupported format'}), 400

@app.route('/user/sessions')
def get_user_sessions():
    """Get user's study sessions"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = verify_session_token(session_token)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get only user's sessions
    user_sessions = [session for session in sessions_storage if session.get('user_id') == user['user_id']]
    
    return jsonify({'sessions': user_sessions})

@app.route('/status')
def get_status():
    """Get application status and configuration"""
    return jsonify({
        'database_available': False,
        'openai_configured': Config.OPENAI_API_KEY not in ['demo-mode-no-api-key', 'your-openai-api-key-here'],
        'mode': 'demo',
        'message': 'Demo mode - running without database',
        'auth_required': True,
        'features': {
            'flashcard_generation': True,
            'user_registration': True,
            'user_login': True,
            'save_flashcards': True,
            'export_flashcards': True,
            'save_sessions': True
        }
    })

@app.route('/demo-info')
def demo_info():
    """Show demo information"""
    return jsonify({
        'message': 'This is a demo version running without MySQL',
        'storage': {
            'users_count': len(users_storage),
            'flashcards_count': len(flashcards_storage),
            'sessions_count': len(sessions_storage)
        }
    })

if __name__ == '__main__':
    print("🚀 Starting AI Study Buddy Demo Mode")
    print("⚠️  This version runs without MySQL - data will be lost on restart")
    print("🌐 Application will be available at: http://localhost:5000")
    print("📖 For full version with database, run: python app.py")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

