# AI Study Buddy — Flashcard Generator

**SDG Focus:** Quality Education (SDG 4)

A web application that automatically generates interactive flashcards from study notes using AI, making studying more efficient and engaging.

## 🚀 Features

- **AI-Powered Generation**: Automatically creates flashcards from pasted study notes using OpenAI's GPT-3.5
- **Interactive Flashcards**: Click to flip cards and reveal answers
- **Study Session Management**: Save and organize your study sessions
- **Export Functionality**: Export flashcards as JSON for backup
- **Responsive Design**: Works on desktop and mobile devices
- **Database Storage**: MySQL database for persistent storage
- **Shuffle Mode**: Randomize card order for better retention

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Database**: MySQL
- **AI**: OpenAI GPT-3.5 API
- **Styling**: Custom CSS with modern gradients and animations

## 📋 Prerequisites

Before running this application, make sure you have:

1. **Python 3.7+** installed
2. **MySQL Server** installed and running
3. **OpenAI API Key** (get one from [OpenAI Platform](https://platform.openai.com/))

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Flashcards
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL Database
1. Start your MySQL server
2. Create a database user (or use root)
3. Update the database configuration in `app.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'your_username',
       'password': 'your_password',
       'database': 'flashcards_db'
   }
   ```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📖 How to Use

### 1. Generate Flashcards
1. Open the application in your browser
2. Enter a subject name (optional)
3. Paste your study notes in the text area
4. Choose the number of flashcards (3-10)
5. Click "Generate Flashcards"

### 2. Study with Flashcards
- **Flip Cards**: Click on any flashcard to flip it and see the answer
- **Navigate**: Use Previous/Next buttons to move between cards
- **Shuffle**: Click "Shuffle" to randomize the card order
- **Save Session**: Save your current set of flashcards for later review
- **Export**: Download your flashcards as JSON file

### 3. Example Study Notes
```
Photosynthesis is the process by which plants convert sunlight into energy. 
The process occurs in the chloroplasts and requires carbon dioxide and water. 
The main products are glucose and oxygen. Chlorophyll is the green pigment 
that captures light energy. The Calvin cycle is the second stage of 
photosynthesis where CO2 is fixed into organic compounds.
```

## 🏗️ Project Structure

```
Flashcards/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment variables (create this)
└── templates/
    └── index.html        # Main HTML template
```

## 🔧 Configuration

### Database Configuration
The application automatically creates the required database and tables on first run. Make sure your MySQL server is running and the credentials in `app.py` are correct.

### OpenAI API Configuration
- Get your API key from [OpenAI Platform](https://platform.openai.com/)
- Set it in the `.env` file or directly in `app.py`
- The application uses GPT-3.5-turbo model for flashcard generation

## 🎯 API Endpoints

- `GET /` - Main application page
- `POST /generate` - Generate flashcards from study notes
- `GET /flashcards` - Get all saved flashcards
- `POST /save-session` - Save a study session
- `GET /export/<format>` - Export flashcards (JSON/PDF)

## 🚀 Future Enhancements

- [ ] PDF export functionality
- [ ] Multiple user support with authentication
- [ ] Spaced repetition algorithm
- [ ] Progress tracking and analytics
- [ ] Mobile app version
- [ ] Integration with learning management systems
- [ ] Voice-to-text input for study notes
- [ ] Collaborative flashcard sharing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- Flask community for the excellent web framework
- All contributors and users of this project

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL server is running
   - Check database credentials in `app.py`
   - Verify database user permissions

2. **OpenAI API Error**
   - Verify your API key is correct
   - Check your OpenAI account balance
   - Ensure you have access to GPT-3.5-turbo

3. **Port Already in Use**
   - Change the port in `app.py` (line 261)
   - Or kill the process using the current port

### Getting Help

If you encounter any issues:
1. Check the console output for error messages
2. Verify all prerequisites are installed
3. Ensure all configuration is correct
4. Open an issue on GitHub with detailed error information

---

**Made with ❤️ for better education and learning!**

