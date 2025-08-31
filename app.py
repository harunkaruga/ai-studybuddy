import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai

# Load environment variables from .env
load_dotenv()

# Check if API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_openai_api_key_here":
    print("WARNING: OPENAI_API_KEY not set. Please create a .env file with your OpenAI API key.")
    print("Get your API key from: https://platform.openai.com/api-keys")
    print("Example .env file content:")
    print("OPENAI_API_KEY=sk-your-actual-api-key-here")

openai.api_key = api_key

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    notes = request.json.get("notes", "").strip()
    if not notes:
        return jsonify({"flashcards": []})

    # Check if API key is properly configured
    if not api_key or api_key == "your_openai_api_key_here":
        return jsonify({
            "flashcards": [{
                "question": "API Key Not Configured", 
                "answer": "Please set your OpenAI API key in a .env file. Get your key from https://platform.openai.com/api-keys"
            }]
        })

    try:
        prompt = f"Create 5 concise flashcards (Q&A) from these study notes:\n\n{notes}"

        # Latest OpenAI API call
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        # Get the AI response
        text = response.choices[0].message.content

        # Parse Q&A lines (expects Q: ... A: ...)
        flashcards = []
        for line in text.split("\n"):
            if line.strip().startswith("Q:") and "A:" in line:
                q, a = line.split("A:", 1)
                flashcards.append({"question": q.replace("Q:", "").strip(), "answer": a.strip()})

        return jsonify({"flashcards": flashcards})

    except Exception as e:
        # In case of errors, show it in a flashcard
        return jsonify({"flashcards": [{"question": "Error", "answer": str(e)}]})

if __name__ == "__main__":
    app.run(debug=True)
