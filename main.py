import csv
import json
import time
import traceback
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

t = 1
timeout = 10

debug = False

headless = False
images = False
maximize = False

incognito = False

headers = ['date', 'home_team', 'away_team', 'home_spread', 'away_spread', 'home_win', 'away_win', 'home_score',
           'away_score', 'quality', 'importance', 'overall']


def getForecast(driver, forecast=""):
    print(f"Getting {forecast} forecast...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    teams = []
    for section in soup.find('div', {"id": "completed-days"}).find_all('section', {"class": "day"}):
        date = section.find('h3', {"class": "h3"}).text
        # time = section.find("th", {"class": "th time"}).text
        for div in section.find_all("div", {"class": "game-body-wrap"}):
            td = div.find_all("td")
            team = {
                "date": date,
                "home_team": td[2].text,
                "away_team": td[9].text,
                "home_spread": td[3].text,
                "away_spread": td[10].text,
                "home_win": td[4].text,
                "away_win": td[11].text,
                "home_score": td[5].text,
                "away_score": td[12].text,
                "quality": div.find("td", {"class": "metric quality"}).find("div", {"class": "val"}).text,
                "importance": div.find("td", {"class": "metric swing"}).find("div", {"class": "val"}).text,
                "overall": div.find("td", {"class": "metric total"}).find("div", {"class": "val"}).text,
            }
            # print(json.dumps(team, indent=4))
            teams.append(team)
    with open(f"fivethirtyeight-{forecast}.csv", "w", newline='', encoding='utf8') as f:
        cfile = csv.DictWriter(f, fieldnames=headers)
        cfile.writeheader()
        cfile.writerows(teams)


def main():
    logo()
    driver = getChromeDriver()
    driver.get("https://projects.fivethirtyeight.com/2023-nba-predictions/games/")
    print("Loading more data...")
    click(driver, '//button[@id="js-complete-expander"]')
    time.sleep(5)
    getForecast(driver, "Raptor")
    print("Selecting Elo")
    click(driver,'//input[@data-value="elo"]',True)
    time.sleep(5)
    getForecast(driver, "Elo")


def pprint(msg):
    try:
        print(f"{datetime.now()}".split(".")[0], msg)
    except:
        traceback.print_exc()


def logo():
    print(rf"""
  _____.__              __  .__    .__         __                .__       .__     __   
_/ ____\__|__  __ _____/  |_|  |__ |__|_______/  |_ ___.__. ____ |__| ____ |  |___/  |_ 
\   __\|  \  \/ // __ \   __\  |  \|  \_  __ \   __<   |  |/ __ \|  |/ ___\|  |  \   __\
 |  |  |  |\   /\  ___/|  | |   Y  \  ||  | \/|  |  \___  \  ___/|  / /_/  >   Y  \  |  
 |__|  |__| \_/  \___  >__| |___|  /__||__|   |__|  / ____|\___  >__\___  /|___|  /__|  
                     \/          \/                 \/         \/  /_____/      \/      
==========================================================================================
            fivethirtyeight NBA Predictions Scraper by @evilgenius786
==========================================================================================
[+] Browser based
[+] Automated
__________________________________________________________________________________________
""")


def click(driver, xpath, js=False):
    if js:
        driver.execute_script("arguments[0].click();", getElement(driver, xpath))
    else:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def getElement(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))


def getElements(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))


def sendkeys(driver, xpath, keys, js=False):
    if js:
        driver.execute_script(f"arguments[0].value='{keys}';", getElement(driver, xpath))
    else:
        getElement(driver, xpath).send_keys(keys)


def getChromeDriver(proxy=None):
    options = webdriver.ChromeOptions()
    if debug:
        # print("Connecting existing Chrome for debugging...")
        options.debugger_address = "127.0.0.1:9222"
    else:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--user-data-dir=C:/Selenium1/ChromeProfile')
    if not images:
        # print("Turning off images to save bandwidth")
        options.add_argument("--blink-settings=imagesEnabled=false")
    if headless:
        # print("Going headless")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    if maximize:
        # print("Maximizing Chrome ")
        options.add_argument("--start-maximized")
    if proxy:
        # print(f"Adding proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")
    if incognito:
        # print("Going incognito")
        options.add_argument("--incognito")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def getFirefoxDriver():
    options = webdriver.FirefoxOptions()
    if not images:
        # print("Turning off images to save bandwidth")
        options.set_preference("permissions.default.image", 2)
    if incognito:
        # print("Enabling incognito mode")
        options.set_preference("browser.privatebrowsing.autostart", True)
    if headless:
        # print("Hiding Firefox")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    return webdriver.Firefox(options)


if __name__ == "__main__":
    main()
