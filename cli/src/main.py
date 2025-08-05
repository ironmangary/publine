# Entry point for the Publine CLI

import sys
from cli.src import new_project, project_manager

def main_menu():
    print("""
📘 Welcome to Publine
Your personal publishing pipeline

1. Create new project
2. Manage existing project
3. Exit
    """)
    
    choice = input("Select an option: ").strip()

    if choice == '1':
        new_project.create_project()
    elif choice == '2':
        project_manager.manage_projects()
    elif choice == '3':
        print("\n👋 Goodbye, and happy publishing!\n")
        sys.exit(0)
    else:
        print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    while True:
        main_menu()
