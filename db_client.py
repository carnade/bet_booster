# This is a simplified version of what your DatabaseClient class might look like.
from pymongo import MongoClient

class DatabaseClient:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['bet_booster']

    def insert_nba_team_data(self, collection_name, nba_data):
        collection = self.db[collection_name]
        for category, data in nba_data.items():
            collection.update_one({"category": category}, {"$set": {"teams": data}}, upsert=True)

    def insert_nba_games(self, collection_name, nba_data):
        collection = self.db[collection_name]
        for date, data in nba_data.items():
            collection.update_one({"date": date}, {"$set": {"games": data}}, upsert=True)

    def get_standings_nba(self):
        team_collection = self.db["nba_teams"]
        team_cursor = team_collection.find({"category": "total"})
        team_list = list(team_cursor)
        team_doc = team_list[0]
        # Since _id is an ObjectId, which is also not JSON serializable, you might need to convert it to string
        team_doc["_id"] = str(team_doc["_id"])
        l5_cursor = team_collection.find({"category": "last5"})
        l5_list = list(l5_cursor)
        for team in l5_list[0]["teams"]:
            team_doc["teams"][team]["l5_wins"] = l5_list[0]["teams"][team]["Wins"]
            team_doc["teams"][team]["l5_loss"] = l5_list[0]["teams"][team]["Losses"]
        return team_list[0]

    def get_games_nba(self, game_date):
        game_collection = self.db["nba_games"]
        game_cursor = game_collection.find({"date": game_date})
        game_list = list(game_cursor)
        game_doc = game_list[0]
        # Since _id is an ObjectId, which is also not JSON serializable, you might need to convert it to string
        game_doc["_id"] = str(game_doc["_id"])
        return game_doc
