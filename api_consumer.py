# Simplified APIConsumer class
import requests

class APIConsumer:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_odds(self, sport):
        # Placeholder for actual API call
        return f"Odds for {sport}"
