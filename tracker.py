import json
import datetime

def load_data(filepath="data.json"):
  """Loads data from a JSON file.

  Args:
    filepath: The path to the JSON file (defaults to "data.json").

  Returns:
    A list of entries if the file exists and contains valid JSON,
    otherwise an empty list.
  """
  try:
    with open(filepath, "r") as f:
      data = json.load(f)
      return data
  except FileNotFoundError:
    return []
  except json.JSONDecodeError:
    # Handle invalid JSON, e.g., by logging a warning
    print(f"Warning: Could not decode JSON from {filepath}. Starting with an empty list.")
    return []

def save_data(data, filepath="data.json"):
  """Saves data to a JSON file.

  Args:
    data: The data to save (expected to be a list of entries).
    filepath: The path to the JSON file (defaults to "data.json").
  """
  with open(filepath, "w") as f:
    json.dump(data, f, indent=4)

def view_entries():
  """Displays past entries."""
  entries = load_data()
  if not entries:
    print("No entries found.")
    return

  for entry in entries:
    # Format timestamp for better readability
    try:
      timestamp_obj = datetime.datetime.fromisoformat(entry['timestamp'])
      formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError): # Handle cases where timestamp might be malformed or not a string
        formatted_timestamp = entry.get('timestamp', 'N/A')

    print(f"Timestamp: {formatted_timestamp}")
    print(f"  Highlight: {entry.get('highlight', 'N/A')}")
    print(f"  Lowlight: {entry.get('lowlight', 'N/A')}")
    print(f"  Happiness: {entry.get('happiness', 'N/A')}")
    print(f"  Major Event: {entry.get('major_event', 'N/A')}")
    print("---")

def main():
  """Main function for the application."""
  while True:
    choice = input("Do you want to (a)dd a new entry or (v)iew past entries? (a/v): ").lower()
    if choice == 'a':
      entries = load_data()
      timestamp = datetime.datetime.now().isoformat()

      highlight = input("What was the highlight of your day? ")
      lowlight = input("What was the lowlight of your day? ")

      while True:
        try:
          happiness_level = int(input("What is your happiness level (1-10)? "))
          if 1 <= happiness_level <= 10:
            break
          else:
            print("Invalid input. Happiness level must be between 1 and 10.")
        except ValueError:
          print("Invalid input. Please enter a number.")

      major_event = input("Did anything major happen today? ")

      new_entry = {
        "timestamp": timestamp,
        "highlight": highlight,
        "lowlight": lowlight,
        "happiness": happiness_level,
        "major_event": major_event,
      }

      entries.append(new_entry)
      save_data(entries)
      print("Entry saved successfully!")
      break # Exit after adding an entry
    elif choice == 'v':
      view_entries()
      break # Exit after viewing entries
    else:
      print("Invalid choice. Please enter 'a' or 'v'.")

if __name__ == "__main__":
  main()
