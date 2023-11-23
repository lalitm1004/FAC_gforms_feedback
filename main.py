import os
from dotenv import load_dotenv

from menu_tool import MenuTool
from form_tool import FormTool
from database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database(os.getenv("MONGODB_CONNECTION_URL"))
    form_tool = FormTool()
    menu_tool = MenuTool()

    # +----------------------+
    # | Write Commands Below |
    # +----------------------+

    print("+-----=FAC Feedback Form=-----+")
    print("(A) - Deploy Todays Menu")
    print("(B) - Collect Responses")
    print("(C) - Create New Deployment")
    print("+-----------------------------+")

    mode = input("> ").lower()
    print("-----")
    if mode == "a":
        todays_menu = menu_tool.get_todays_menu()
        for key, value in todays_menu.items():
            print(f"->> {key}")
            for item in value:
                print(f"\t{item}")
        print("The above items will be deployed. Continue? (Y/N)")
        confirmation = input("> ").lower()
        print("-----")
        if confirmation == "y":
            form_tool.deploy_items(todays_menu=todays_menu)
            print("Deployed.")
        elif confirmation == "n":
            print("Exiting.")
        else:
            print("Invalid input. Exiting.")
    elif mode == "b":
        responses = form_tool.compile_responses()
        for key, value in responses.items():
            print(f"{key} - {value}")
        print("The above will be pushed to database. Continue? (Y/N)")
        confirmation = input("> ").lower()
        print("-----")
        if confirmation == "y":
            db.add_roster(item_rating_dict=responses)
            print("Ratings pushed to database.")
            print("Shift to tommorows menu? (Y/N)")
            confirmation = input("> ").lower()
            if confirmation == "y":
                menu_tool.del_todays_menu()
            elif confirmation == "n":
                print("Exiting.")
            else:
                print("Invalid input. Exiitng.")

            print("Clear form? (Y/N)")
            confirmation = input("> ").lower()
            if confirmation == "y":
                form_tool.clear_form()
                print("Form cleared.")
            elif confirmation == "n":
                print("Exiting.")
            else:
                print("Invalid input. Exiting.")

        elif confirmation == "n":
            print("Exiting.")
        else:
            print("Invalid input. Exiting.")
    elif mode == "c":
        print("Doing so will create a new form. Are you absolutely sure? (Y/N)")
        confirmation = input("> ").lower()
        if confirmation == "y":
            form_tool.create_new_form()
            print("New form deployed. Check your google forms to access it.")
        elif confirmation == "n":
            print("Exiting.")
        else:
            print("Invalid input. Exiting.")
    else:
        print("Invalid input. Exiting.")
