import json
from flask import Flask, render_template, flash, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Question, Answer, Result

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "securekey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///biodb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with open('preguntas.json') as f:
    questions_data = json.load(f)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


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
    # Verificar si el usuario está autenticado
    if "username" not in session:
        return redirect(url_for('login'))
    
    # Obtener las preguntas desde la base de datos
    questions = Question.query.all()
    
    return render_template("dashboard.html", user_name=session['username'], questions=questions)


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


        # Calcular puntuaciones en función de las respuestas del usuario
        for response in data['responses']:
            scores[response['biotype']] += response['points']

        # Determinar el biotipo predominante
        predominant_biotype = max(scores, key=scores.get)

        # Obtener el usuario actual
        username = session['username']
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Guardar el resultado en la base de datos
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



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
