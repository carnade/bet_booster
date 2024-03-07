import os
from dotenv import load_dotenv
from db_client import DatabaseClient
from scraper_espn import NbaTeamScraper_espn
from api_consumer import APIConsumer
from rest_backend import API
import threading
import schedule
import time
from functools import partial
from datetime import datetime


def scheduled_scrape(db_client, scraper, time):
    print(f"Running Schedule: {time}")
    scraped_team_data = scraper.collect_nba_team_data()
    db_client.insert_nba_team_data("nba_teams", scraped_team_data)
    scraped_games = scraper.collect_nba_games()
    db_client.insert_nba_games("nba_games", scraped_games)

def run_scheduler(db_client, scraper):
    print("Starting scheduler...")
    scheduled_task_0600 = partial(scheduled_scrape, db_client, scraper, "0600")
    scheduled_task_1600 = partial(scheduled_scrape, db_client, scraper, "1600")
    # Define the schedule for your tasks
    schedule.every().day.at("06:00").do(scheduled_task_0600)
    schedule.every().day.at("16:00").do(scheduled_task_1600)
    print("Scheduler set up, entering loop...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
def on_startup(db_client, scraper, skip_standings, skip_games, skip_results):
    if not skip_standings:
        print("Startup: Fetch standings")
        scraped_team_data = scraper.collect_nba_team_data()
        db_client.insert_nba_team_data("nba_teams", scraped_team_data)
    if not skip_games:
        print("Startup: Fetch games")
        scraped_games = scraper.collect_nba_games()
        db_client.insert_nba_games("nba_games", scraped_games)
    if not skip_results:
        print("Startup: Fetch results")
        scraped_results = scraper.collect_nba_results()
        db_client.insert_nba_results("nba_games", scraped_results)


def main():
    isMock = False
    skip_standings = False
    skip_games = False
    skip_results = False
    # Initialize the database client
    load_dotenv()
    mongo_uri = os.getenv('MONGODB_URI')
    db_client = DatabaseClient(mongo_uri)
    scraper = NbaTeamScraper_espn(isMock)
    on_startup(db_client, scraper, skip_standings, skip_games, skip_results)

    # Initialize the API consumer
    api_consumer = APIConsumer("your_api_key")
    odds_data = api_consumer.fetch_odds("nba")
    # Use the fetched data as needed
    print(odds_data)

    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=lambda: run_scheduler(db_client, scraper))
    scheduler_thread.daemon = True  # Allows the thread to be automatically killed when the main program exits
    scheduler_thread.start()

    # Initialize and run your API
    api = API(db_client)
    api.run()

if __name__ == "__main__":
    main()
