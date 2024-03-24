# This is a simplified version of what your DatabaseClient class might look like.
from pymongo import MongoClient
from datetime import datetime, timedelta
from pymongo.errors import PyMongoError
from helpers import calc_predicted_overunder

class DatabaseClient:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['bet_booster']

    def upsert_game(self, collection, date, game_data):
        document = collection.find_one({"date": date})

        if not document:
            # Document for the date does not exist, insert a new one
            #for game in game_data:
            collection.insert_one({"date": date, "games": game_data})
        else:
            # Document exists, check if game is in the "games" list
            for new_game in game_data:
                game_exists = False
                found_game = None
                for existing_game in document["games"]:
                    if existing_game["HomeTeam"] == new_game["HomeTeam"] and existing_game["AwayTeam"] == new_game["AwayTeam"]:
                            found_game = existing_game
                            game_exists = True
                            # Update the game data here
                            # Note: You'll need to manipulate the document['games'] list and update the specific game
                            break
                if game_exists:
                    if (found_game["HomeMoneyLineOdds"] != new_game["HomeMoneyLineOdds"]
                            or found_game["HomeHandicap"] != new_game["HomeHandicap"]
                            or found_game["OverUnder"] != new_game["OverUnder"]):
                        collection.update_one(
                            {"date": date},
                            {"$set": {
                                "games.$[elem].AwayMoneyLineOdds": new_game["AwayMoneyLineOdds"],
                                "games.$[elem].HomeMoneyLineOdds": new_game["HomeMoneyLineOdds"],
                                "games.$[elem].AwayHandicap": new_game["AwayHandicap"],
                                "games.$[elem].HomeHandicap": new_game["HomeHandicap"],
                                "games.$[elem].OverUnder": new_game["OverUnder"]
                            }},
                            array_filters=[{"elem.AwayTeam": found_game["AwayTeam"], "elem.HomeTeam": found_game["HomeTeam"]}]
                        )

                if not game_exists:
                    # Game does not exist, append to the "games" list
                    collection.update_one({"date": date}, {"$push": {"games": new_game}})

    def enrich_results_data(self, data, standings):
        data["predicted_OU"] = calc_predicted_overunder(standings, data["HomeTeam"], data["AwayTeam"])
        data["HTWinPct"] = round(
            float(standings[data["HomeTeam"]]["Wins"]) / float(standings[data["HomeTeam"]]["Games"]), 3)
        data["HTHomeWinPct"] = round(float(standings[data["HomeTeam"]]["Home"].split("-")[0]) /
                                     (float(standings[data["HomeTeam"]]["Home"].split("-")[0]) + float(
                                         standings[data["HomeTeam"]]["Home"].split("-")[1])), 3)
        data["ATWinPct"] = round(
            float(standings[data["AwayTeam"]]["Wins"]) / float(standings[data["AwayTeam"]]["Games"]), 3)
        data["ATAwayWinPct"] = round(float(standings[data["AwayTeam"]]["Away"].split("-")[0]) /
                                     (float(standings[data["AwayTeam"]]["Away"].split("-")[0]) + float(
                                         standings[data["AwayTeam"]]["Away"].split("-")[1])), 3)
        return data

    def insert_nba_team_data(self, collection_name, nba_data):
        collection = self.db[collection_name]
        for category, data in nba_data.items():
            collection.update_one({"category": category}, {"$set": {"teams": data}}, upsert=True)

    def insert_nba_games(self, collection_name, nba_data):
        collection = self.db[collection_name]
        date = datetime.now().strftime("%y%m%d")
        for date, data in nba_data.items():
            self.upsert_game(collection, date, data)
            #collection.update_one({"date": date}, {"$set": {"games": data}}, upsert=True)

    def insert_nba_results(self, collection_name, nba_data):
        collection = self.db[collection_name]
        standings = self.get_standings_nba()["teams"]
        for game_date in nba_data:
            for data in nba_data[game_date]:
                data = self.enrich_results_data(data,standings)
                try:
                    collection.update_one(
                        {"date": game_date, "games.HomeTeam": data["HomeTeam"]},
                        {"$set": {"games.$.results": data}},
                        upsert=True
                    )
                except PyMongoError as e:
                    print(f"An error occurred: {e}")
                    continue  # Skip the current iteration and continue with the next one

    def get_standings_nba(self):
        team_collection = self.db["nba_teams"]
        team_cursor = team_collection.find({"category": "total"})
        team_list = list(team_cursor)
        team_doc = team_list[0]
        # Since _id is an ObjectId, which is also not JSON serializable, you might need to convert it to string
        team_doc["_id"] = str(team_doc["_id"])
        return team_list[0]

    def get_games_nba(self, game_date=None):
        game_collection = self.db["nba_games"]
        if game_date is not None:
            game_cursor = game_collection.find({"date": game_date})
            game_list = list(game_cursor)
            games_doc = game_list[0]
            # Since _id is an ObjectId, which is also not JSON serializable, you might need to convert it to string
            games_doc["_id"] = str(games_doc["_id"])
        else:
            game_cursor = game_collection.find()
            games_doc = list(game_cursor)
            for game in games_doc:
                game["_id"] = str(game["_id"])
        return games_doc

    def get_results_nba(self, game_date):
        game_collection = self.db["nba_games"]
        game_cursor = game_collection.find({"date": game_date})
        game_list = list(game_cursor)
        game_doc = game_list[0]
        # Since _id is an ObjectId, which is also not JSON serializable, you might need to convert it to string
        game_doc["_id"] = str(game_doc["_id"])
        return game_doc

    def get_statistics_nba(self):
        result = {}
        game_collection = self.db["nba_games"]
        game_cursor = game_collection.find()
        game_list = list(game_cursor)
        standings = self.get_standings_nba()["teams"]
        all_games = [game for entry in game_list["games"] for game in entry['games']]
        result["games"] = game_list
        result["standings"] = standings
        return result