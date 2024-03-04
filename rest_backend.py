from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from db_client import DatabaseClient  # Adjust this import to your file structure

class API:
    def __init__(self, db_client):
        self.app = Flask(__name__)
        #CORS(self.app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
        CORS(self.app, origins="*")
        self.db_client = db_client  # Initialize your database class

    def setup_routes(self):
        @self.app.route('/standings/nba', methods=['GET'])
        def get_standings():
            print("Getting standings")
            try:
                # Assuming get_data method fetches data from your database
                data = self.db_client.get_standings_nba()
                teams_list = [{"Team": team, **info} for team, info in data["teams"].items()]
                return jsonify(teams_list), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/games/nba', methods=['GET'])
        def get_games():
            print("Getting games")
            try:
                today = datetime.now().strftime("%y%m%d")
                # Assuming get_data method fetches data from your database
                data_today = self.db_client.get_games_nba(today)
                for game in data_today["games"]:
                    game["Date"] = datetime.now().strftime("%y%m%d")
                    game["Game"] = f"{game['HomeTeam']} - {game['AwayTeam']}"
                try:
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
                    data_tomorrow = self.db_client.get_games_nba(tomorrow)
                    for game in data_tomorrow["games"]:
                        game["Date"] = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
                        game["Game"] = f"{game['HomeTeam']} - {game['AwayTeam']}"
                except Exception as e:
                    return jsonify(data_today), 200
                #merged_dict = {**data_today, **data_tomorrow}
                data_today.update(data_tomorrow)
                return jsonify(data_today), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/test-cors')
        def test_cors():
            return jsonify(message="CORS is working")

    def run(self):
        self.setup_routes()
        self.app.run(debug=False, host='0.0.0.0', port=6020)

'''
@app.route('/data', methods=['GET'])
def get_data():
    # This could be a call to a method in YourDatabaseClass that fetches data
    data = db.fetch_all_data()
    return jsonify(data)

@app.route('/data/<int:data_id>', methods=['GET'])
def get_data_by_id(data_id):
    # Fetch data by id or return 404 if not found
    data = db.fetch_data_by_id(data_id)
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404

# Additional routes can be added similarly for POST, PUT, DELETE operations

if __name__ == '__main__':
    app.run(debug=True)  # Starts the Flask web server
'''