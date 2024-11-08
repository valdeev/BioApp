from flask import Flask, render_template, flash, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "securekey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///biodb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
        
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
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
            flash("El usuario ya existe")
            return render_template("register.html")
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("User registered successfully")
            return redirect(url_for('dashboard'))
    
    if session:
        return redirect(url_for('dashboard'))
    else:
        return render_template("register.html")



@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", user_name=session['username'])



@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)