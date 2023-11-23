import os
from pymongo import MongoClient
from dotenv import load_dotenv


class Database:
    def __init__(self, connection_url: str) -> None:
        self.cluster0 = MongoClient(connection_url)

        self.CentralFoodDatabase = self.cluster0["CentralFoodDatabase"]
        self.foodMasterCollection = self.CentralFoodDatabase["foodMasterCollection"]

    def create_item(self, food_name: str) -> None:
        self.foodMasterCollection.insert_one(
            {
                "_id": food_name,
                "ratings": [],
            }
        )
        return

    def fetch_item(self, food_name: str) -> dict:
        if self.foodMasterCollection.find_one({"_id": food_name}) is None:
            self.create_item(food_name=food_name)
        return self.foodMasterCollection.find_one({"_id": food_name})

    def append_rating(self, food_name: str, rating: int) -> None:
        food_item = self.fetch_item(food_name=food_name)
        ratings: list = food_item["ratings"]
        ratings.append(rating)
        self.foodMasterCollection.update_one(
            {"_id": food_name}, {"$set": {"ratings": ratings}}
        )
        return

    def get_average_rating(self, food_name: str) -> None | float:
        food_item = self.fetch_item(food_name=food_name)
        ratings = food_item["ratings"]
        avg = sum(ratings) / len(ratings) if len(ratings) != 0 else None
        return avg

    def add_roster(self, item_rating_dict: dict) -> None:
        for key in item_rating_dict.keys():
            item = key
            rating = item_rating_dict[key]
            self.append_rating(food_name=item, rating=rating)

    def clear_everything(self) -> None:
        self.foodMasterCollection.delete_many({})
