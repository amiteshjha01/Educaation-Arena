from flask import Flask, render_template, request, redirect, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages
app.config["MONGO_URI"] = "mongodb+srv://amitesh040977:12345@amiteshjha.6gna1.mongodb.net/userdata"
mongo = PyMongo(app)

# Home Route
@app.route("/")
def home():
    return render_template("home.html")


# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if user already exists
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect("/login")

        # Insert user into MongoDB
        mongo.db.users.insert_one({"name": name, "email": email, "password": password})
        flash("Registration successful! Please log in.", "success")
        return redirect("/login")

    return render_template("registration.html")


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Authenticate user
        user = mongo.db.users.find_one({"email": email, "password": password})
        if user:
            session["user_id"] = str(user["_id"])  # Save user ID in session
            flash("Login successful!", "success")
            return redirect("/profile")

        flash("Invalid email or password.", "error")
        return redirect("/login")

    return render_template("login.html")


# User Profile Route
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in to access your profile.", "error")
        return redirect("/login")

    # Fetch user details from MongoDB
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})

    if request.method == "POST":
        # Update profile information
        dob = request.form.get("dob")
        contact = request.form.get("contact")
        address = request.form.get("address")
        college = request.form.get("college")
        course = request.form.get("course")

        mongo.db.users.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": {
                "dob": dob,
                "contact": contact,
                "address": address,
                "college": college,
                "course": course
            }}
        )
        flash("Profile updated successfully!", "success")
        return redirect("/profile")

    # Fetch user's enrolled courses
    enrolled_courses = mongo.db.enrollments.find({"user_id": session["user_id"]})
    enrolled_course_names = [course["course_name"] for course in enrolled_courses]

    # Fetch all available courses
    all_courses = list(mongo.db.courses.find())

    return render_template("profile.html", user=user, enrolled_courses=enrolled_course_names, all_courses=all_courses)


# Enroll Route
@app.route("/enroll/<course_id>", methods=["POST"])
def enroll(course_id):
    if "user_id" not in session:
        flash("Please log in to enroll in courses.", "error")
        return redirect("/login")

    # Check if already enrolled
    existing_enrollment = mongo.db.enrollments.find_one({"user_id": session["user_id"], "course_id": course_id})
    if existing_enrollment:
        flash("You are already enrolled in this course.", "info")
    else:
        # Enroll user in course
        course = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
        mongo.db.enrollments.insert_one({
            "user_id": session["user_id"],
            "course_id": course_id,
            "course_name": course["name"]
        })
        flash(f"Enrolled in {course['name']} successfully!", "success")

    return redirect("/profile")


# Forgot Password Route
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = request.form["new_password"]

        # Update password in MongoDB
        user = mongo.db.users.find_one({"email": email})
        if user:
            mongo.db.users.update_one({"email": email}, {"$set": {"password": new_password}})
            flash("Password updated successfully! Please log in.", "success")
            return redirect("/login")

        flash("Email not found. Please register.", "error")
        return redirect("/register")

    return render_template("forgot_password.html")


# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/")


# Courses Route
@app.route("/courses")
def courses():
    courses = list(mongo.db.courses.find())
    return render_template('courses.html', courses=courses)


# About Us Route
@app.route("/about")
def aboutus():
    return render_template('about us.html')


# Contact Us Route
@app.route("/contact")
def contactus():
    return render_template('contact us.html')


# Send Message Route
@app.route("/send_message", methods=["POST"])
def send_message():
    # Get form data
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message = request.form.get("message")

    # Store the message in MongoDB
    mongo.db.messages.insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "message": message
    })

    # Flash success message
    flash("Your message has been sent successfully. We will get back to you soon!", "success")
    return redirect("/contact")


if __name__ == "__main__":
    app.run(debug=True)
