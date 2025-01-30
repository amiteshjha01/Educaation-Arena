from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # In production, use a strong secret key
app.config["MONGO_URI"] = "mongodb+srv://amitesh040977:12345@amiteshjha.6gna1.mongodb.net/userdata"
mongo = PyMongo(app)


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            # Store the requested URL in session
            session['next_url'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for('profile'))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "student")  # Default role is student

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect(url_for('login'))

        user_data = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.utcnow()
        }
        mongo.db.users.insert_one(user_data)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for('profile'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Both email and password are required.", "error")
            return redirect(url_for('login'))

        user = mongo.db.users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["role"] = user.get("role", "student")
            flash("Login successful!", "success")

            # Redirect to the stored next_url if it exists
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('profile'))

        flash("Invalid email or password.", "error")
        return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})
    if not user:
        session.clear()
        flash("User not found.", "error")
        return redirect(url_for('login'))

    if request.method == "POST":
        update_data = {
            "dob": request.form.get("dob"),
            "contact": request.form.get("contact"),
            "address": request.form.get("address"),
            "college": request.form.get("college"),
            "course": request.form.get("course"),
            "updated_at": datetime.utcnow()
        }

        mongo.db.users.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": update_data}
        )
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    # Get enrolled courses with more details
    enrolled_courses = list(mongo.db.enrollments.aggregate([
        {"$match": {"user_id": session["user_id"]}},
        {"$lookup": {
            "from": "courses",
            "localField": "course_id",
            "foreignField": "_id",
            "as": "course_details"
        }},
        {"$unwind": "$course_details"}
    ]))

    # Get available courses (not enrolled)
    enrolled_course_ids = [ObjectId(course["course_id"]) for course in enrolled_courses]
    available_courses = list(mongo.db.courses.find(
        {"_id": {"$nin": enrolled_course_ids}}
    ))

    return render_template(
        "profile.html",
        user=user,
        enrolled_courses=enrolled_courses,
        available_courses=available_courses
    )


@app.route("/enroll/<course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    try:
        course_id_obj = ObjectId(course_id)
    except:
        flash("Invalid course ID.", "error")
        return redirect(url_for('profile'))

    existing_enrollment = mongo.db.enrollments.find_one({
        "user_id": session["user_id"],
        "course_id": str(course_id_obj)
    })

    if existing_enrollment:
        flash("You are already enrolled in this course.", "info")
        return redirect(url_for('profile'))

    course = mongo.db.courses.find_one({"_id": course_id_obj})
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('profile'))

    enrollment_data = {
        "user_id": session["user_id"],
        "course_id": str(course_id_obj),
        "course_name": course["name"],
        "progress": 0,
        "quiz_completed": False,
        "enrolled_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow()
    }

    mongo.db.enrollments.insert_one(enrollment_data)
    flash(f"Successfully enrolled in {course['name']}!", "success")
    return redirect(url_for('learn', course_id=course_id))


@app.route("/learn/<course_id>")
@login_required
def learn(course_id):
    try:
        course_id_obj = ObjectId(course_id)
    except:
        flash("Invalid course ID.", "error")
        return redirect(url_for('profile'))

    enrollment = mongo.db.enrollments.find_one({
        "user_id": session["user_id"],
        "course_id": str(course_id_obj)
    })

    if not enrollment:
        flash("Please enroll in the course first.", "error")
        return redirect(url_for('profile'))

    course = mongo.db.courses.find_one({"_id": course_id_obj})
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('profile'))

    # Update last accessed timestamp
    mongo.db.enrollments.update_one(
        {"_id": enrollment["_id"]},
        {"$set": {"last_accessed": datetime.utcnow()}}
    )

    return render_template(
        "learn.html",
        course=course,
        enrollment=enrollment
    )


@app.route("/quiz/<course_id>", methods=["GET", "POST"])
@login_required
def quiz(course_id):
    enrollment = mongo.db.enrollments.find_one({
        "user_id": session["user_id"],
        "course_id": course_id
    })

    if not enrollment:
        flash("Please enroll in the course first.", "error")
        return redirect(url_for('profile'))

    course = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('profile'))

    if request.method == "POST":
        score = 0
        answers = request.form
        quiz_data = course.get("quiz", {})

        for question, answer in answers.items():
            if question.startswith('q_') and quiz_data.get(question) == answer:
                score += 1

        passing_score = len(quiz_data) * 0.7  # 70% passing score
        if score >= passing_score:
            mongo.db.enrollments.update_one(
                {"_id": enrollment["_id"]},
                {
                    "$set": {
                        "quiz_completed": True,
                        "quiz_score": score,
                        "quiz_completed_at": datetime.utcnow()
                    }
                }
            )
            flash(f"Congratulations! You passed the quiz with a score of {score}!", "success")
            return redirect(url_for('learn', course_id=course_id))
        else:
            flash(f"Quiz failed. You scored {score}. Need {passing_score} to pass.", "error")

    return render_template("quiz.html", course=course)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('home'))


# Role-specific routes
@app.route("/instructor/dashboard")
@login_required
def instructor_dashboard():
    if session.get("role") != "instructor":
        flash("Access denied. Instructor privileges required.", "error")
        return redirect(url_for('profile'))

    # Get instructor's courses and related statistics
    courses = list(mongo.db.courses.find({"instructor_id": ObjectId(session["user_id"])}))
    return render_template("instructor_dashboard.html", courses=courses)


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('profile'))

    # Get admin statistics
    stats = {
        "total_users": mongo.db.users.count_documents({}),
        "total_courses": mongo.db.courses.count_documents({}),
        "total_enrollments": mongo.db.enrollments.count_documents({})
    }
    return render_template("admin_dashboard.html", stats=stats)


@app.route("/quiz")
def quizprogress():
    return render_template('quiz.html')


@app.route("/about")
def aboutus():
    return render_template('about us.html')

@app.route("/contact")
def contactus():
    return render_template('contact us.html')

@app.route("/courses")
def courses():
    return render_template('courses.html')
@app.route("/forgot")
def forgotpassword():
    return render_template('forgotpassword.html')


@app.route("/instructor")
def instructor():
    return render_template('instructor.html')

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route("/discussion")
def discussion():
    return render_template('discussion.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)