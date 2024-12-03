import json
import os
from flask import Flask, render_template, flash, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, User, Question, Answer, Result, UserStateHistory

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "securekey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///biodb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREGUNTAS_FILE = os.path.join(BASE_DIR, 'preguntas.json')
PHRASES_FILE = os.path.join(BASE_DIR, 'frases.json')

with open(PREGUNTAS_FILE) as f:
    questions_data = json.load(f)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/create_tables')
def create_tables():
    with app.app_context():
        db.create_all()
    return "Tablas creadas correctamente."

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    flash("That account doesn't exist")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Complete all fields")
            return render_template("register.html")

        if password != confirmation:
            flash("Passwords do not match")
            return render_template("register.html")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("User already exists")
            return render_template("register.html")

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        flash("User registered successfully")
        return redirect(url_for('dashboard'))

    if session:
        return redirect(url_for('dashboard'))
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for('login'))

    # Obtener el usuario basado en el username
    biotipoId = User.query.filter_by(username=session["username"]).first()

    # Si el usuario no existe en la base de datos, redirige al login
    if biotipoId is None:
        return redirect(url_for('login'))

    # Consultar biotipo y estado
    biotipo = Result.query.filter_by(user_id=biotipoId.id).first()
    estado = UserStateHistory.query.filter_by(user_id=biotipoId.id).first()

    # Lógica de renderizado según la existencia de biotipo y estado
    if biotipo is None and estado is None:
        return render_template("dashboard.html", user_name=session["username"], biotipo="...", estado="...")
    elif biotipo is None:
        return render_template("dashboard.html", user_name=session["username"], biotipo="...", estado=estado.estado)
    elif estado is None:
        return render_template("dashboard.html", user_name=session["username"], biotipo=biotipo.biotype, estado="...")
    else:
        return render_template("dashboard.html", user_name=session["username"], biotipo=biotipo.biotype, estado=estado.estado)



@app.route('/questions')
def questions():
    if "username" in session:
        try:
            with open(PREGUNTAS_FILE) as f:
                questions_data = json.load(f)
            return jsonify(questions_data)
        except FileNotFoundError:
            return jsonify({"error": "Archivo no encontrado"}), 500


@app.route("/biotypes")
def biotypes():
    if "username" in session:
        questions = Question.query.all()
        return render_template("biotypes.html", questions=questions)



@app.route('/submit', methods=['POST'])
def submit_answers():
    if "username" not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        data = request.json
        scores = {
            "Mediador": 0,
            "Prudente": 0,
            "Ejecutivo": 0,
            "Cautivador": 0,
            "Trascendental": 0,
            "Creativo": 0,
            "Investigador": 0,
            "Audaz": 0,
            "Protector": 0,
            "Visionario": 0
        }

        for response in data['responses']:
            scores[response['biotype']] += response['points']

        predominant_biotype = max(scores, key=scores.get)
        username = session['username']
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        result = Result(user_id=user.id, biotype=predominant_biotype, total_score=scores[predominant_biotype])
        db.session.add(result)
        db.session.commit()

        return jsonify({
            "biotype": predominant_biotype,
            "scores": scores
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/phrases')
def phrases():
    try:
        with open(PHRASES_FILE) as f:
            phrases_data = json.load(f)
        return jsonify(phrases_data)
    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 500


@app.route("/analysis")
def analysis():
    if "username" not in session:
        return redirect(url_for('login'))
    return render_template("analysis.html")


@app.route('/save_results', methods=['POST'])
def save_results():
    try:
        data = request.json
        left_score = data.get('left')
        right_score = data.get('right')
        id_user = User.query.filter_by(username=session["username"]).first()
        user_id = id_user.id

        if user_id is None or left_score is None or right_score is None:
            return jsonify({'error': 'Faltan datos'}), 400

        # Determinar el estado
        if left_score > right_score:
            estado = 'Extrovertido'
        elif right_score > left_score:
            estado = 'Introvertido'
        else:
            estado = 'Neutral'

        new_state = UserStateHistory(user_id=user_id, estado=estado)
        db.session.add(new_state)
        db.session.commit()

        return jsonify({'message': 'Resultados guardados correctamente', 'estado': estado}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)