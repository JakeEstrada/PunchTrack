import sqlite3
import bcrypt
from calculations import calculate_weekly_totals, calculate_break_duration, calculate_daily_hours, calculate_overtime, calculate_weighted_hours
from flask import Flask, session, render_template, request, g, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = "LunchMeat2020"
app.config["SESSION_COOKIE_NAME"] = "myCOOKIE_monSTER528"
DATABASE = 'PunchCardSystem.db'


# Route for the login 
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

@app.route("/punch-recorder")
def punch_recorder():
    return render_template("punch_in.html")


@app.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.json
    pin = data.get("pin")  # Ensure you are sending the 'pin' key from the frontend

    if not pin:
        return jsonify({"message": "Missing PIN"}), 400

    db = get_db()
    cursor = db.cursor()

    # Check if the PIN exists in the database
    cursor.execute(
        "SELECT * FROM Employee WHERE four_digit_code = ?",
        (pin,)
    )
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Invalid PIN"}), 401

    # Store the employee_id in the session
    session["employee_id"] = user["employee_id"]
    return jsonify({"message": "PIN authenticated successfully"}), 200

@app.route('/store-action', methods=['POST'])
def store_action():
    data = request.json
    action = data.get('action')
    employee_id = session.get('employee_id')

    if not employee_id:
        return {"message": "Unauthorized"}, 403

    # Log punch action with current date and time
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M:%S')

    db = get_db()
    cursor = db.cursor()

    # Calculate the week_starting_day and week_ending_day
    current_date_obj = datetime.strptime(current_date, '%Y-%m-%d')
    week_starting_day = current_date_obj - timedelta(days=current_date_obj.weekday())  # Monday
    week_ending_day = week_starting_day + timedelta(days=6)  # Sunday

    # Check if a WeekLog entry already exists for this week
    cursor.execute("""
        SELECT week_id FROM WeekLog
        WHERE employee_id = ? AND week_starting_day = ? AND week_ending_day = ?
    """, (employee_id, week_starting_day.strftime('%Y-%m-%d'), week_ending_day.strftime('%Y-%m-%d')))
    week_log = cursor.fetchone()

    # If no WeekLog exists, create one with NULL for total_hours, overtime, and weighted_hours
    if not week_log:
        cursor.execute("""
            INSERT INTO WeekLog (employee_id, week_starting_day, week_ending_day)
            VALUES (?, ?, ?)
        """, (employee_id, week_starting_day.strftime('%Y-%m-%d'), week_ending_day.strftime('%Y-%m-%d')))
        db.commit()

        # Retrieve the newly created week_id
        week_log_id = cursor.lastrowid
    else:
        week_log_id = week_log['week_id']

    # Handle punch actions
    if action == 'Punch In':
        cursor.execute("""
            INSERT INTO PunchRecord (employee_id, week_id, record_date, punch_in_time)
            VALUES (?, ?, ?, ?)
        """, (employee_id, week_log_id, current_date, current_time))
    elif action == 'Punch Out':
        cursor.execute("""
            UPDATE PunchRecord
            SET punch_out_time = ?
            WHERE employee_id = ? AND record_date = ? AND week_id = ? AND punch_out_time IS NULL
        """, (current_time, employee_id, current_date, week_log_id))
    elif action == 'Start Break':
        cursor.execute("""
            UPDATE PunchRecord
            SET break_start_time = ?
            WHERE employee_id = ? AND record_date = ? AND week_id = ? AND break_start_time IS NULL
        """, (current_time, employee_id, current_date, week_log_id))
    elif action == 'End Break':
        cursor.execute("""
            UPDATE PunchRecord
            SET break_end_time = ?
            WHERE employee_id = ? AND record_date = ? AND week_id = ? AND break_end_time IS NULL
        """, (current_time, employee_id, current_date, week_log_id))
    else:
        return {"message": "Invalid action"}, 400

    db.commit()
    return {"message": f"{action} recorded successfully"}, 200




@app.route("/admin-dashboard")
def admin_dashboard():
    try:
        db = get_db()  # Initialize database connection
        cursor = db.cursor()

        # Fetch all employees
        cursor.execute("SELECT * FROM Employee")
        employees = cursor.fetchall()

        # Fetch all punch records
        cursor.execute("""
            SELECT * FROM PunchRecord
            ORDER BY record_date DESC
        """)
        punch_records = cursor.fetchall()

        # Fetch all miles records
        cursor.execute("""
            SELECT * FROM MilesLog
            ORDER BY miles_date DESC
        """)
        miles_records = cursor.fetchall()

        # Fetch all change logs (excluding 'description')
        cursor.execute("""
            SELECT change_id, change_date, change_time, employee_id
            FROM ChangeLog
            ORDER BY change_date DESC, change_time DESC
        """)
        change_logs = cursor.fetchall()

        return render_template(
            "admin_page.html",
            employees=employees,
            punch_records=punch_records,
            miles_records=miles_records,
            change_logs=change_logs
        )
    except Exception as e:
        print(f"An error occurred in the admin_dashboard: {e}")
        return render_template("error.html", error_message=str(e)), 500





