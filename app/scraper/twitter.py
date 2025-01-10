from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from datetime import datetime
import uuid
import requests
import time
import pickle
import os
from app.database import get_db

class TwitterScraper:
    def __init__(self, twitter_username, twitter_password, proxy_username, proxy_password):
        self.twitter_username = twitter_username
        self.twitter_password = twitter_password
        self.proxy_auth = f"{proxy_username}:{proxy_password}" if proxy_username and proxy_password else None
        self.proxy_url = "http://proxymesh.com:31280"
        self.max_retries = 3
        self.retry_delay = 2
        self.cookies_file = f"twitter_cookies_{twitter_username}.pkl"

    def get_proxy(self):
        """Get proxy configuration"""
        if self.proxy_auth:
            return {
                'http': f'http://{self.proxy_auth}@{self.proxy_url}',
                'https': f'http://{self.proxy_auth}@{self.proxy_url}'
            }
        return None

    def get_current_ip(self):
        """Fetch current IP address with retry logic"""
        ip_services = [
            'https://api.ipify.org',
            'https://ip.seeip.org',
            'https://api.myip.com'
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
            except requests.RequestException:
                continue
        
        return "IP fetch failed"

    def setup_driver(self):
        """Setup and configure Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        proxy = self.get_proxy()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy["http"]}')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Additional settings to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def save_cookies(self, driver):
        """Save cookies to file"""
        try:
            pickle.dump(driver.get_cookies(), open(self.cookies_file, "wb"))
            return True
        except Exception:
            return False

    def load_cookies(self, driver):
        """Load cookies from file"""
        try:
            if os.path.exists(self.cookies_file):
                cookies = pickle.load(open(self.cookies_file, "rb"))
                for cookie in cookies:
                    driver.add_cookie(cookie)
                return True
        except Exception:
            pass
        return False

    def verify_login(self, driver):
        """Verify if we're actually logged in"""
        try:
            home_element = WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Home']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='AppTabBar_Home_Link']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
                )
            )
            
            if driver.find_elements(By.CSS_SELECTOR, "input[autocomplete='username']"):
                return False
                
            return True
        except TimeoutException:
            return False

    def login_twitter(self, driver):
        """Login to Twitter with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # First try loading saved cookies
                driver.get("https://twitter.com")
                if self.load_cookies(driver):
                    driver.refresh()
                    if self.verify_login(driver):
                        return True
                
                # If cookies didn't work, do full login
                driver.delete_all_cookies()
                driver.get("https://twitter.com/i/flow/login")
                time.sleep(3)
                
                # Enter username
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
                )
                username_field.clear()
                time.sleep(1)
                username_field.send_keys(self.twitter_username)
                time.sleep(1)
                
                # Click Next
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_button.click()
                time.sleep(2)
                
                # Enter password
                password_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                password_field.clear()
                time.sleep(1)
                password_field.send_keys(self.twitter_password)
                time.sleep(1)
                
                # Click Login
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
                )
                login_button.click()
                time.sleep(3)
                
                # Verify login success
                if self.verify_login(driver):
                    self.save_cookies(driver)
                    return True
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to login after {self.max_retries} attempts: {str(e)}")
                time.sleep(self.retry_delay)
                continue
        
        return False

    def get_trending_topics(self):
        """Get trending topics from Twitter"""
        driver = self.setup_driver()
        
        try:
            if not self.login_twitter(driver):
                raise Exception("Failed to maintain login session")
            
            time.sleep(5)
            driver.get("https://twitter.com/explore/tabs/trending")
            time.sleep(5)
            
            trend_texts = []
            
            for attempt in range(self.max_retries):
                try:
                    # Scroll to ensure content is loaded
                    driver.execute_script("window.scrollTo(0, 300)")
                    time.sleep(2)
                    
                    # Try multiple possible selectors for trends
                    possible_selectors = [
                        "div[data-testid='trend'] > div:nth-child(2) > span",  # Main trend text
                        "div[data-testid='trend'] span[dir='ltr']",           # Alternative trend text
                        "div[data-testid='cellInnerDiv'] div[dir='ltr']",     # Another possible structure
                        "div[data-testid='trend'] > div > div > div > span"    # Deeper nested structure
                    ]
                    
                    # Wait for any trend element to be present
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='trend']"))
                    )
                    
                    # Try each selector
                    for selector in possible_selectors:
                        try:
                            print(f"Trying selector: {selector}")  # Debug print
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            
                            for element in elements:
                                try:
                                    # Wait for element to be visible and get its text
                                    WebDriverWait(driver, 3).until(
                                        EC.visibility_of(element)
                                    )
                                    trend_text = element.text.strip()
                                    print(f"Found trend text: {trend_text}")  # Debug print
                                    
                                    # Validate trend text
                                    if (trend_text and 
                                        not trend_text.isdigit() and 
                                        trend_text not in ["Trending", "View Tweet"] and
                                        len(trend_text) > 1):
                                        trend_texts.append(trend_text)
                                except Exception as e:
                                    print(f"Error extracting individual trend: {str(e)}")  # Debug print
                                    continue
                            
                            # If we found valid trends, break out of selector loop
                            if trend_texts:
                                break
                                
                        except Exception as e:
                            print(f"Error with selector {selector}: {str(e)}")  # Debug print
                            continue
                    
                    # Remove duplicates while preserving order
                    trend_texts = list(dict.fromkeys(trend_texts))
                    
                    if len(trend_texts) >= 5:
                        break
                    else:
                        print(f"Not enough trends found ({len(trend_texts)}), retrying...")  # Debug print
                        time.sleep(self.retry_delay)
                        
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Failed to fetch trends: {str(e)}")
                    print(f"Attempt {attempt + 1} failed: {str(e)}")  # Debug print
                    time.sleep(self.retry_delay)
                    continue
            
            # Take only the first 5 unique trends
            trend_texts = trend_texts[:5]
            
            # Fill remaining slots if we don't have enough trends
            while len(trend_texts) < 5:
                trend_texts.append("No trend found")
            
            # Create record
            record = {
                "_id": str(uuid.uuid4()),
                "timestamp": datetime.now(),
                "ip_address": self.get_current_ip()
            }
            
            for i, trend in enumerate(trend_texts, 1):
                record[f"nameoftrend{i}"] = trend
            
            # Save to database
            get_db().trends.insert_one(record)
            return record
            
        except Exception as e:
            raise Exception(f"Scraping error: {str(e)}")
            
        finally:
            driver.quit()