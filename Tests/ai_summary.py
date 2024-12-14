from datetime import datetime, timedelta

def generate_employee_summary(employee_data, punch_records, absence_records):
    """Generate a natural language summary of employee attendance."""
    
    summary = []
    
    # Basic employee info
    summary.append(f"Attendance Summary for {employee_data['first_name']} {employee_data['last_name']} (ID: {employee_data['employee_id']})")
    summary.append(f"Role: {employee_data['employee_role']}\n")
    
    # Analyze attendance patterns
    total_days = len(punch_records)
    if total_days > 0:
        on_time_count = sum(1 for record in punch_records 
                          if datetime.strptime(record['punch_in_time'], '%H:%M:%S').time() 
                          <= datetime.strptime('07:00:00', '%H:%M:%S').time())
        late_count = total_days - on_time_count
        
        summary.append(f"Attendance Overview:")
        summary.append(f"- Total Days Worked: {total_days}")
        summary.append(f"- On-time Arrivals: {on_time_count}")
        summary.append(f"- Late Arrivals: {late_count}")
        
        if late_count > 0:
            late_percentage = (late_count / total_days) * 100
            summary.append(f"- Late Arrival Rate: {late_percentage:.1f}%\n")
    
    # Analyze absences
    if absence_records:
        absence_types = {}
        for record in absence_records:
            absence_type = record['absence_type']
            absence_types[absence_type] = absence_types.get(absence_type, 0) + 1
        
        summary.append("Absence Patterns:")
        for absence_type, count in absence_types.items():
            summary.append(f"- {absence_type}: {count} occurrences")
        
        # Add specific absence notes
        summary.append("\nRecent Absence Notes:")
        for record in sorted(absence_records, 
                           key=lambda x: datetime.strptime(x['absence_date'], '%Y-%m-%d'),
                           reverse=True)[:3]:
            summary.append(f"- {record['absence_date']}: {record['notes']}")
    
    # Add recommendations
    summary.append("\nRecommendations:")
    if late_count > total_days * 0.2:  # If late more than 20% of the time
        summary.append("- Employee shows a pattern of late arrivals. Consider scheduling a discussion about punctuality.")
    if any(record['absence_type'] == 'NC/NS' for record in absence_records):
        summary.append("- There are instances of No Call/No Show. This requires immediate attention.")
    if any(record['absence_type'] == 'Write Up' for record in absence_records):
        summary.append("- Employee has received formal write-ups. Monitor closely and document all incidents.")
    
    return "\n".join(summary) 