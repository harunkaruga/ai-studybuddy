#!/usr/bin/env python3
"""
Demo version of AI Study Buddy Flashcard Generator
This version runs without MySQL for testing purposes.
"""

from flask import Flask, render_template, request, jsonify
import openai
import json
import os
from datetime import datetime
import uuid
from config import Config

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
openai.api_key = Config.OPENAI_API_KEY

# In-memory storage for demo
flashcards_storage = []
sessions_storage = []

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

def save_flashcards_demo(flashcards, subject="General"):
    """Save flashcards to in-memory storage"""
    saved_ids = []
    for card in flashcards:
        card_id = str(uuid.uuid4())
        card_data = {
            'id': card_id,
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
        
        # Save to in-memory storage
        card_ids = save_flashcards_demo(flashcards, subject)
        
        return jsonify({
            'flashcards': flashcards,
            'card_ids': card_ids,
            'message': f'Successfully generated {len(flashcards)} flashcards!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/flashcards')
def get_flashcards():
    """Get all flashcards from in-memory storage"""
    return jsonify({'flashcards': flashcards_storage})

@app.route('/save-session', methods=['POST'])
def save_session():
    """Save a study session"""
    try:
        data = request.get_json()
        session_name = data.get('session_name', 'Study Session')
        flashcard_ids = data.get('flashcard_ids', [])
        
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
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
    """Export flashcards in different formats"""
    if format == 'json':
        return jsonify({'flashcards': flashcards_storage})
    elif format == 'pdf':
        return jsonify({'flashcards': flashcards_storage, 'format': 'pdf'})
    else:
        return jsonify({'error': 'Unsupported format'}), 400

@app.route('/demo-info')
def demo_info():
    """Show demo information"""
    return jsonify({
        'message': 'This is a demo version running without MySQL',
        'storage': {
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
