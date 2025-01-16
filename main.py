from flask import Flask, render_template, request, redirect, flash
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages
app.config["MONGO_URI"] = "mongodb+srv://amitesh040977:12345@amiteshjha.6gna1.mongodb.net/userdata"
mongo = PyMongo(app)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def aboutus():
    return render_template('about us.html')

@app.route("/contact")
def contactus():
    return render_template('contact us.html')

@app.route("/courses")
def courses():
    return render_template('courses.html')

@app.route("/register", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect("/login")

        # Insert new user into MongoDB
        mongo.db.users.insert_one({"name": name, "email": email, "password": password})
        flash("Registration successful! Please log in.", "success")
        return redirect("/login")
    return render_template('registration.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate credentials
        user = mongo.db.users.find_one({"email": email})
        if user and user["password"] == password:
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect("/profile")
        else:
            flash("Invalid email or password. Please try again.", "error")

    return render_template('login.html')

@app.route("/forgot")
def forgotPassword():
    return render_template('forgotpassword.html')

@app.route("/profile")
def userprofile():
    return render_template('profile.html')

if __name__ == "__main__":
    app.run(debug=True)
