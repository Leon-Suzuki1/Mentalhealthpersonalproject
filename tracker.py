import json
from datetime import datetime, date, timedelta
# Assuming auth.py is in the same directory
from auth import sign_up, log_in

DATA_FILE_TEMPLATE = "data_{}.json"

def get_email_prefix(email):
  """Extracts the part of an email before the '@' symbol."""
  if not isinstance(email, str) or '@' not in email:
    # Return a default or raise an error if email format is unexpected
    # For now, returning a placeholder to avoid crashes if an invalid email is passed
    print(f"Warning: Invalid email format provided: {email}. Using 'unknown_user' as prefix.")
    return "unknown_user"
  return email.split('@')[0]

def calculate_streak(user_email_prefix):
  """Calculates the current streak of consecutive days with entries."""
  entries = load_data(user_email_prefix)
  if not entries:
    return 0

  # Sort entries by timestamp in descending order (most recent first)
  try:
    entries.sort(key=lambda x: x['timestamp'], reverse=True)
  except (TypeError, KeyError) as e:
    print(f"Error sorting entries: {e}. Ensure all entries have a valid 'timestamp'.")
    return 0 # Cannot calculate streak if timestamps are unreliable

  today = date.today()
  streak = 0

  # Check the most recent entry first
  try:
    most_recent_entry_ts_str = entries[0]['timestamp']
    most_recent_entry_date = datetime.fromisoformat(most_recent_entry_ts_str).date()
  except (ValueError, KeyError, IndexError) as e:
    print(f"Error processing most recent entry's timestamp: {e}")
    return 0 # Cannot determine streak if the latest entry is problematic

  if most_recent_entry_date == today or most_recent_entry_date == today - timedelta(days=1):
    streak = 1
  else:
    # If the most recent entry is older than yesterday, there's no current streak
    return 0

  if len(entries) > 1:
    last_streak_date = most_recent_entry_date
    for entry in entries[1:]:
      try:
        current_entry_ts_str = entry['timestamp']
        current_entry_date = datetime.fromisoformat(current_entry_ts_str).date()
      except (ValueError, KeyError) as e:
        print(f"Warning: Skipping entry with problematic timestamp during streak calculation: {e}")
        continue # Skip this entry and try to continue the streak with others

      expected_date = last_streak_date - timedelta(days=1)
      if current_entry_date == expected_date:
        streak += 1
        last_streak_date = current_entry_date
      elif current_entry_date < expected_date:
        # Gap in days, streak is broken
        break
      # If current_entry_date == last_streak_date, it's an entry from the same day, continue
      # If current_entry_date > expected_date (and not same day), implies unsorted or future data, break
      elif current_entry_date > expected_date and current_entry_date != last_streak_date:
          print(f"Warning: Encountered an out-of-order or future-dated entry ({current_entry_date}) after {last_streak_date}. Streak calculation might be affected.")
          break

  return streak

def provide_proactive_support(user_details, new_entry_happiness):
  """Provides proactive support messages based on happiness level."""
  HAPPINESS_THRESHOLD = 4
  if new_entry_happiness < HAPPINESS_THRESHOLD:
    print("\n--- Gentle Reminder ---")
    print("It's understandable to have tough days. Remember to be gentle with yourself. Small acts of self-care can make a difference.")

    coping_mechanisms = user_details.get("coping_mechanisms", "") # Default to empty string
    if coping_mechanisms: # Now just check if it's a non-empty string (None is handled by default)
      print(f"You mentioned that the following helps you feel better or calm down: {coping_mechanisms}")
    else:
      print("Consider engaging in an activity you usually find relaxing or enjoyable.")
    print("-----------------------\n")

def load_data(user_email_prefix):
  """Loads data from a user-specific JSON file.

  Args:
    user_email_prefix: The prefix derived from the user's email to identify their data file.

  Returns:
    A list of entries if the file exists and contains valid JSON,
    otherwise an empty list.
  """
  filepath = DATA_FILE_TEMPLATE.format(user_email_prefix)
  try:
    with open(filepath, "r") as f:
      data = json.load(f)
      # Ensure data is a list, as expected by downstream functions
      if not isinstance(data, list):
          print(f"Warning: Data in {filepath} is not a list. Returning empty list.")
          return []
      return data
  except FileNotFoundError:
    return []
  except json.JSONDecodeError:
    # Handle invalid JSON, e.g., by logging a warning
    print(f"Warning: Could not decode JSON from {filepath}. Starting with an empty list.")
    return []

def save_data(data, user_email_prefix):
  """Saves data to a user-specific JSON file.

  Args:
    data: The data to save (expected to be a list of entries).
    user_email_prefix: The prefix derived from the user's email to identify their data file.
  """
  filepath = DATA_FILE_TEMPLATE.format(user_email_prefix)
  try:
    with open(filepath, "w") as f:
      json.dump(data, f, indent=4)
  except IOError as e:
    print(f"Error: Could not save entry data to {filepath}. {e}")