# Miles Log
@app.route("/miles-log", methods=["GET"])
def miles_log():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    # Fetch all miles logged for the employee, ordered by date (descending)
    cursor.execute(
        """
        SELECT miles_id, week_id, miles_date, miles_driven
        FROM MilesLog
        WHERE employee_id = ?
        ORDER BY miles_date DESC

        """,
        (session["employee_id"],)
    )
    miles_data = cursor.fetchall()

    return render_template("miles_log.html", miles_data=miles_data)

@app.route("/view-logs")
def view_logs():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
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

    return render_template("view_logs.html", week_logs=week_logs)


# Employee log
@app.route("/employee-dashboard", defaults={'week_id': None})
@app.route("/employee-dashboard/<week_id>")
def employee_dashboard(week_id):
    if "employee_id" not in session:
        print("User not logged in. Redirecting to login.")
        return redirect(url_for("login"))

    try:
        db = get_db()  # Initialize database connection
        cursor = db.cursor()

        # Fetch the most recent week_id if not provided
        if not week_id:
            cursor.execute(
                "SELECT MAX(week_id) AS latest_week_id FROM WeekLog WHERE employee_id = ?",
                (session["employee_id"],)
            )
            result = cursor.fetchone()
            week_id = result["latest_week_id"] if result else None

        # Handle cases where no week_id is found
        if not week_id:
            # Calculate the current week's start and end dates
            current_date = datetime.now().date()
            week_starting_day = current_date - timedelta(days=current_date.weekday())  # Monday
            week_ending_day = week_starting_day + timedelta(days=6)  # Sunday

            # Insert a new WeekLog entry if it doesn't exist
            cursor.execute(
                """
                SELECT week_id FROM WeekLog
                WHERE employee_id = ? AND week_starting_day = ? AND week_ending_day = ?
                """,
                (session["employee_id"], week_starting_day, week_ending_day)
            )
            week_log = cursor.fetchone()

            if not week_log:
                cursor.execute(
                    """
                    INSERT INTO WeekLog (employee_id, week_starting_day, week_ending_day)
                    VALUES (?, ?, ?)
                    """,
                    (session["employee_id"], week_starting_day, week_ending_day)
                )
                db.commit()

                # Retrieve the newly created week_id
                week_id = cursor.lastrowid
            else:
                week_id = week_log["week_id"]

        # Fetch the week start and end dates
        cursor.execute(
            "SELECT week_starting_day, week_ending_day FROM WeekLog WHERE week_id = ? AND employee_id = ?",
            (week_id, session["employee_id"])
        )
        week_data = cursor.fetchone()
        if not week_data:
            raise ValueError("Week data not found in the database.")

        week_start_date = datetime.strptime(week_data["week_starting_day"], "%Y-%m-%d")
        week_end_date = datetime.strptime(week_data["week_ending_day"], "%Y-%m-%d")

        # Format week_ending_day as MM/DD/YYYY
        formatted_week_ending_date = week_end_date.strftime("%m/%d/%Y")

        # Generate all days of the week
        all_days = [
            (week_start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((week_end_date - week_start_date).days + 1)
        ]

        # Query existing punch records for the week
        cursor.execute(
            "SELECT record_date FROM PunchRecord WHERE employee_id = ? AND week_id = ?",
            (session["employee_id"], week_id)
        )
        existing_records = {row["record_date"] for row in cursor.fetchall()}

        # Determine available days
        available_days = [day for day in all_days if day not in existing_records]

        # Fetch punch records
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

        # Fetch miles data
        cursor.execute(
            """
            SELECT miles_id, miles_date AS day, miles_driven
            FROM MilesLog
            WHERE employee_id = ? AND week_id = ?
            ORDER BY miles_date
            """,
            (session["employee_id"], week_id)
        )
        miles_records = cursor.fetchall()

        # Enrich punch logs
        enriched_logs = []
        total_hours = total_overtime = total_weighted_hours = 0

        for log in work_logs:
            try:
                # Parse times and calculate durations
                break_duration = calculate_break_duration(log["break_start"], log["break_end"])
                hours = calculate_daily_hours(log["clock_in"], log["clock_out"], break_duration)
                overtime = calculate_overtime(hours)
                weighted_hours = calculate_weighted_hours(hours, overtime)

                total_hours += hours
                total_overtime += overtime
                total_weighted_hours += weighted_hours

                enriched_logs.append({
                    "day": log["day"],
                    "clock_in": log["clock_in"],
                    "clock_out": log["clock_out"],
                    "break_duration": break_duration,
                    "hours": hours,
                    "overtime": overtime,
                    "weighted_hours": weighted_hours,
                })
            except Exception as log_error:
                print(f"Error processing log for {log['day']}: {log_error}")

        # Fetch previous and next week_ids
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

        # Fetch employee details
        cursor.execute(
            "SELECT first_name, last_name, employee_role FROM Employee WHERE employee_id = ?",
            (session.get("employee_id"),)
        )
        employee = cursor.fetchone()

        if not employee:
            print(f"No employee found for ID: {session.get('employee_id')}")
            return redirect(url_for("login"))

        print(f"Employee fetched: {employee}")

        # Render the dashboard
        return render_template(
            "dashboard.html",
            employee=employee,
            work_logs=enriched_logs,
            miles_records=miles_records,
            total_hours=round(total_hours, 2),
            total_overtime=round(total_overtime, 2),
            total_weighted_hours=round(total_weighted_hours, 2),
            previous_week_id=previous_week["week_id"] if previous_week else None,
            next_week_id=next_week["week_id"] if next_week else None,
            available_days=available_days,
            week_ending_date=formatted_week_ending_date  # Pass formatted week ending date
        )
    except Exception as e:
        print(f"An error occurred in the employee_dashboard: {e}")
        return render_template("error.html", error_message=str(e)), 500




@app.route("/add-row", methods=["POST"])
def add_row():
    if "employee_id" not in session:
        return {"message": "Unauthorized"}, 403

    try:
        # Retrieve data from the request
        data = request.json
        record_date = data.get("record_date")
        clock_in = data.get("clock_in")
        clock_out = data.get("clock_out")
        break_start = data.get("break_start")  # Break Start (optional)
        break_end = data.get("break_end")      # Break End (optional)

        # Validate required fields
        if not (record_date and clock_in and clock_out):
            return {"message": "Invalid input: Date, Clock In, and Clock Out are required."}, 400

        # Validate that break_start and break_end are either both provided or both null
        if (break_start and not break_end) or (break_end and not break_start):
            return {"message": "Invalid input: Both Break Start and Break End must be provided or left empty."}, 400

        # Connect to the database
        db = get_db()
        cursor = db.cursor()

        # Determine the week_id for the record_date
        cursor.execute(
            """
            SELECT week_id 
            FROM WeekLog
            WHERE employee_id = ? 
              AND week_starting_day <= ? 
              AND week_ending_day >= ?
            """,
            (session["employee_id"], record_date, record_date)
        )
        week_row = cursor.fetchone()
        if not week_row:
            return {"message": "No matching week found for the selected date."}, 400

        week_id = week_row["week_id"]

        # Insert the new PunchRecord
        cursor.execute(
            """
            INSERT INTO PunchRecord (
                employee_id, week_id, record_date, punch_in_time, punch_out_time, break_start_time, break_end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["employee_id"],
                week_id,
                record_date,
                clock_in,
                clock_out,
                break_start,  # Break Start (can be null)
                break_end     # Break End (can be null)
            )
        )

        db.commit()
        return {"message": "Log added successfully"}, 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"message": "Failed to add log due to a database error."}, 500
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "An unexpected error occurred"}, 500



@app.route("/add-log", methods=["POST"])
def add_log():
    if "employee_id" not in session:
        return {"message": "Unauthorized"}, 403

    try:
        data = request.json
        record_date = data.get("record_date")
        clock_in = data.get("clock_in")
        clock_out = data.get("clock_out")
        break_duration = int(data.get("break_duration"))

        if not (record_date and clock_in and clock_out and break_duration >= 0):
            return {"message": "Invalid input"}, 400

        db = get_db()
        cursor = db.cursor()

        # Determine week_id for the record_date
        cursor.execute(
            """
            SELECT week_id 
            FROM WeekLog
            WHERE employee_id = ? 
              AND week_starting_day <= ? 
              AND week_ending_day >= ?
            """,
            (session["employee_id"], record_date, record_date)
        )
        week_row = cursor.fetchone()
        if not week_row:
            return {"message": "No matching week found for the selected date."}, 400

        week_id = week_row["week_id"]

        # Insert the new PunchRecord
        cursor.execute(
            """
            INSERT INTO PunchRecord (
                employee_id, week_id, record_date, punch_in_time, punch_out_time, break_start_time, break_end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["employee_id"],
                week_id,
                record_date,
                clock_in,
                clock_out,
                None,  # Optional: Adjust break times if required
                None,  # Optional: Adjust break times if required
            )
        )

        db.commit()
        return {"message": "Log added successfully"}, 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"message": "Failed to add log"}, 500
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "An unexpected error occurred"}, 500




