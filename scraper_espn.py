# Simplified Scraper class
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from random import randint
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.firefox.options import Options

class NbaTeamScraper_espn:
    def __init__(self, isMock):
        self.isMock = isMock

    def has_both_classes(self, tag):
        return "style_row__yBzX8" in tag.get("class", []) and "style_row__12oAB" in tag.get("class", [])

    def perform_action_on_element(self, lst, index, action):
        if index < len(lst) and lst[index] is not None:
            element = lst[index]
            # Ensure 'action' is callable before attempting to call it
            if callable(action):
                return action(element)
        return None

    def safe_extract_text(self, element):
        """
        Safely extract text from the specified BeautifulSoup element.
        Checks if the element and the <span> tag within it exist.
        """
        if element and element.find("span", class_="style_price__3Haa9"):
            return element.find("span", class_="style_price__3Haa9").text.strip()
        return None

    def get_text_from_span(self, element, idx):
        spans = element.find_all("span")
        if spans and len(spans) > idx:
            return spans[idx].text.strip()
        return ""

    def collect_nba_games(self):
        data = {}

        if self.isMock:
            #file_path = './bet_files/Odds på Basket _ Spel på Basket (25_02_2024 18_13_02).html'
            file_path = './bet_files/Odds på Basket _ Spel på Basket (26_02_2024 19_37_48).html'
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        else:
            url = "https://www.pinnacle.se/sv/basketball/nba/matchups#period:0"
            '''print(f"Getting from {url}")
            response = requests.get(url)
            print(f"Got response code {response.status_code}")
            if response.status_code == 200:
                html_content = response.content
            '''
            # Initialize the WebDriver (example with Chrome)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')  # Disabling extensions can save resources
            chrome_options.add_argument('--disable-plugins')  # Disable plugins
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")  # Increase verbosity
            chrome_options.add_argument("--log-level=0")  # Log all levels
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
            prefs = {
                'profile.managed_default_content_settings.images': 2,
                'profile.managed_default_content_settings.stylesheets': 2,
                'profile.managed_default_content_settings.javascript': 2,
            }
            chrome_options.add_experimental_option('prefs', prefs)
            # Initialize the WebDriver with the specified options
            driver = webdriver.Chrome(options=chrome_options)

            # Set the viewport size to match your desktop browser
            driver.set_window_size(2560, 1440)

            print(f"Getting: {url}")
            driver.get(url)
            #time.sleep(6)
            driver.implicitly_wait(20)  # Waits for 10 seconds
            html_content = driver.page_source
            driver.quit()
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        date_elements = soup.find_all("div", class_="style_dateBar__1adEH")

        for date_element in date_elements:
            # Extract the date
            date = date_element.get_text(strip=True)

            # Find all next siblings until the next date element
            rows = []
            next_sibling = date_element.find_next_sibling()


            while next_sibling and "style_dateBar__1adEH" not in next_sibling.get("class", ""):
                if next_sibling and self.has_both_classes(next_sibling):
                    team_names = next_sibling.find_all("span", class_="ellipsis event-row-participant style_participant__2BBhy")
                    # Extract the text for each team name
                    teams = [name.get_text(strip=True) for name in team_names]
                    cleaned_teams = [' '.join(team.split()) for team in teams]
                    # Find all market values within the row
                    market_values = next_sibling.find_all("button", class_="market-btn style_button__G9pbN style_pill__2U30o style_vertical__2J4sL")
                    row_data = {
                        'AwayTeam': cleaned_teams[0].strip(),
                        'HomeTeam': cleaned_teams[1].strip(),
                        'AwayHandicap': self.perform_action_on_element(market_values, 0, lambda element: self.get_text_from_span(element, 0)),
                        'HomeHandicap': self.perform_action_on_element(market_values, 1, lambda element: self.get_text_from_span(element, 0)),
                        'AwayMoneyLineOdds': self.perform_action_on_element(market_values, 2, self.safe_extract_text),
                        'HomeMoneyLineOdds': self.perform_action_on_element(market_values, 3, self.safe_extract_text),
                        'OverUnder': self.perform_action_on_element(market_values, 4, lambda element: self.get_text_from_span(element, 0)),
                    }
                    rows.append(row_data)
                next_sibling = next_sibling.find_next_sibling()

            if "Idag" in date:
                formatted_date = datetime.now().strftime("%y%m%d")
            elif "Imorgon" in date:
                formatted_date = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
            else:
                formatted_date = "Unknown"

            data[formatted_date] = rows
        return data


    def collect_nba_team_data(self):
        data = {}

        # Load the HTML content from the uploaded file
        data["total"] = self.fetch_team_data(self.isMock)
        sleep_time = randint(3, 6)
        print(f"Sleepin {sleep_time} secs")
        time.sleep(sleep_time)

        #print(data)
        # Convert to DataFrame
        #df = pd.DataFrame(data)

        return data  # Just an example, you'd extract real data

    def fetch_team_data(self, mock):
        data = {}
        if mock:
            file_path = './bet_files/NBA Standings - 2023-24 Regular Season League Standings - ESPN (03_03_2024 20_40_08).html'
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        else:
            url = f"https://www.espn.com/nba/standings/_/group/league"
            # Initialize the WebDriver (example with Chrome)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')  # Disabling extensions can save resources
            chrome_options.add_argument('--disable-plugins')  # Disable plugins
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")  # Increase verbosity
            chrome_options.add_argument("--log-level=0")  # Log all levels
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
            prefs = {
                'profile.managed_default_content_settings.images': 2,
                'profile.managed_default_content_settings.stylesheets': 2,
                'profile.managed_default_content_settings.javascript': 2,
            }
            chrome_options.add_experimental_option('prefs', prefs)
            # Initialize the WebDriver with the specified options
            driver = webdriver.Chrome(options=chrome_options)

            # Set the viewport size to match your desktop browser
            driver.set_window_size(1920, 1080)

            print(f"Getting: {url}")
            driver.get(url)
            #time.sleep(6)
            driver.implicitly_wait(20)  # Waits for 10 seconds
            html_content = driver.page_source
            driver.quit()

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'lxml')

        # Find all the 'tbody' tags with class 'Table__TBODY'
        tbodies = soup.find_all("tbody", class_="Table__TBODY")

        # Extract team names from the first 'tbody'
        team_names = []
        if tbodies and len(tbodies) > 0:
            team_names = [abbr.get("title") for abbr in tbodies[0].find_all("abbr", title=True)]

        # Extract team stats from the second 'tbody'
        team_stats = []
        if len(tbodies) > 1:
            for tr in tbodies[1].find_all("tr"):
                stats = [span.text for span in tr.find_all("span", class_="stat-cell")]
                team_stats.append(stats)

        # Combine team names with their stats
        for name, stats in zip(team_names, team_stats):
            row_data = {
                "Team": name,
                'Games': int(stats[0]) + int(stats[1]),
                'Wins': stats[0],
                'Losses': stats[1],
                'Home': stats[4],
                'Away': stats[5],
                'PPG': stats[8],
                'OPPG':stats[9],
                'STRK':stats[11],
                'L10': stats[12]
            }
            data[name] = row_data
        return data
