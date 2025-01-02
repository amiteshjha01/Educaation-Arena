from flask import Flask, render_template,request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://amitesh040977:12345@amiteshjha.6gna1.mongodb.net/"
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

@app.route("/register",methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        passwords = request.form.get('password')

        return render_template('login.html')
        # return f"Registration successful for {name} with email {email}!"
    return render_template('registration.html')

@app.route("/forgot")
def forgotPassword():
    return render_template('forgotpassword.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/profile")
def userprofile():
    return render_template('profile.html')



app.run(debug = True)