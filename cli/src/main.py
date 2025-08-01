# publine.py

import sys
from cli.src import new_project, project_manager

def main_menu():
    print("""
📘 Welcome to Publine
Your personal publishing pipeline

1. Create new project
2. Manage existing project
3. Settings
4. Help (coming soon)
5. Exit
    """)
    
    choice = input("Select an option: ").strip()

    if choice == '1':
        new_project.create_project()
    elif choice == '2':
        project_manager.manage_projects()
    elif choice == '3':
        settings_menu()
    elif choice == '4':
        print("\n📖 Help section under construction.")
    elif choice == '5':
        print("\n👋 Goodbye, and happy publishing!\n")
        sys.exit(0)
    else:
        print("❌ Invalid option. Please try again.")

def settings_menu():
    while True:
        print("""
🔧 Settings Menu

        1. Configure AI Provider
2. Back
            """)
        choice = input("Select an option: ")

        if choice == "1":
            configure_ai_provider() 
        elif choice == "2":
            break
        else:
            print("Invalid selection. Try again.")

if __name__ == "__main__":
    while True:
        main_menu()
