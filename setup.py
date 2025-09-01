#!/usr/bin/env python3
"""
Setup script for AI Study Buddy Flashcard Generator
This script helps users set up the project and check dependencies.
"""

import os
import sys
import subprocess
import mysql.connector
from config import Config

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'openai',
        'mysql-connector-python',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            return False
    
    return True

def check_mysql_connection():
    """Check MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password']
        )
        conn.close()
        print("✅ MySQL connection successful")
        return True
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n🔧 To fix this:")
        print("1. Make sure MySQL server is running")
        print("2. Update database credentials in config.py or set environment variables")
        print("3. Create a .env file with your database settings")
        return False

def check_openai_key():
    """Check if OpenAI API key is configured"""
    if Config.OPENAI_API_KEY == 'your-openai-api-key-here':
        print("⚠️  OpenAI API key not configured")
        print("\n🔧 To fix this:")
        print("1. Get an API key from https://platform.openai.com/")
        print("2. Create a .env file with: OPENAI_API_KEY=your_key_here")
        print("3. Or set the environment variable directly")
        return False
    else:
        print("✅ OpenAI API key configured")
        return True

def create_env_template():
    """Create a template .env file if it doesn't exist"""
    env_file = '.env'
    if not os.path.exists(env_file):
        print("\n📝 Creating .env template file...")
        with open(env_file, 'w') as f:
            f.write("""# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here

# Database Configuration (optional - can be set in config.py)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=flashcards_db
""")
        print("✅ .env template created!")
        print("⚠️  Please edit .env file with your actual credentials")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 AI Study Buddy - Setup Check")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return
    
    print("\n🗄️  Checking MySQL connection...")
    mysql_ok = check_mysql_connection()
    
    print("\n🤖 Checking OpenAI configuration...")
    openai_ok = check_openai_key()
    
    print("\n📁 Creating environment file...")
    create_env_template()
    
    print("\n" + "=" * 40)
    if mysql_ok and openai_ok:
        print("🎉 Setup complete! You can now run the application:")
        print("   python app.py")
    else:
        print("⚠️  Setup incomplete. Please fix the issues above before running the app.")
    
    print("\n📖 For more information, see README.md")

if __name__ == '__main__':
    main()

