import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect("PunchCardSystem.db")
cursor = connection.cursor()

cursor.execute("PRAGMA foreign_keys = OFF;")

# Drop tables if they exist (SQLite doesn't support IF EXISTS in DROP statements)
tables = ["ChangeLog", "MilesLog", "WeekLog", "AbsenceRecord", "PunchRecord", "Employee"]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

# Re-enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

# Create the Employee table
cursor.execute("""
CREATE TABLE Employee (
    employee_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    four_digit_code TEXT UNIQUE,
    employee_role TEXT NOT NULL
)
""")


# Create the PunchRecord table
cursor.execute("""
CREATE TABLE PunchRecord (
    punch_id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    week_id INTEGER,
    record_date DATE NOT NULL,
    punch_in_time TIME,
    punch_out_time TIME,
    break_start_time TIME,
    break_end_time TIME,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (week_id) REFERENCES WeekLog(week_id)
)
""")


# Create the AbsenceRecord table
cursor.execute("""
CREATE TABLE AbsenceRecord (
    absence_id INTEGER PRIMARY KEY ,
    employee_id INTEGER NOT NULL,
    absence_type TEXT NOT NULL,
    absence_date DATE NOT NULL,
    notes TEXT,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
)
""")

# Create the MilesLog table
cursor.execute("""
CREATE TABLE MilesLog (
    miles_id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    week_id INTEGER,
    miles_date DATE NOT NULL,
    miles_driven REAL NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (week_id) REFERENCES WeekLog(week_id)
)
""")


# Create the WeekLog table
cursor.execute("""
CREATE TABLE WeekLog (
    week_id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    week_starting_day DATE NOT NULL,
    week_ending_day DATE NOT NULL,
    total_hours REAL,
    overtime REAL,
    weighted_hours REAL,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
)
""")

# Create the ChangeLog table
cursor.execute("""
CREATE TABLE ChangeLog (
    change_id INTEGER PRIMARY KEY ,
    employee_id INTEGER NOT NULL,
    change_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_date DATE NOT NULL,
    change_time TIME NOT NULL,
    changed_by TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
)
""")


