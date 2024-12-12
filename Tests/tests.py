from calculations import calculate_break_duration

print("Testing calculate_break_duration:")

# Test cases with corrected time format
test_cases = [
    ("12:00:00", "12:30:00"),  # 30 minutes break
    ("10:15:00", "10:45:00"),  # 30 minutes break
    ("08:00:00", "08:10:00"),  # 10 minutes break
    ("14:00:00", "15:00:00"),  # 1 hour break
    (None, None),              # No break
    ("10:30:00", None),        # Break start with no end
    (None, "11:00:00"),        # Break end with no start
]

# Expected outputs
expected_outputs = [
    30.0,
    30.0,
    10.0,
    60.0,
    0.0,
    0.0,
    0.0,
]

# Running the tests
for i, (start, end) in enumerate(test_cases):
    try:
        result = calculate_break_duration(start, end)
        assert result == expected_outputs[i], f"Test case {i+1} failed: Expected {expected_outputs[i]}, got {result}"
        print(f"Test case {i+1} passed: {start} to {end} = {result} minutes")
    except Exception as e:
        print(f"Test case {i+1} failed: {start} to {end} raised an error - {e}")
