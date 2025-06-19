# publine.py

import sys
from src import new_project, project_manager

def main_menu():
    print("\n📘 Welcome to Publine")
    print("Your personal publishing pipeline\n")
    print("[1] Create new project")
    print("[2] Manage existing project")
    print("[3] Tools (coming soon)")
    print("[4] Help (coming soon)")
    print("[5] Exit")

    choice = input("Select an option: ").strip()

    if choice == '1':
        new_project.create_project()
    elif choice == '2':
        project_manager.manage_projects()
    elif choice == '3':
        print("\n🧰 Tools coming soon!")
    elif choice == '4':
        print("\n📖 Help section under construction.")
    elif choice == '5':
        print("\n👋 Goodbye, and happy publishing!\n")
        sys.exit(0)
    else:
        print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    while True:
        main_menu()