employee_data = [
    (100, 'Rogers', 'Woodshop', 'Admin', '$2b$12$VWgjs1r5.RKLIsu4STuayutfqTsZH1Tz2LBX/HxW/CCq00cLaOHzm', '0001', 'Admin'),
    (101, 'Felix', 'Bonilla', 'fbonilla76', '$2b$12$wmUljZJ4Xv0UwqSPHafF9uadgDDsSyxhSBJdYgZZi0O0v8QS3fQpG', '1234', 'Shop Worker'),
    (102, 'Walter', 'Ramos', 'wramos2007', '$2b$12$s2C7NDgEeNXuokfnI4ZkmuqsIW7kSPSS/9ZG9YsxOwL/8L772l95i', '5678', 'Installer'),
    (103, 'Eder', 'Uribe', 'euribe2023', '$2b$12$V6a3/j8YDCqmCnIZj.9nG.qVQI.KJgyCD3FtBbD.2LciDgg13FHUa', '9101', 'Shop Manager'),
    (104, 'Scott', 'Shannon', 'sshannon1030', '$2b$12$IqX.Y5fVHHDwxZlVMb.KBuw7S8mIR.WZR/7lMfu.1UwEwRtZZ05pa', '1121', 'Sales Lead'),
    (105, 'Olivia', 'Carter', 'ocarter92', '$2b$12$ik9KM17N6jpoqoHUQNA2T./rmA8Gmxg3uqzd3jMexqmsH.F0U.7FS', '3141', 'PT Office Administrator')
]
# Insert Employee data first
cursor.executemany("""
    INSERT INTO Employee (employee_id, first_name, last_name, username, password_hash, four_digit_code, employee_role)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", employee_data)



# Insert data into WeekLog table
week_log_data = [
    # Data for Employee 101
    (20, 101, '2024-11-04', '2024-11-10', 37.21, 2.21, 38.32),
    (19, 101, '2024-10-28', '2024-11-03', 33.87, 1.87, 34.81),
    (18, 101, '2024-10-21', '2024-10-27', 42.21, 2.39, 43.41),
    (17, 101, '2024-10-14', '2024-10-20', 25, 0, 25.5),

    # Data for Employee 102
    (16, 102, '2024-11-04', '2024-11-10', 40, 0, 40),
    (15, 102, '2024-10-28', '2024-11-03', 24, 0, 24),
    (14, 102, '2024-10-21', '2024-10-27', 40, 0, 40),
    (13, 102, '2024-10-14', '2024-10-20', 40, 0, 40),

    # Data for Employee 103
    (12, 103, '2024-11-04', '2024-11-10', 42.5, 2.5, 43.75),
    (11, 103, '2024-10-28', '2024-11-03', 34, 0, 35),
    (10, 103, '2024-10-21', '2024-10-27', 41.5, 0, 42.5),
    (9, 103, '2024-10-14', '2024-10-20', 42.5, 2.5, 43.75),

    # Data for Employee 104
    (8, 104, '2024-11-04', '2024-11-10', 41.25, 1.25, 41.88),
    (7, 104, '2024-10-28', '2024-11-03', 43.5, 3.5, 45.25),
    (6, 104, '2024-10-21', '2024-10-27', 0, 0, 0),
    (5, 104, '2024-10-14', '2024-10-20', 42.5, 2.5, 43.75),

    # Data for Employee 105
    (4, 105, '2024-11-04', '2024-11-10', 24, 0, 24),
    (3, 105, '2024-10-28', '2024-11-03', 30, 0, 30),
    (2, 105, '2024-10-21','2024-10-27', 24, 0, 24),
    (1, 105, '2024-10-14', '2024-10-20', 24, 0, 24)
]

# Insert WeekLog data second
cursor.executemany("""
    INSERT INTO WeekLog (week_id, employee_id,week_starting_day, week_ending_day, total_hours, overtime, weighted_hours)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", week_log_data)


# Insert data into PunchRecord table
punch_record_data = [

    # Data for Employee 101
    (89, 101, 20, '2024-11-08', '09:00:00', '12:00:00', None, None),
    (88, 101, 20, '2024-11-07', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (87, 101, 20, '2024-11-06', '06:31:00', '15:30:00', '11:30:00', '12:00:00'),
    (86, 101, 20, '2024-11-05', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (85, 101, 20, '2024-11-04', '06:47:00', '15:30:00', '11:30:00', '12:00:00'),
    (84, 101, 19, '2024-11-01', '06:35:00', '15:30:00', '11:30:00', '12:00:00'),
    (83, 101, 19, '2024-10-31', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (82, 101, 19, '2024-10-30', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (81, 101, 19, '2024-10-29', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (80, 101, 18, '2024-10-25', '07:11:00', '15:30:00', '11:30:00', '12:00:00'),
    (79, 101, 18, '2024-10-24', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (78, 101, 18, '2024-10-23', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (77, 101, 18, '2024-10-22', '06:37:00', '15:30:00', '11:30:00', '12:00:00'),
    (76, 101, 18, '2024-10-21', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (75, 101, 17, '2024-10-16', '06:51:00', '15:30:00', '11:30:00', '12:00:00'),
    (74, 101, 17, '2024-10-15', '06:39:00', '15:30:00', '11:30:00', '12:00:00'),
    (73, 101, 17, '2024-10-14', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),

    # Data for Employee 102
    (72, 102, 16, '2024-11-08', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (71, 102, 16, '2024-11-07', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (70, 102, 16, '2024-11-06', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (69, 102, 16, '2024-11-05', '08:00:00', '16:30:00', '11:30:00', '12:00:00'),
    (68, 102, 16, '2024-11-04', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (67, 102, 15, '2024-10-30', '08:00:00', '16:30:00', '11:30:00', '12:00:00'),
    (66, 102, 15, '2024-10-29', '08:30:00', '17:00:00', '11:30:00', '12:00:00'),
    (65, 102, 15, '2024-10-28', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (64, 102, 14, '2024-10-25', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (63, 102, 14, '2024-10-24', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (62, 102, 14, '2024-10-23', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (61, 102, 14, '2024-10-22', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (60, 102, 14, '2024-10-21', '09:00:00', '17:30:00', '11:30:00', '12:00:00'),
    (59, 102, 13, '2024-10-19', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (58, 102, 13, '2024-10-18', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (57, 102, 13, '2024-10-16', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (56, 102, 13, '2024-10-15', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (55, 102, 13, '2024-10-14', '07:30:00', '16:00:00', '11:30:00', '12:00:00'),

	# Data for Employee 103
    (54, 103, 12,  '2024-11-08', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (53, 103, 12,  '2024-11-07', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (52, 103, 12,  '2024-11-06', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (51, 103, 12,  '2024-11-05', '06:50:00', '15:50:00', '11:30:00', '12:00:00'),
    (50, 103, 12,  '2024-11-04', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (49, 103, 11,  '2024-11-01', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (48, 103, 11,  '2024-10-31', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (47, 103, 11,  '2024-10-30', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (46, 103, 11,  '2024-10-28', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (45, 103, 10,  '2024-10-25', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (44, 103, 10,  '2024-10-24', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (43, 103, 10,  '2024-10-23', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (42, 103, 10,  '2024-10-22', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (41, 103, 10,  '2024-10-21', '09:00:00', '17:00:00', '11:30:00', '12:00:00'),
    (40, 103, 9,   '2024-10-19', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (39, 103, 9,   '2024-10-18', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (38, 103, 9,   '2024-10-16', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (37, 103, 9,   '2024-10-15', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (36, 103, 9,   '2024-10-14', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),

    # Data for Employee 104
    (35, 104, 8, '2024-11-08', '06:30:00', '15:00:00', '11:30:00', '12:00:00'),
    (34, 104, 8, '2024-11-07', '06:30:00', '15:00:00', '11:30:00', '12:00:00'),
    (33, 104, 8, '2024-11-06', '06:30:00', '15:00:00', '11:30:00', '12:00:00'),
    (32, 104, 8, '2024-11-05', '06:30:00', '15:15:00', '11:30:00', '12:00:00'),
    (31, 104, 8, '2024-11-04', '06:30:00', '16:00:00', '11:30:00', '12:00:00'),
    (30, 104, 6, '2024-10-25', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (29, 104, 6, '2024-10-24', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (28, 104, 6, '2024-10-23', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (27, 104, 6, '2024-10-22', '05:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (26, 104, 6, '2024-10-21', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (25, 104, 5, '2024-10-19', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (24, 104, 5, '2024-10-18', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (23, 104, 5, '2024-10-17', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (22, 104, 5, '2024-10-16', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (21, 104, 5, '2024-10-15', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),
    (20, 104, 5, '2024-10-14', '06:30:00', '15:30:00', '11:30:00', '12:00:00'),

    # Data for Employee 105
    (19, 105, 4, '2024-11-08', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (18, 105, 4, '2024-11-07', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (17, 105, 4, '2024-11-06', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (16, 105, 4, '2024-11-05', '09:00:00', '15:50:00', '11:30:00', '12:00:00'),
    (15, 105, 3, '2024-11-01', '09:00:00', '15:50:00', '11:30:00', '12:00:00'),
    (14, 105, 3, '2024-10-31', '09:00:00', '15:50:00', '11:30:00', '12:00:00'),
    (13, 105, 3, '2024-10-30', '09:00:00', '15:50:00', '11:30:00', '12:00:00'),
    (12, 105, 3, '2024-10-29', '09:00:00', '15:50:00', '11:30:00', '12:00:00'),
    (11, 105, 3, '2024-10-28', '09:00:00', '15:50:00', '11:30:00', '12:00:00'),
    (10, 105, 2, '2024-10-26', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (9, 105, 2, '2024-10-24', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (8, 105, 2, '2024-10-23', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (7, 105, 2, '2024-10-22', '08:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (6, 105, 2, '2024-10-21', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (5, 105, 2, '2024-10-19', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (4, 105, 1, '2024-10-18', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (3, 105, 1, '2024-10-16', '09:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (2, 105, 1, '2024-10-15', '08:00:00', '15:30:00', '11:30:00', '12:00:00'),
    (1, 105, 1, '2024-10-14', '09:00:00', '15:30:00', '11:30:00', '12:00:00')
    

]

# Insert PunchRecord data last
cursor.executemany("""
    INSERT INTO PunchRecord (punch_id, employee_id, week_id, record_date, punch_in_time, punch_out_time, break_start_time, break_end_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", punch_record_data)





# Insert data into MilesLog table
miles_log_data = [
    # Data for Employee 101
    (32, 101, 20, '2024-11-08', 110),
    (31, 101, 19, '2024-10-31', 57),
    (30, 101, 18, '2024-10-25', 113),
    (29, 101, 18, '2024-10-24', 13),
    (28, 101, 14, '2024-10-15', 53),

    # Data for Employee 102
    (27, 102, 13, '2024-10-24', 11),

    # Data for Employee 103
    (26, 103, 12, '2024-11-08', 79),
    (25, 103, 12, '2024-11-07', 151),
    (24, 103, 11, '2024-11-01', 57),
    (23, 103, 11, '2024-10-30', 33),
    (22, 103, 10, '2024-10-25', 37),
    (21, 103, 10, '2024-10-24', 35),
    (20, 103, 10, '2024-10-21', 196),
    (19, 103, 9,  '2024-10-15', 91),
    (18, 103, 9,  '2024-10-14', 64),

    # Data for Employee 104
    (17, 104, 8,   '2024-11-08', 67),
    (16, 104, 8,   '2024-11-07', 32),
    (15, 104, 8,   '2024-11-06', 35),
    (14, 104, 8,   '2024-11-05', 78),
    (13, 104, 6,   '2024-11-04', 41),
    (12, 104, 6,   '2024-10-25', 75),
    (11, 104, 6,   '2024-10-24', 79),
    (10, 104, 6,   '2024-10-23', 72),
    (9,  104, 6,   '2024-10-22', 70),
    (8,  104, 6,   '2024-10-21', 61),
    (7,  104, 5,   '2024-10-19', 75),
    (6,  104, 5,   '2024-10-18', 33),
    (5,  104, 5,   '2024-10-16', 35),
    (4,  104, 5,   '2024-10-15', 51),
    (3,  104, 5,   '2024-10-14', 61),

    # Data for Employee 105
    (2,  105, 4, '2024-11-08', 14),
    (1,  105, 3,'2024-10-31', 17)
]

# Insert MilesLog data last
cursor.executemany("""
    INSERT INTO MilesLog (miles_id, employee_id, week_id, miles_date, miles_driven)
    VALUES (?, ?, ?, ?, ?)
""", miles_log_data)





# Insert data into ChangeLog table
change_log_data = [
    
    (104, 'time', '10/14/2024 6:47', '10/14/2024 6:35', '2024-10-14', '7:15', 'sshannon1030'),
    (104, 'time', '10/14/2024 6:35', '10/14/2024 6:30', '2024-10-14', '14:57', 'sshannon1030'),
    (104, 'time', '10/15/2024 6:57', '10/15/2024 6:30', '2024-10-15', '7:00', 'sshannon1030'),
    (104, 'time', '10/18/2024 6:34', '10/18/2024 6:30', '2024-10-18', '6:35', 'sshannon1030'),
    (104, 'time', '10/19/2024 6:36', '10/19/2024 6:30', '2024-10-19', '11:13', 'sshannon1030'),
    (105, 'time', '10/17/2024 NULL', '10/17/2024 15:00', '2024-10-17', '14:00', 'ocarter69'),
    (105, 'username', 'ocarter69', 'ocarter92', '2024-10-19', '14:00', 'ocarter69'),
    (105, 'time', 'NULL', '10/17/2024 16:00', '2024-11-05', '9:45', 'ocarter92')
]
cursor.executemany("""
    INSERT INTO ChangeLog (employee_id, change_type, old_value, new_value, change_date, change_time, changed_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", change_log_data)



# Insert data into AbsenceRecord table
absence_record_data = [
    (101, 'Late', '2024-11-08', 'Employee had to help a family member move, just came in for catching up shop work'),
    (101, 'Late', '2024-11-04', 'Employee showed up late, talked with him regarding attendance'),
    (101, 'NC/NS', '2024-11-03', 'No Call no show'),
    (101, 'D-Day', '2024-10-28', 'Discretionary day'),
    (101, 'Late', '2024-10-25', 'Employee showed up late, talked with him regarding attendance'),
    (101, 'SICK', '2024-10-19', 'Employees wife called in on behalf of him being sick'),
    (101, 'SICK', '2024-10-18', 'Employees wife called in on behalf of him being sick'),
    
    (102, 'Late', '2024-11-05', 'Employee called in to let us know he is coming in late due to car troubles'),
    (102, 'D-Day', '2024-11-01', 'Discretionary day'),
    (102, 'D-Day', '2024-10-31', 'Discretionary day'),
    (102, 'Late', '2024-10-30', 'Employee called in to let us know he is going to be late'),
    (102, 'Late', '2024-10-29', 'Employee called in to let us know he is going to be late'),
    (102, 'Late', '2024-10-21', 'Employee came in late – Slept through alarm'),
    
    (103, 'Late', '2024-11-05', 'Employee called in that he was running behind due to traffic'),
    (103, 'SICK', '2024-10-29', 'Employee called in sick with the Flu'),
    (103, 'SICK', '2024-10-21', 'Employee called in that he cant come in until 9am'),
    
    (104, 'Vacation', '2024-11-01', 'Vacation Day'),
    (104, 'Vacation', '2024-10-31', 'Vacation Day'),
    (104, 'Vacation', '2024-10-30', 'Vacation Day'),
    (104, 'Vacation', '2024-10-29', 'Vacation Day'),
    (104, 'Vacation', '2024-10-28', 'Vacation Day'),
    (104, 'Write Up', '2024-10-19', 'Theft of company time / A breach of trust / fraudulent reporting of hours'),
    
    (105, 'Late', '2024-10-28', 'Employee called in that they need to come in later because of late night shift at second job, will make it up next day'),
    (105, 'SICK', '2024-10-25', 'Employee called in sick: suspicious that they are calling out to extend weekend'),
    (105, 'SICK', '2024-10-25', 'Spoke to employee about the importance of attendance'),
    (105, 'SICK', '2024-10-20', 'Employee called in sick on Friday'),
    (105, 'Late', '2024-10-15', 'Employee called in that they need to come in later because of late night shift at second job, will make it up next two days')
]

cursor.executemany("""
    INSERT INTO AbsenceRecord (employee_id, absence_type, absence_date, notes)
    VALUES (?, ?, ?, ?)
""", absence_record_data)



# Print all records from Employee table
print("\nEmployee Table:")
cursor.execute("SELECT * FROM Employee")
for row in cursor.fetchall():
    print(row)

# Print all records from WeekLog table
print("\nWeekLog Table:")
cursor.execute("SELECT * FROM WeekLog")
for row in cursor.fetchall():
    print(row)

# Print all records from PunchRecord table
print("\nPunchRecord Table:")
cursor.execute("SELECT * FROM PunchRecord")
for row in cursor.fetchall():
    print(row)

# Print all records from MilesLog table
print("\nMilesLog Table:")
cursor.execute("SELECT * FROM MilesLog")
for row in cursor.fetchall():
    print(row)

# Print all records from ChangeLog table
print("\nChangeLog Table:")
cursor.execute("SELECT * FROM ChangeLog")
for row in cursor.fetchall():
    print(row)

# Print all records from AbsenceRecord table (if it exists)
print("\nAbsenceRecord Table:")
cursor.execute("SELECT * FROM AbsenceRecord")
for row in cursor.fetchall():
    print(row)



try:
    # Your database operations here
    connection.commit()
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    connection.close()

