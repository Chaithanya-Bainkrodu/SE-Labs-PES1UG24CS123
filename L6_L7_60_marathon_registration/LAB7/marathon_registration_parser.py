def format_bib_name(name):
    """
    Upper-cases a runner's name and cuts it to 12 characters for the bib.
    Safely handles None, non-string, empty, or whitespace-only inputs.
    """
    if not isinstance(name, str) or not name.strip():
        return "N/A"
    return name.strip().upper()[:12]

def parse_finish_time(text):
    """
    Converts a finish time written as H:MM:SS into seconds.
    Returns 0 if format is invalid or missing.
    """
    if not isinstance(text, str):
        return 0
    parts = text.strip().split(':')
    if len(parts) != 3:
        return 0
    try:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        if hours < 0 or minutes < 0 or seconds < 0:
            return 0
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0

def average_split(text):
    """
    Averages split times given in minutes, separated by spaces.
    Returns 0.0 if inputs are invalid or no valid splits exist.
    """
    if not isinstance(text, str):
        return 0.0
    splits = []
    for token in text.strip().split():
        try:
            splits.append(float(token))
        except ValueError:
            continue
    if not splits:
        return 0.0
    return sum(splits) / len(splits)

def main():
    print("==== Running format_bib_name ====")
    value = input("Enter the name to print on the bib: ")
    print("Bib name:", format_bib_name(value))

    print("\n==== Running parse_finish_time ====")
    value = input("Enter a finish time as H:MM:SS (e.g. 3:45:10): ")
    print("Finish time in seconds:", parse_finish_time(value))

    print("\n==== Running average_split ====")
    value = input("Enter your 5 km split times in minutes separated by spaces (e.g. 25 26 24): ")
    print("Average split (minutes):", average_split(value))

if __name__ == "__main__":
    main()