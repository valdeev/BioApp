import json
from app import app
from models import db, Question, Answer

def load_questions():
    with open('preguntas.json') as f:
        data = json.load(f)

    with app.app_context():
        for q in data['questions']:
            # Verificar si la pregunta ya existe en la base de datos
            existing_question = Question.query.filter_by(text=q['text']).first()
            if not existing_question:
                new_question = Question(text=q['text'])
                db.session.add(new_question)
                db.session.commit()
                
                # Obtener el ID de la nueva pregunta
                question_id = new_question.question_id

                # Agregar respuestas para la pregunta
                for ans in q['answers']:
                    new_answer = Answer(
                        question_id=question_id,
                        text=ans['text'],
                        biotype=ans['biotype'],
                        points=ans['points']
                    )
                    db.session.add(new_answer)
                db.session.commit()

        print("Questions and answers loaded successfully.")

if __name__ == "__main__":
    load_questions()