@app.route("/delete-log/<day>", methods=["DELETE"])
def delete_log(day):
    if "employee_id" not in session:
        return {"message": "Unauthorized"}, 403

    db = get_db()
    cursor = db.cursor()

    try:
        # Delete the record
        cursor.execute(
            "DELETE FROM PunchRecord WHERE employee_id = ? AND record_date = ?",
            (session["employee_id"], day)
        )
        db.commit()

    
        # Recalculate totals for the current week if needed
        week_id = request.args.get("week_id")
        if week_id:
            recalculate_week_totals(session["employee_id"], week_id)

        # Redirect to the employee dashboard after deletion
        return redirect(url_for("employee_dashboard", week_id=week_id))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"message": "Failed to delete record or recalculate totals."}, 500


@app.route("/get-week-totals", methods=["GET"])
def get_week_totals():
    if "employee_id" not in session:
        return {"message": "Unauthorized"}, 403

    db = get_db()
    cursor = db.cursor()

    # Fetch totals for the current week
    week_id = request.args.get('week_id', None)
    if week_id:
        cursor.execute(
            """
            SELECT total_hours, overtime, weighted_hours
            FROM WeekLog
            WHERE employee_id = ? AND week_id = ?
            """,
            (session["employee_id"], week_id)
        )
        totals = cursor.fetchone()
        if totals:
            return {
                "total_hours": totals["total_hours"],
                "total_overtime": totals["overtime"],
                "total_weighted_hours": totals["weighted_hours"]
            }

    return {"message": "Totals not found"}, 404