def view_entries(user_email_prefix): # Needs user_email_prefix to load correct data
  """Displays past entries for a specific user."""
  entries = load_data(user_email_prefix)
  if not entries:
    print("No entries found.")
    return

  # Sort entries by timestamp in ascending order for viewing
  try:
    entries.sort(key=lambda x: x['timestamp'])
  except (TypeError, KeyError) as e:
    print(f"Warning: Could not sort entries for viewing due to: {e}. Displaying in current order.")

  for entry in entries:
    # Format timestamp for better readability
    try:
      # Using datetime.fromisoformat correctly
      timestamp_obj = datetime.fromisoformat(entry['timestamp'])
      formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, KeyError) as e: # Handle cases where timestamp might be malformed, not a string or missing
        formatted_timestamp = entry.get('timestamp', 'N/A')
        print(f"Warning: Could not parse timestamp '{entry.get('timestamp')}' for an entry: {e}")

    print(f"Timestamp: {formatted_timestamp}")
    print(f"  Highlight: {entry.get('highlight', 'N/A')}")
    print(f"  Lowlight: {entry.get('lowlight', 'N/A')}")
    print(f"  Happiness: {entry.get('happiness', 'N/A')}")
    print(f"  Major Event: {entry.get('major_event', 'N/A')}")
    print("---")

def main():
  """Main function for the application."""
  current_user = None
  user_email_prefix = None # Will be set after login/signup

  while True:
    if current_user is None:
      # Logged-out state
      choice = input("Choose action: (S)ign up, (L)og in, (Q)uit: ").lower()
      if choice == 's':
        user = sign_up() # This function from auth.py now handles onboarding
        if user:
          current_user = user
          user_email_prefix = get_email_prefix(current_user['email'])
          # Calculate streak - for a new user, it's likely 0 unless they had prior data
          # (auth.py prevents re-signup, so this is mostly for the first time)
          streak = calculate_streak(user_email_prefix)
          print(f"\nWelcome, {current_user['email']}!")
          print(f"It's great to have you on board. Your current streak is: {streak} days.")
          # Onboarding questions are now part of sign_up() in auth.py
      elif choice == 'l':
        user = log_in()
        if user:
          current_user = user
          user_email_prefix = get_email_prefix(current_user['email'])
          streak = calculate_streak(user_email_prefix)
          print(f"\nWelcome back, {current_user['email']}! Your current streak: {streak} days.")
      elif choice == 'q':
        print("Goodbye!")
        break
      else:
        print("Invalid choice. Please try again.")
    else:
      # Logged-in state
      # user_email_prefix should already be set from login/signup
      action = input(f"\nLogged in as {current_user['email']}. Choose action: (A)dd entry, (V)iew entries, (L)og out: ").lower()
      if action == 'a':
        highlight = input("What was the highlight of your day? ")
        lowlight = input("What was the lowlight of your day? ")

        happiness_level = -1
        while True:
          try:
            happiness_str = input("What is your happiness level (1-10)? ")
            happiness_level = int(happiness_str)
            if 1 <= happiness_level <= 10:
              break
            else:
              print("Please enter a number between 1 and 10.")
          except ValueError:
            print("Invalid input. Please enter a number.")

        major_event = input("Did anything major happen today? ")
        timestamp = datetime.now().isoformat()

        new_entry = {
          "timestamp": timestamp,
          "highlight": highlight,
          "lowlight": lowlight,
          "happiness": happiness_level,
          "major_event": major_event
        }

        entries = load_data(user_email_prefix)
        entries.append(new_entry)
        save_data(entries, user_email_prefix)
        print("Entry saved successfully!")

        provide_proactive_support(current_user, happiness_level) # Pass the full current_user dict

        current_streak = calculate_streak(user_email_prefix)
        print(f"Your updated streak: {current_streak} days.")

        # --- Distress Condition Check ---
        all_user_entries = load_data(user_email_prefix)
        # Sort entries by timestamp (newest first), safely
        all_user_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        distress_condition_met = False
        if len(all_user_entries) >= 5:
          recent_five_entries = all_user_entries[:5]
          low_happiness_count = 0
          for entry in recent_five_entries:
            happiness = entry.get('happiness')
            # Check if happiness is explicitly 1 or 2
            if happiness == 1 or happiness == 2:
              low_happiness_count += 1

          if low_happiness_count == 5:
            distress_condition_met = True

        # Check the flag and print the message if the condition is met
        if distress_condition_met:
          print("\nWe've noticed you may be going through a difficult time. Please remember that it's okay to seek support.")
          print("Talking to a trusted friend, family member, teacher, or a professional counselor can often make a big difference.")
          print("You don't have to go through this alone.\n")
        # --- End Distress Condition Check & Message ---

      elif action == 'v':
        view_entries(user_email_prefix)
      elif action == 'l':
        print(f"Logging out {current_user['email']}.")
        current_user = None
        user_email_prefix = None # Reset prefix
      else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
  # --- Cleared placeholder user data and test calls ---
  # The main function now handles the application flow.
  main()
