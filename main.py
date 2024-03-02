import os
from dotenv import load_dotenv
from db_client import DatabaseClient
from scraper import NbaTeamScraper
from api_consumer import APIConsumer
from rest_backend import API

def main():
    isMock = False
    skip_fetch = True
    # Initialize the database client
    load_dotenv()
    mongo_uri = os.getenv('MONGODB_URI')
    db_client = DatabaseClient(mongo_uri)
    
    # Initialize the scraper
    scraper = NbaTeamScraper(isMock)
    if not skip_fetch:
        scraped_team_data = scraper.collect_nba_team_data()
        scraped_games = scraper.collect_nba_games()

        db_client.insert_nba_team_data("nba_teams", scraped_team_data)
        db_client.insert_nba_games("nba_games", scraped_games)

    # Initialize the API consumer
    api_consumer = APIConsumer("your_api_key")
    odds_data = api_consumer.fetch_odds("nba")
    # Use the fetched data as needed
    print(odds_data)

    # Initialize and run your API
    api = API(db_client)
    api.run()

if __name__ == "__main__":
    main()
