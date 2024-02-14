from db_client import DatabaseClient
from scraper import NbaTeamScraper
from api_consumer import APIConsumer

def main():
    # Initialize the database client
    db_client = DatabaseClient("your_mongodb_uri")
    
    # Initialize the scraper
    scraper = NbaTeamScraper("http://example.com")
    scraped_data = scraper.fetch_data()
    # Here you would process scraped_data and then insert it into the database
    # db_client.insert_document("collection_name", processed_data)

    # Initialize the API consumer
    api_consumer = APIConsumer("your_api_key")
    odds_data = api_consumer.fetch_odds("nba")
    # Use the fetched data as needed
    print(odds_data)

if __name__ == "__main__":
    main()
