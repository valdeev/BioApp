from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Modelo de usuario (conserva el original)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Modelo para preguntas
class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    answers = db.relationship('Answer', backref='question', lazy=True)


class Answer(db.Model):
    __tablename__ = 'answers'
    answer_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    biotype = db.Column(db.String(50))
    points = db.Column(db.Integer)



# Modelo para almacenar los resultados de los usuarios
class Result(db.Model):
    __tablename__ = 'results'
    result_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    biotype = db.Column(db.String(50))
    total_score = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
