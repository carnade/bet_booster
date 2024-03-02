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

class NbaTeamScraper:
    def __init__(self, isMock):
        self.isMock = isMock

    def has_both_classes(self, tag):
        return "style_row__yBzX8" in tag.get("class", []) and "style_row__12oAB" in tag.get("class", [])

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
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
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
                        'AwayHandicap': market_values[0].find_all("span")[0].text.strip() if market_values[0].find_all("span") else "",
                        'HomeHandicap': market_values[1].find_all("span")[0].text.strip() if market_values[1].find_all("span") else "",
                        'AwayMoneyLineOdds': market_values[2].text.strip(),
                        'HomeMoneyLineOdds': market_values[3].text.strip(),
                        'OverUnder': market_values[4].find_all("span")[0].text.strip() if market_values[0].find_all("span") else "",
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
        recent_games = 5

        # Load the HTML content from the uploaded file
        data["total"] = self.fetch_team_data(0, self.isMock)
        sleep_time = randint(3, 6)
        print(f"Sleepin {sleep_time} secs")
        time.sleep(sleep_time)
        data[f"last{recent_games}"] = self.fetch_team_data(recent_games, self.isMock)

        #print(data)
        # Convert to DataFrame
        #df = pd.DataFrame(data)

        return data  # Just an example, you'd extract real data

    def fetch_team_data(self, games, mock):
        data = {}
        if mock:
            if games == 5:
                file_path = './bet_files/Teams Traditional _ Stats _ NBA.com Last5 (25_02_2024 10_26_38).html'
            else:
                file_path = './bet_files/Teams Traditional _ Stats _ NBA.com (24_02_2024 16_43_52).html'
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        else:
            url = f"https://www.nba.com/stats/teams/traditional?LastNGames={games}"
            '''print(f"Getting from {url}")
            response = requests.get(url)
            print(f"Got response code {response.status_code}")
            if response.status_code == 200:
                html_content = response.content'''
            # Initialize the WebDriver (example with Chrome)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
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

        # Find the tbody with the specified class
        tbody = soup.find('tbody', class_=re.compile(r'^Crom_body__'))


        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            team = tds[1].text.strip(),
            row_data = {
                'Games': tds[2].text.strip(),
                'Wins': tds[3].text.strip(),
                'Losses': tds[4].text.strip(),
                'PointsAvg': tds[7].text.strip(),
            }
            data[team[0]] = row_data

        sleep_time = randint(3, 6)
        print(f"Sleepin {sleep_time} secs")
        time.sleep(sleep_time)

        # https: // www.nba.com / stats / teams / opponent
        # https: // www.nba.com / stats / teams / opponent?LastNGames = 5
        if mock:
            if games == 5:
                file_path2 = './bet_files/Teams Opponent _ Stats _ NBA.com Last5 (25_02_2024 10_25_34).html'
            else:
                file_path2 = './bet_files/Teams Opponent _ Stats _ NBA.com (24_02_2024 16_57_09).html'
            with open(file_path2, 'r', encoding='utf-8') as file:
                html_content = file.read()
        else:
            url = f"https://www.nba.com/stats/teams/opponent?LastNGames={games}"
            '''response = requests.get(url)
            if response.status_code == 200:
                html_content = response.content'''
            # Initialize the WebDriver (example with Chrome)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
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
        soupOpp = BeautifulSoup(html_content, 'html.parser')

        # Find the tbody with the specified class
        tbody = soupOpp.find('tbody', class_=re.compile(r'^Crom_body__'))

        # Extract data
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            team = tds[1].text.strip(),
            row_data = {
                'OppReb': tds[7].text.strip(),
                'OppAss': tds[18].text.strip(),
                'OppSteal': tds[20].text.strip(),
                'OppBlock': tds[21].text.strip(),
                'OppPointsAvg': tds[25].text.strip(),
            }
            data.get(team[0]).update(row_data)

        return data
