import json

def load_license_definitions(licenses_path):
    with open(licenses_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_license_definitions(licenses):
    with open(licenses_path, "w", encoding="utf-8") as f:
        json.dump(licenses, f, indent=4, ensure_ascii=False)

def choose_license(licenses_path):
    licenses = load_license_definitions(licenses_path)

    print("\nAvailable licenses:")
    for i, lic in enumerate(licenses, start=1):
        print(f"  {i}. {lic['long_name']} – {lic['description']}")

    print("\n  C. Choose a custom license (URL and name)")
    print("  A. Add a new license to the global list")

    choice = input("\nEnter a number, 'C' for custom, or 'A' to add new: ").strip().lower()

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(licenses):
            return licenses[index]["short_name"]
        else:
            print("Invalid selection.")
            return None

    elif choice == "c":
        print("\nEnter a custom license (this will be stored only in this project):")
        short = input("Short name (e.g., custom-nc): ").strip()
        name = input("Long name: ").strip()
        link = input("Link/URL: ").strip()
        desc = input("Brief description: ").strip()
        return {
            "short_name": short,
            "long_name": name,
            "link": link,
            "description": desc
        }

    elif choice == "a":
        print("\nDefine a new license (this will be added to the global list):")
        short = input("Short name (e.g., cc-by-5.0): ").strip()
        name = input("Long name: ").strip()
        link = input("Link/URL: ").strip()
        desc = input("Brief description: ").strip()

        new_license = {
            "short_name": short,
            "long_name": name,
            "link": link,
            "description": desc
        }

        licenses.append(new_license)
        save_license_definitions(licenses)
        print(f"\nAdded '{short}' to licenses.json.")
        return short

    else:
        print("Invalid choice.")
        return None