@app.route("/add-miles", methods=["POST"])
def add_miles():
    if "employee_id" not in session:
        return {"message": "Unauthorized"}, 403

    try:
        # Get data from form submission
        miles_date = request.form.get("miles_date")
        miles_driven = request.form.get("miles_driven")

        if not miles_date or not miles_driven:
            return {"message": "All fields are required"}, 400

        miles_driven = float(miles_driven)
        if miles_driven < 0:
            return {"message": "Miles driven must be non-negative"}, 400

        db = get_db()
        cursor = db.cursor()

        # Check if a record already exists for the date
        cursor.execute(
            """
            SELECT miles_id FROM MilesLog
            WHERE employee_id = ? AND miles_date = ?
            """,
            (session["employee_id"], miles_date)
        )
        record = cursor.fetchone()

        if record:
            # Update existing record
            cursor.execute(
                """
                UPDATE MilesLog
                SET miles_driven = ?
                WHERE miles_id = ?
                """,
                (miles_driven, record["miles_id"])
            )
        else:
            # Insert new record
            cursor.execute(
                """
                INSERT INTO MilesLog (employee_id, miles_date, miles_driven)
                VALUES (?, ?, ?)
                """,
                (session["employee_id"], miles_date, miles_driven)
            )

        db.commit()
        return redirect(url_for("miles_log"))  # Redirect to miles log on success

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"message": "Failed to add/update miles due to database error"}, 500
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "An unexpected error occurred"}, 500



@app.route("/delete-miles/<miles_id>", methods=["POST"])
def delete_miles(miles_id):
    if "employee_id" not in session:
        return {"message": "Unauthorized"}, 403

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if the miles record exists and belongs to the logged-in employee
        cursor.execute(
            "SELECT * FROM MilesLog WHERE miles_id = ? AND employee_id = ?",
            (miles_id, session["employee_id"])
        )
        record = cursor.fetchone()
        if not record:
            return {"message": "Record not found or unauthorized"}, 404

        # Delete the record
        cursor.execute(
            "DELETE FROM MilesLog WHERE miles_id = ? AND employee_id = ?",
            (miles_id, session["employee_id"])
        )
        db.commit()

        return redirect(url_for("miles_log"))  # Redirect to miles log

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"message": "Failed to delete record or recalculate totals."}, 500





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

@app.route("/logout")
def logout():
    # Clear the session to log the user out
    session.clear()
    return redirect(url_for("login"))  # Redirect to the login page


# Database Helpers
def get_db():
    db = sqlite3.connect("PunchCardSystem.db")
    db.row_factory = sqlite3.Row
    return db



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()



if __name__ == "__main__":
    app.run(debug=True)
