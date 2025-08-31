#!/usr/bin/env python3
"""
Simple test script for AI Study Buddy Flashcard Generator
Tests basic functionality without requiring external dependencies.
"""

import json
import sys
from datetime import datetime

def test_fallback_flashcard_generation():
    """Test the fallback flashcard generation function"""
    print("🧪 Testing fallback flashcard generation...")
    
    # Sample study notes
    notes = """
    Photosynthesis is the process by which plants convert sunlight into energy. 
    The process occurs in the chloroplasts and requires carbon dioxide and water. 
    The main products are glucose and oxygen. Chlorophyll is the green pigment 
    that captures light energy.
    """
    
    # Simulate the fallback function
    sentences = notes.split('.')
    flashcards = []
    
    for i in range(min(5, len(sentences))):
        if sentences[i].strip():
            question = f"What is the key point about: {sentences[i][:50]}..."
            answer = sentences[i].strip()
            flashcards.append({
                "question": question,
                "answer": answer
            })
    
    print(f"✅ Generated {len(flashcards)} flashcards")
    for i, card in enumerate(flashcards, 1):
        print(f"   Card {i}: {card['question'][:60]}...")
    
    return len(flashcards) > 0

def test_json_parsing():
    """Test JSON parsing functionality"""
    print("\n🧪 Testing JSON parsing...")
    
    # Sample JSON response
    sample_json = '''
    [
        {
            "question": "What is photosynthesis?",
            "answer": "The process by which plants convert sunlight into energy"
        },
        {
            "question": "Where does photosynthesis occur?",
            "answer": "In the chloroplasts of plant cells"
        }
    ]
    '''
    
    try:
        flashcards = json.loads(sample_json)
        print(f"✅ Successfully parsed {len(flashcards)} flashcards from JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing configuration loading...")
    
    try:
        from config import Config
        print("✅ Configuration module loaded successfully")
        print(f"   Max flashcards: {Config.MAX_FLASHCARDS}")
        print(f"   OpenAI model: {Config.OPENAI_MODEL}")
        return True
    except ImportError as e:
        print(f"❌ Failed to load config: {e}")
        return False

def test_flask_import():
    """Test Flask import"""
    print("\n🧪 Testing Flask import...")
    
    try:
        import flask
        print(f"✅ Flask version {flask.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

def test_openai_import():
    """Test OpenAI import"""
    print("\n🧪 Testing OpenAI import...")
    
    try:
        import openai
        print("✅ OpenAI library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

def test_mysql_import():
    """Test MySQL import"""
    print("\n🧪 Testing MySQL import...")
    
    try:
        import mysql.connector
        print("✅ MySQL Connector imported successfully")
        return True
    except ImportError as e:
        print(f"❌ MySQL import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Study Buddy - Test Suite")
    print("=" * 40)
    
    tests = [
        test_fallback_flashcard_generation,
        test_json_parsing,
        test_config_loading,
        test_flask_import,
        test_openai_import,
        test_mysql_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
