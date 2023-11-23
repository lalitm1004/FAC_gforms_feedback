import pandas as pd
from pathlib import Path

UPCOMING_MENU_PATH = str(Path("data/upcoming_menu.csv"))


class MenuTool:
    def get_todays_menu(self) -> dict:
        df = pd.read_csv(UPCOMING_MENU_PATH)
        df.drop(["Unnamed: 0"], axis=1, inplace=True)

        todays_menu = {
            "Breakfast": [],
            "Lunch": [],
            "Dinner": [],
        }
        for item in df[df.columns[0]]:
            item: str
            if item == "-":
                continue

            if item.startswith("<b>"):
                todays_menu["Breakfast"].append(item.removeprefix("<b>"))
            if item.startswith("<l>"):
                todays_menu["Lunch"].append(item.removeprefix("<l>"))
            if item.startswith("<d>"):
                todays_menu["Dinner"].append(item.removeprefix("<d>"))

        return todays_menu

    def del_todays_menu(self):
        df = pd.read_csv(UPCOMING_MENU_PATH)
        df.drop(["Unnamed: 0"], axis=1, inplace=True)
        df.drop([df.columns[0]], axis=1, inplace=True)
        df.to_csv(UPCOMING_MENU_PATH)


if __name__ == "__main__":
    menu = MenuTool()
    print(menu.get_todays_menu())
    # print(menu.del_todays_menu())
