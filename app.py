import sqlite3
import bcrypt
from calculations import calculate_weekly_totals, calculate_break_duration, calculate_daily_hours, calculate_overtime, calculate_weighted_hours
from flask import Flask, session, render_template, request, g, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "LunchMeat2020"
app.config["SESSION_COOKIE_NAME"] = "myCOOKIE_monSTER528"
DATABASE = 'PunchCardSystem.db'


# Route for the login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = validate_user(username, password)
        if user:
            session["employee_id"] = user["employee_id"]
            session["username"] = user["username"]
            return redirect(url_for("employee_dashboard"))
        else:
            flash("Invalid username or password!", "error")
    return render_template("login.html")


# Employee Dashboard
@app.route("/employee-dashboard", defaults={'week_id': None})
@app.route("/employee-dashboard/<week_id>")
def employee_dashboard(week_id):
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    # If no week_id is provided, fetch the most recent week_id
    if not week_id:
        cursor.execute(
            "SELECT MAX(week_id) AS latest_week_id FROM WeekLog WHERE employee_id = ?",
            (session["employee_id"],)
        )
        result = cursor.fetchone()
        week_id = result["latest_week_id"] if result else None

    # Query for current week's punch records
    cursor.execute(
        """
        SELECT record_date AS day, punch_in_time AS clock_in, punch_out_time AS clock_out,
               break_start_time AS break_start, break_end_time AS break_end
        FROM PunchRecord
        WHERE employee_id = ? AND week_id = ?
        """,
        (session["employee_id"], week_id)
    )
    work_logs = cursor.fetchall()

    # Query for miles driven in the current week
    cursor.execute(
        """
        SELECT miles_date AS day, SUM(miles_driven) AS total_miles
        FROM MilesLog
        WHERE employee_id = ? AND week_id = ?
        GROUP BY miles_date
        """,
        (session["employee_id"], week_id)
    )
    miles_data = cursor.fetchall()

    # Map miles driven data to corresponding days
    miles_by_day = {entry["day"]: entry["total_miles"] for entry in miles_data}

    # Enrich logs with calculations and miles
    enriched_logs = []
    total_miles = total_hours = total_overtime = total_weighted_hours = 0

    for log in work_logs:
        break_duration = calculate_break_duration(log["break_start"], log["break_end"])
        hours = calculate_daily_hours(log["clock_in"], log["clock_out"], break_duration)
        overtime = calculate_overtime(hours)
        weighted_hours = calculate_weighted_hours(hours, overtime)

        miles = miles_by_day.get(log["day"], 0)  # Get miles for the day, default to 0

        total_miles += miles
        total_hours += hours
        total_overtime += overtime
        total_weighted_hours += weighted_hours

        enriched_logs.append({
            "day": log["day"],
            "clock_in": log["clock_in"],
            "clock_out": log["clock_out"],
            "break_duration": break_duration,
            "hours": hours,
            "miles_driven": miles,
            "overtime": overtime,
            "weighted_hours": weighted_hours,
        })

    # Query for previous and next week_ids
    cursor.execute(
        "SELECT week_id FROM WeekLog WHERE employee_id = ? AND week_id < ? ORDER BY week_id DESC LIMIT 1",
        (session["employee_id"], week_id)
    )
    previous_week = cursor.fetchone()

    cursor.execute(
        "SELECT week_id FROM WeekLog WHERE employee_id = ? AND week_id > ? ORDER BY week_id ASC LIMIT 1",
        (session["employee_id"], week_id)
    )
    next_week = cursor.fetchone()

    # Query for employee details
    cursor.execute(
        "SELECT first_name, last_name, employee_role FROM Employee WHERE employee_id = ?",
        (session["employee_id"],)
    )
    employee = cursor.fetchone()

    return render_template(
        "dashboard.html",
        employee=employee,
        work_logs=enriched_logs,
        total_miles=total_miles,
        total_hours=round(total_hours, 2),
        total_overtime=round(total_overtime, 2),
        total_weighted_hours=round(total_weighted_hours, 2),
        previous_week_id=previous_week["week_id"] if previous_week else None,
        next_week_id=next_week["week_id"] if next_week else None,
    )


# Week Logs View
@app.route("/view-logs")
def view_logs():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    # Fetch the WeekLog data for the logged-in employee
    cursor.execute(
        """
        SELECT week_id, week_ending_day, total_hours, overtime, weighted_hours
        FROM WeekLog
        WHERE employee_id = ?
        ORDER BY week_ending_day DESC
        """,
        (session["employee_id"],)
    )
    week_logs = cursor.fetchall()

    # Debugging logs
    print(f"Employee ID: {session['employee_id']}")
    print(f"Week Logs: {week_logs}")

    # Pass the logs to the template
    return render_template("view_logs.html", week_logs=week_logs)

@app.route("/miles-log", methods=["GET"])
def miles_log():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    # Fetch all miles logged for the employee, ordered by date (descending)
    cursor.execute(
        """
        SELECT miles_date, miles_driven
        FROM MilesLog
        WHERE employee_id = ?
        ORDER BY miles_date DESC
        """,
        (session["employee_id"],)
    )
    miles_data = cursor.fetchall()

    return render_template("miles_log.html", miles_data=miles_data)


@app.route("/add-miles", methods=["POST"])
def add_miles():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    miles_date = request.form.get("miles_date")
    miles_driven = float(request.form.get("miles_driven"))

    # Check if miles exist for the selected date
    cursor.execute(
        """
        SELECT miles_id FROM MilesLog
        WHERE employee_id = ? AND miles_date = ?
        """,
        (session["employee_id"], miles_date)
    )
    record = cursor.fetchone()

    if record:
        # Update existing miles
        cursor.execute(
            """
            UPDATE MilesLog
            SET miles_driven = miles_driven + ?
            WHERE miles_id = ?
            """,
            (miles_driven, record["miles_id"])
        )
    else:
        # Add new miles entry
        cursor.execute(
            """
            INSERT INTO MilesLog (miles_id, employee_id, miles_date, miles_driven)
            VALUES (?, ?, ?, ?)
            """,
            (f"{session['employee_id']}-{miles_date}", session["employee_id"], miles_date, miles_driven)
        )

    db.commit()
    return redirect(url_for("miles_log"))



@app.route("/delete-miles/<miles_id>", methods=["POST"])
def delete_miles(miles_id):
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM MilesLog WHERE miles_id = ? AND employee_id = ?",
        (miles_id, session["employee_id"])
    )
    db.commit()
    return redirect(url_for("miles_log"))




# Validate User
def validate_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT employee_id, username, password_hash FROM Employee WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return {"employee_id": user["employee_id"], "username": user["username"]}
    return None


# Database Helpers
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
