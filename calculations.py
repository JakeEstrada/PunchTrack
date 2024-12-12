from datetime import datetime, timedelta
from collections import defaultdict

def parse_time(time_str):
    """
    Parse a time string in either '%H:%M:%S' or '%H:%M' format.
    """
    try:
        # Try parsing as '%H:%M:%S'
        return datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        try:
            # Try parsing as '%H:%M'
            return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            # Handle invalid time format
            raise ValueError(f"Time data '{time_str}' does not match format '%H:%M:%S' or '%H:%M'")

def calculate_break_duration(break_start, break_end):
    """
    Calculate the duration of a break in minutes.
    """
    if not break_start or not break_end:
        return 0.0  # No break if either time is missing

    # Parse times using the updated function
    break_start_time = parse_time(break_start)
    break_end_time = parse_time(break_end)

    # Calculate the duration
    duration = break_end_time - break_start_time
    return duration.total_seconds() / 60  # Convert seconds to minutes


def time_to_hours(time_str):
    """Convert HH:MM time format to hours as a float."""
    hours, minutes = map(int, time_str.split(":"))
    return hours + minutes / 60.0

def calculate_daily_hours(clock_in, clock_out, break_duration):
    print(f"Clock-in: {clock_in}, Clock-out: {clock_out}, Break Duration: {break_duration}")
    
    if not clock_in or not clock_out:
        return 0

    # Normalize time format
    if len(clock_in.split(":")) == 2:
        clock_in += ":00"  # Add seconds if missing
    if len(clock_out.split(":")) == 2:
        clock_out += ":00"

    clock_in_time = datetime.strptime(clock_in, "%H:%M:%S")
    clock_out_time = datetime.strptime(clock_out, "%H:%M:%S")

    total_worked = (clock_out_time - clock_in_time).seconds / 3600
    print(f"Total Worked (raw): {total_worked} hours")
    return round(total_worked - break_duration / 60, 2)




def calculate_overtime(hours):
    print(f"Calculating Overtime: Total Hours Worked: {hours}")
    overtime = max(0, hours - 8)
    print(f"Overtime: {overtime}")
    return overtime


def calculate_weighted_hours(hours, overtime):
    print(f"Calculating Weighted Hours: Hours: {hours}, Overtime: {overtime}")
    weighted_hours = hours + (1.5 * overtime)
    print(f"Weighted Hours: {weighted_hours}")
    return weighted_hours


def group_by_weeks(work_records):
    """
    Group work records into weeks based on their dates.
    Each week starts on a Sunday.
    """
    weekly_data = defaultdict(list)

    for record in work_records:
        date = datetime.strptime(record['day'], '%Y-%m-%d')  # Assuming 'day' is in 'YYYY-MM-DD' format

        # Adjust to start the week on Sunday
        sunday = date - timedelta(days=date.weekday() + 1 if date.weekday() < 6 else 0)

        # Group by the week starting date (Sunday)
        weekly_data[sunday.strftime('%Y-%m-%d')].append(record)

    return weekly_data

def calculate_weekly_totals(work_records):
    """
    Group work records by weeks and calculate weekly totals.
    """
    weekly_records = group_by_weeks(work_records)

    weekly_totals = {}
    for week, records in weekly_records.items():
        total_hours = 0
        total_overtime = 0
        total_weighted_hours = 0

        for record in records:
            clock_in = record.get("clock_in", "00:00:00")
            clock_out = record.get("clock_out", "00:00:00")
            break_start = record.get("break_start")
            break_end = record.get("break_end")
            break_duration = calculate_break_duration(break_start, break_end)
            daily_hours = calculate_daily_hours(clock_in, clock_out, break_duration)
            daily_overtime = calculate_overtime(daily_hours)
            daily_weighted_hours = calculate_weighted_hours(daily_hours, daily_overtime)

            total_hours += daily_hours
            total_overtime += daily_overtime
            total_weighted_hours += daily_weighted_hours

        weekly_totals[week] = {
            'total_hours': round(total_hours, 2),
            'total_overtime': round(total_overtime, 2),
            'total_weighted_hours': round(total_weighted_hours, 2)
        }

    return weekly_totals




def calculate_week_ending_date(date):
    """
    Calculate the week-ending date (Saturday) for a given date.
    """
    date = datetime.strptime(date, '%Y-%m-%d')
    week_end = date + timedelta(days=(5 - date.weekday()))
    return week_end.strftime('%Y-%m-%d')

# Example Usage:
if __name__ == "__main__":
    # Mock data for testing
    work_records = [
        {'day': '2024-11-27', 'clock_in': '06:30', 'clock_out': '15:30', 'break_duration': 0.5},
        {'day': '2024-11-28', 'clock_in': '06:30', 'clock_out': '15:30', 'break_duration': 0.5},
        {'day': '2024-11-29', 'clock_in': '06:30', 'clock_out': '15:30', 'break_duration': 0.5},
        {'day': '2024-11-30', 'clock_in': '06:30', 'clock_out': '15:30', 'break_duration': 0.5},
        {'day': '2024-12-01', 'clock_in': '06:30', 'clock_out': '15:30', 'break_duration': 0.5}
    ]

    weekly_totals = calculate_weekly_totals(work_records)
    print("Weekly Totals:", weekly_totals)
