# Food Affairs Committee Feedback
This project uses Google Forms API to automatically update a google form with todays menu each day. At the end of the day, the script is run again to collect user responses from the google form. A weighted average is calculated and pushed onto a mongoDB database.

# Steps to run for your own project.
1. Configure your OAuth consent screen on google cloud console.
2. Clone this repository and navigate into it.
3. Run `pip install -r requirements.txt` (Use a virtual environment if wanted)
3. Make and download an OAuth client ID json file. Rename it to `client_secret.json` and place it in `data/`.
4. Create a `current_deployment.json` file in `data/`.
5. Create a mongoDB cluster and save its connection URL in a `.env` file under `MONGODB_CONNECTION_URL`. (Make sure to include the password in the URL.)
6. Update `data/upcoming_menu.csv` as required. Prefixes:
    - `<b>` - Breakfast
    - `<l>` - Lunch
    - `<d>` - Dinner
7. Run `main.py` and follow the terminal.

# TODO
- Automate a method to create `upcoming_menu.csv`. Currently it needs to be done manually.
- Add a time function to run the script 24/7 and automatically run commands. Currently this script needs to be run each time a command needs to be run.
- Make a master food database to document each item that has/will ever be deployed. Implement a fuzzy string search algorithm to account for ease of use.