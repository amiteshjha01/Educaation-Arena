from flask import Flask, render_template

app = Flask(__name__)

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

@app.route("/register")
def registration():
    return render_template('registration.html')

@app.route("/forgot")
def forgotPassword():
    return render_template('forgotpassword.html')

@app.route("/login")
def login():
    return render_template('login.html')





app.run(debug = True)