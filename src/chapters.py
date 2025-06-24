from src.chapter_utils import list_chapters, load_chapters, save_chapters, add_chapter, edit_chapter, delete_chapter, get_chapters_path

def manage_chapters(project_path):
    while True:
        print("\n📚 Chapter Management")

        chapters = list_chapters(project_path)
        if chapters:
            print("Existing chapters:")
            for ch in chapters:
                num = ch.get("number")
                title = ch.get("title", "<Untitled>")
                print(f"  [{num}] {title}")
        else:
            print("No chapters yet.")

        print("\nOptions:")
        print("[1] Add a new chapter")
        print("[2] Edit a chapter entry")
        print("[3] Delete a chapter")
        print("[4] Back")

        choice = input("Select an option: ").strip()

        if choice == "1":
            add_chapter(project_path)
        elif choice == "2":
            edit_chapter(project_path, chapters)
        elif choice == "3":
            delete_chapter(project_path, chapters)
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice.")
