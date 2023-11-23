import os
import json
from pathlib import Path

# Google OAuth Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.body.readonly",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

TOKEN_PATH = str(Path("data/token.json"))
CLIENT_SECRET_PATH = str(Path("data/client_secret.json"))
CURRENT_DEPLOYMENT_PATH = str(Path("data/current_deployment.json"))


class FormTool:
    def __init__(self) -> None:
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        self.form_service = build(
            "forms",
            "v1",
            credentials=creds,
            discoveryServiceUrl=DISCOVERY_DOC,
            static_discovery=False,
        )

    # Helper Functions
    def load_current_deployment(self) -> dict:
        with open(CURRENT_DEPLOYMENT_PATH, "r") as f:
            current_deployment = json.load(f)
        return current_deployment

    def update_current_deployment(self, updated_data) -> None:
        with open(CURRENT_DEPLOYMENT_PATH, "w") as f:
            json.dump(updated_data, f, indent=4)

    def add_ratings(self, ratings: list) -> dict:
        for index in range(0, len(ratings) - 1):
            ratings[0]["N/A"] += ratings[index + 1]["N/A"]
            ratings[0]["1"] += ratings[index + 1]["1"]
            ratings[0]["2"] += ratings[index + 1]["2"]
            ratings[0]["3"] += ratings[index + 1]["3"]
            ratings[0]["4"] += ratings[index + 1]["4"]
            ratings[0]["5"] += ratings[index + 1]["5"]
        return ratings[0]

    def get_weighted_average_rating(self, rating: dict) -> float:
        _1_ratings = rating["1"]
        _2_ratings = rating["2"]
        _3_ratings = rating["3"]
        _4_ratings = rating["4"]
        _5_ratings = rating["5"]
        total_ratings = _1_ratings + _2_ratings + _3_ratings + _4_ratings + _5_ratings
        weighted_sum = (
            1 * _1_ratings
            + 2 * _2_ratings
            + 3 * _3_ratings
            + 4 * _4_ratings
            + 5 * _5_ratings
        )
        try:
            return round(weighted_sum / total_ratings, ndigits=2)
        except ZeroDivisionError:
            return -1.0

    def create_new_form(self) -> None:
        current_deployment = self.load_current_deployment()
        result = (
            self.form()
            .create(body={"info": {"title": "FAC Feedback Testing"}})
            .execute()
        )
        current_deployment["formId"] = result["formId"]
        self.update_current_deployment(current_deployment)

    def clear_form(self) -> None:
        current_deployement = self.load_current_deployment()
        form_id = current_deployement["formId"]
        menu_strength = sum(
            len(current_deployement["deployedItems"][i])
            for i in current_deployement["deployedItems"].keys()
        )
        for i in range(menu_strength):
            self.form_service.forms().batchUpdate(
                formId=form_id,
                body={"requests": [{"deleteItem": {"location": {"index": 0}}}]},
            ).execute()
            print(f"{round(((i+1)/menu_strength)*100, ndigits=2)}% Done")

    def deploy_items(self, todays_menu: dict) -> None:
        current_deployment = self.load_current_deployment()
        form_id = current_deployment["formId"]
        menu_strength = sum(len(todays_menu[i]) for i in todays_menu.keys())
        current_deployment["deployedItems"] = {
            "Breakfast": {},
            "Lunch": {},
            "Dinner": {},
        }
        index = 0
        for key in todays_menu.keys():
            items: list = todays_menu[key]
            for item in items:
                request_body = {
                    "requests": [
                        {
                            "createItem": {
                                "item": {
                                    "title": f"{key} - {item}",
                                    "questionItem": {
                                        "question": {
                                            "required": True,
                                            "choiceQuestion": {
                                                "type": "RADIO",
                                                "options": [
                                                    {"value": "N/A"},
                                                    {"value": "1"},
                                                    {"value": "2"},
                                                    {"value": "3"},
                                                    {"value": "4"},
                                                    {"value": "5"},
                                                ],
                                                "shuffle": False,
                                            },
                                        }
                                    },
                                },
                                "location": {"index": index},
                            }
                        }
                    ]
                }
                response = (
                    self.form_service.forms()
                    .batchUpdate(formId=form_id, body=request_body)
                    .execute()
                )
                current_deployment["deployedItems"][key][
                    response["replies"][0]["createItem"]["questionId"][0]
                ] = item
                index += 1

                print(f"{round((index/menu_strength)*100, ndigits=2)}% Done")

        self.update_current_deployment(current_deployment)

    def compile_responses(self) -> dict:
        current_deployment = self.load_current_deployment()
        deployed_items: dict = current_deployment["deployedItems"]
        form_id = current_deployment["formId"]
        # todays_menu: dict = current_deployment["todaysMenu"]

        item_qid_dict = {}
        for menu_type in deployed_items.keys():
            for qid, item in deployed_items[menu_type].items():
                if item in item_qid_dict.keys():
                    item_qid_dict[item].append(qid)
                else:
                    item_qid_dict[item] = [qid]

        qid_ratings_dict = {}
        for menu_type in deployed_items.keys():
            for qid in deployed_items[menu_type].keys():
                qid_ratings_dict[qid] = {
                    "N/A": 0,
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0,
                }

        responses = (
            self.form_service.forms()
            .responses()
            .list(formId=form_id)
            .execute()["responses"]
        )
        for response in responses:
            answers: dict = response["answers"]
            for qid in answers.keys():
                qid_ratings_dict[qid][
                    answers[qid]["textAnswers"]["answers"][0]["value"]
                ] += 1

        for item in item_qid_dict.keys():
            for index, qid in enumerate(item_qid_dict[item]):
                item_qid_dict[item][index] = qid_ratings_dict[qid]

        item_ratings_dict = item_qid_dict
        for item in item_ratings_dict.keys():
            item_ratings_dict[item] = self.get_weighted_average_rating(
                self.add_ratings(item_ratings_dict[item])
            )

        return item_ratings_dict
