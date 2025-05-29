from flask import Flask, request, render_template, jsonify
from google import genai
import markdown
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.getenv('KEY')  # Still needed for Flask internals
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

class CacheAnswer(db.Model):
    question = db.Column(db.String, primary_key=True)  # Unique questions
    answer = db.Column(db.String)

with app.app_context():
    db.create_all()

def gemini_call(question):
    client = genai.Client(api_key=os.getenv('GEMINI_API'))
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[question]
    )
    answer = markdown.markdown(response.text)
    return answer

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json['question']
    cached = CacheAnswer.query.get(question)
    if cached:
        answer = cached.answer
    else:
        answer = gemini_call(question)
        new_entry = CacheAnswer(question=question, answer=answer)
        db.session.add(new_entry)
        db.session.commit()
    return jsonify({'answer': answer})

if __name__ == "__main__":
    app.run(debug=True)