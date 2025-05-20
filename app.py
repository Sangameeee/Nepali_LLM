from flask import Flask, request, render_template
from google import genai
import markdown
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') 
db = SQLAlchemy(app)


class CacheAnswer(db.Model):
    question = db.Column(db.String, primary_key = True) #unique questions
    answer = db.Column(db.String)

with app.app_context():
    db.create_all()

def gemini_call(question):
    client = genai.Client(api_key=f"{os.getenv('GEMINI_API')}")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[question]
    )
    answer = markdown.markdown(response.text)
    return answer


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form.get('question')
        cached = CacheAnswer.query.get(question)
        if cached:
            answer = cached.answer
            print('took cached value')
            return f"<p>{answer}</p>"
        else:
            answer = gemini_call(question)
            new_entry = CacheAnswer(question = question, answer = answer)
            db.session.add(new_entry)
            db.session.commit()
            print("saved to cached and showed it")
            return f"<p>{answer}</p>"
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)