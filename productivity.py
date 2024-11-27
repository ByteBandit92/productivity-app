import json
import time
from datetime import datetime, timedelta
from termcolor import cprint
import random
import os
import threading
import select
import sys

def load_tasks():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tasks_path = os.path.join(script_dir, "tasks.json")
    
    try:
        with open(tasks_path, "r") as f:
            tasks = json.load(f)
            if not tasks:
                print("Error: No tasks found in tasks.json")
                exit(1)
            return tasks
    except FileNotFoundError:
        sample_tasks = {
            "Code Review": 30,
            "Development": 45,
            "Testing": 25,
            "Documentation": 20
        }
        with open(tasks_path, "w") as f:
            json.dump(sample_tasks, f, indent=4)
        print("Created new tasks.json with sample tasks")
        return sample_tasks
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in tasks.json")
        exit(1)

def get_tasks_schedule(tasks):
    tasks_start_time = datetime.now()
    schedule = []
    for task, minutes in tasks.items():
        end_time = tasks_start_time + timedelta(minutes=minutes)
        schedule.append((task, tasks_start_time, end_time))
        tasks_start_time = end_time
    return schedule

def check_input():
    if select.select([sys.stdin], [], [], 0.0)[0]:
        return sys.stdin.readline().strip()
    return None

# ... (previous imports and functions remain the same)

def main():
    # Move list_of_reminders to the beginning of main()
    list_of_reminders = [
        "Every day I get better, keep going!",
        "Keep walking, it's a marathon - you will win if you walk on!",
        "You're learning skills to be free and independent forever!",
        "I become my thoughts!",
        "I will be the best algo trader!"
    ]

    try:
        tasks = load_tasks()
        schedule = get_tasks_schedule(tasks)
        current_index = 0
        is_paused = False
        pause_start_time = None
        blink_state = False
        last_reminder_time = datetime.now()
        current_reminder = random.choice(list_of_reminders)

        print("\nStarting task scheduler...")
        print(f"Loaded {len(tasks)} tasks for today\n")
        print("Commands: 'p' to pause/resume, 'q' to quit")

        while True:
            now = datetime.now()
            current_task, start_time, end_time = schedule[current_index]
            
            if not is_paused:
                remaining_time = end_time - now
                remaining_minutes = int(remaining_time.total_seconds() // 60)
                remaining_seconds = int(remaining_time.total_seconds() % 60)
            
            # Update reminder every minute
            if (now - last_reminder_time).total_seconds() >= 60:
                current_reminder = random.choice(list_of_reminders)
                last_reminder_time = now
            
            # Clear screen
            os.system('clear')

            print("\n=== Task Schedule ===")
            if is_paused:
                cprint("⏸  PAUSED - Enter 'p' to resume", "white", "on_yellow")
            else:
                cprint("▶  Running - Enter 'p' to pause", "white", "on_blue")
            print()
            
            for index, (task, s_time, e_time) in enumerate(schedule):
                if index < current_index:
                    print(f"✓ {task} done: {e_time.strftime('%H:%M')}")
                elif index == current_index:
                    if is_paused:
                        cprint(f"► {task} - PAUSED at {remaining_minutes}:{remaining_seconds:02d}", "white", "on_yellow")
                    elif remaining_minutes < 2:
                        if blink_state:
                            cprint(f"► {task} - {remaining_minutes}:{remaining_seconds:02d} mins left!", "white", "on_red", attrs=["bold"])
                        else:
                            print(" " * (len(task) + 20))
                    elif remaining_minutes < 5:
                        cprint(f"► {task} - {remaining_minutes}:{remaining_seconds:02d} mins", "white", "on_red")
                    else:
                        cprint(f"► {task} - {remaining_minutes}:{remaining_seconds:02d} mins", "white", "on_blue")
                else:
                    print(f"• {task} @ {s_time.strftime('%H:%M')}")

            # Display current reminder
            print("\n💪 " + current_reminder)
            print("\nCommands:")
            print("'p': Pause/Resume")
            print("'q': Quit")
            
            # Toggle blink state every second
            blink_state = not blink_state
            
            # Check for input with a timeout to allow blinking
            if sys.stdin in select.select([sys.stdin], [], [], 0.5)[0]:
                command = sys.stdin.readline().strip().lower()
                if command == 'p':
                    is_paused = not is_paused
                    if is_paused:
                        pause_start_time = now
                    else:
                        # Adjust all future task times by the pause duration
                        pause_duration = now - pause_start_time
                        for i in range(current_index, len(schedule)):
                            task, start_time, end_time = schedule[i]
                            schedule[i] = (task, 
                                         start_time + pause_duration, 
                                         end_time + pause_duration)
                elif command == 'q':
                    print("\nExiting program. Goodbye!")
                    break

            if not is_paused and now >= end_time:
                current_index += 1
                if current_index >= len(schedule):
                    cprint("\n🎉 All tasks are completed! Well done!", "white", "on_green")
                    break

    except KeyboardInterrupt:
        print("\n\nProgram stopped by user. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()