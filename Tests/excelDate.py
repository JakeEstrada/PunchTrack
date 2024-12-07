from datetime import datetime, timedelta

def string_to_excel_date(input_string):
    # Split the string using '-' as a delimiter
    parts = input_string.split('-')
    
    # Use only the first part for the date calculation
    if len(parts) < 1 or not parts[0].isdigit():
        raise ValueError("Input must be in the format '12345-678', with a valid numeric first part.")
    
    # Convert the first part to an integer
    date_number = int(parts[0])
    print(f"Original date number: {date_number}")  # Debug output

    # Adjust for the year 2000 base date
    # Excel day 0 for this range starts at 2000-01-01 as 36526
    year_2000_base_number = 36526
    adjusted_days = date_number - year_2000_base_number
    print(f"Adjusted days since year 2000: {adjusted_days}")  # Debug output

    # Calculate the corresponding date
    excel_base_date = datetime(2000, 1, 1)  # New base date
    excel_date = excel_base_date + timedelta(days=adjusted_days)
    print(f"Calculated Excel date: {excel_date}")  # Debug output
    
    return excel_date

# Main program
if __name__ == "__main__":
    user_input = input("Enter the string (e.g., '36526-678'): ")
    try:
        result_date = string_to_excel_date(user_input)
        print(f"The Excel date for '{user_input}' is: {result_date.strftime('%Y-%m-%d')}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except OverflowError as oe:
        print(f"Error: {oe}")
