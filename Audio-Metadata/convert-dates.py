import sys
import datetime

# Define a dictionary to map month abbreviations to numbers
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

# Read input from stdin
for line in sys.stdin:
    # Split the input line into date components
    components = line.strip().split('-')
    if len(components)!= 3:
        print(f"Invalid input line: {line.strip()}")
        continue

    day, month, year = components
    month_num = month_map[month[:3]]
    year = int(year)
    if year < 100:
        year += 2000

    # Create a datetime object from the components
    try:
        dt = datetime.date(year, month_num, int(day))
    except ValueError:
        print(f"Invalid date: {line.strip()}")
        continue

    # Print the date in ISO 8601 format
    print(dt.isoformat()[:10])
