from flask import Flask, render_template, request, jsonify
import openai
import mysql.connector
import json
import os
from datetime import datetime
import uuid
from config import Config

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
OPENAI_API_KEY = Config.OPENAI_API_KEY

# Database configuration
DB_CONFIG = Config.DB_CONFIG

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def create_database():
    """Create database and tables if they don't exist"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS flashcards_db")
        cursor.execute("USE flashcards_db")
        
        # Create flashcards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id VARCHAR(36) PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                subject VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create study_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id VARCHAR(36) PRIMARY KEY,
                session_name VARCHAR(200),
                flashcard_ids JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables created successfully!")
        
    except Exception as e:
        print(f"Database setup error: {e}")

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
        
        response = openai.ChatCompletion.create(
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
        # Try to extract JSON from the response
        try:
            # Look for JSON array in the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                flashcards = json.loads(json_str)
                return flashcards
            else:
                # Fallback: create simple flashcards
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

def save_flashcards_to_db(flashcards, subject="General"):
    """Save flashcards to database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        saved_ids = []
        for card in flashcards:
            card_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO flashcards (id, question, answer, subject)
                VALUES (%s, %s, %s, %s)
            """, (card_id, card['question'], card['answer'], subject))
            saved_ids.append(card_id)
        
        conn.commit()
        cursor.close()
        conn.close()
        return saved_ids
        
    except Exception as e:
        print(f"Database save error: {e}")
        return []

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

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
        
        # Generate flashcards
        flashcards = generate_flashcards(notes, num_cards)
        
        # Save to database
        card_ids = save_flashcards_to_db(flashcards, subject)
        
        return jsonify({
            'flashcards': flashcards,
            'card_ids': card_ids,
            'message': f'Successfully generated {len(flashcards)} flashcards!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/flashcards')
def get_flashcards():
    """Get all flashcards from database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM flashcards ORDER BY created_at DESC")
        flashcards = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'flashcards': flashcards})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save-session', methods=['POST'])
def save_session():
    """Save a study session"""
    try:
        data = request.get_json()
        session_name = data.get('session_name', 'Study Session')
        flashcard_ids = data.get('flashcard_ids', [])
        
        session_id = str(uuid.uuid4())
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO study_sessions (id, session_name, flashcard_ids)
            VALUES (%s, %s, %s)
        """, (session_id, session_name, json.dumps(flashcard_ids)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'session_id': session_id, 'message': 'Session saved successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/<format>')
def export_flashcards(format):
    """Export flashcards in different formats"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM flashcards ORDER BY created_at DESC")
        flashcards = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if format == 'json':
            return jsonify({'flashcards': flashcards})
        elif format == 'pdf':
            # For now, return JSON. PDF generation can be added later
            return jsonify({'flashcards': flashcards, 'format': 'pdf'})
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create database on startup
    create_database()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
