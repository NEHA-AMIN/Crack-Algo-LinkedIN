#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Matt Flood (Updated for Robust LinkedIn Selectors and Error Handling)

import os
import random
import time
import re
from urllib.parse import urlparse
from selenium import webdriver
import traceback
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from random import shuffle
from os.path import join, dirname
from dotenv import load_dotenv

# --- Configuration Loading ---
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Ensure credentials are read, with fallbacks for testing environment
EMAIL = os.getenv("EMAIL", '')
PASSWORD = os.getenv("PASSWORD", '')
if not EMAIL or not PASSWORD:
    try:
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not EMAIL:
            m = re.search(r"EMAIL\s*=\s*['\"]?([^'\"\s]+)['\"]?", content)
            if m: EMAIL = m.group(1)
        if not PASSWORD:
            m = re.search(r"PASSWORD\s*=\s*['\"]?([^'\"\n]+)['\"]?", content)
            if m: PASSWORD = m.group(1)
    except Exception:
        pass

# --- Constants ---
VIEW_SPECIFIC_USERS = False
SPECIFIC_USERS_TO_VIEW = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE = 5
CONNECT_WITH_USERS = True
RANDOMIZE_CONNECTING_WITH_USERS = True
JOBS_TO_CONNECT_WITH = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
ENDORSE_CONNECTIONS = False
RANDOMIZE_ENDORSING_CONNECTIONS = True
VERBOSE = True
TIMEOUT_SECONDS = 10 # Standard timeout for waiting for elements

# --- Core Functions ---

def Launch():
    """Launch the LinkedIn bot."""
    if not os.path.isfile('visitedUsers.txt'):
        with open('visitedUsers.txt', 'w') as f:
            f.write('') # Create empty file

    print('Choose your browser:')
    print('[1] Chrome')
    print('[2] Firefox/Iceweasel')
    print('[3] PhantomJS')

    while True:
        try:
            browserChoice = int(input('Choice? '))
            if browserChoice in [1, 2, 3]:
                break
            else:
                print('Invalid choice.')
        except ValueError:
            print('Invalid choice.')

    StartBrowser(browserChoice)


# def StartBrowser(browserChoice):
#     """Launch broswer, handle driver, and perform login."""
    
#     browser = None
    
#     try:
#         if browserChoice == 1:
#             print('\nLaunching Chrome')
#             # Use ChromeDriverManager for consistent driver management in a testing environment
#             driver_path = ChromeDriverManager().install()
#             service = Service(driver_path)
#             # Add option to ignore cert errors, common in test environments
#             options = webdriver.ChromeOptions()
#             options.add_argument('--ignore-certificate-errors')
#             browser = webdriver.Chrome(service=service, options=options)
#         elif browserChoice == 2:
#             print('\nLaunching Firefox/Iceweasel')
#             browser = webdriver.Firefox()
#         elif browserChoice == 3:
#             print('\nLaunching PhantomJS')
#             browser = webdriver.PhantomJS()
        
#         # Sign in
#         browser.get('https://linkedin.com/uas/login')
#         print('Navigated to login page.')
        
#         # Use WebDriverWait here for robust element finding
#         from selenium.webdriver.support.ui import WebDriverWait
#         from selenium.webdriver.support import expected_conditions as EC

#         WebDriverWait(browser, TIMEOUT_SECONDS).until(
#             EC.presence_of_element_located((By.ID, 'username'))
#         )
        
#         emailElement = browser.find_element(By.ID, 'username')
#         emailElement.send_keys(EMAIL)
#         passElement = browser.find_element(By.ID, 'password')
#         passElement.send_keys(PASSWORD)
#         passElement.submit()

#         print('Signing in... Waiting for redirect.')
#         time.sleep(5) # Increased sleep after submission

#         # --- Login Verification / Debugging ---
#         current_url = browser.current_url
#         current_title = browser.title
        
#         if 'error' in browser.page_source.lower() or 'incorrect' in browser.page_source.lower():
#             print('Error! Please verify your username and password.')
#             print(f"DEBUG URL: {current_url}")
#             browser.quit()
#         elif 'challenge' in current_url or 'security' in current_url:
#             print('Error! Stuck on a security challenge (e.g., CAPTCHA/MFA). Cannot proceed.')
#             print(f"DEBUG URL: {current_url}")
#             browser.quit()
#         elif current_title == '403: Forbidden':
#             print('LinkedIn is momentarily unavailable. Please wait a moment, then try again.')
#             browser.quit()
#         else:
#             print('Success! Login confirmed.')
#             print(f"DEBUG: Successfully landed on page: {current_title}")
            
#             # Navigate to the main workhorse function
#             LinkedInBot(browser)
            
#     except Exception as e:
#         print(f"\nCRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
#         traceback.print_exc()
#         if browser:
#             try:
#                 print(f"Final URL: {browser.current_url}")
#                 # Save a snapshot of the current page for debugging
#                 try:
#                     with open('startup_error_page.html', 'w', encoding='utf-8') as fh:
#                         fh.write(browser.page_source)
#                     print('Saved current page HTML to startup_error_page.html')
#                 except Exception as _e:
#                     print('Could not save page HTML:', _e)
#             except Exception:
#                 pass
#             try:
#                 browser.quit()
#             except Exception:
#                 pass
#         # Do not silently exit; re-raise so the caller sees the failure (or exit after logging)
#         sys.exit(1)

# def StartBrowser(browserChoice):
#     """Launch broswer, handle driver, and perform login."""
    
#     browser = None
    
#     try:
#         # ... (Browser launch setup remains the same) ...
#         if browserChoice == 1:
#             print('\nLaunching Chrome')
#             # Use ChromeDriverManager for consistent driver management
#             driver_path = ChromeDriverManager().install()
#             service = Service(driver_path)
#             options = webdriver.ChromeOptions()
#             options.add_argument('--ignore-certificate-errors')

#             # --- STABILIZED BOT-BYPASS OPTIONS ---
#             # 1. Disable the Infobars/Automated Control Message
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             # 2. Disable the Blink/Chrome Driver automation flag (critical for bot detection)
#             options.add_experimental_option('useAutomationExtension', False)
#             # 3. Add a standard User Agent
#             options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36")
#             # 4. CRITICAL: Force Chrome to use the system DNS resolver
#             options.add_argument('--enable-system-dns-host-resolver')
#             # 5. Disable the built-in DNS prefetcher (can cause issues with automation)
#             options.add_argument('--disable-dns-prefetching')

            
#             browser = webdriver.Chrome(service=service, options=options)
#         # ... (rest of the browser choices and sign-in logic remains the same) ...

#         # Sign in
#         browser.get('https://linkedin.com/uas/login')
#         print('Navigated to login page.')
        
#         # ... (Keep the rest of the login and WebDriverWait logic as is) ...
#         from selenium.webdriver.support.ui import WebDriverWait
#         from selenium.webdriver.support import expected_conditions as EC

#         WebDriverWait(browser, TIMEOUT_SECONDS).until(
#             EC.presence_of_element_located((By.ID, 'username'))
#         )
        
#         emailElement = browser.find_element(By.ID, 'username')
#         emailElement.send_keys(EMAIL)
#         passElement = browser.find_element(By.ID, 'password')
#         passElement.send_keys(PASSWORD)
#         passElement.submit()

#         print('Signing in... Waiting for redirect.')
        
#         # Wait for the search bar (or a stable element)
#         try:
#             WebDriverWait(browser, 20).until(
#                 EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"]'))
#             )
#             print("Successfully found Search Bar. Login confirmed and stable.")
#         except TimeoutException:
#             # Removed the print statement here to avoid confusion later
#             pass

#         # --- Login Verification / Debugging ---
#         current_url = browser.current_url
#         current_title = browser.title
        
#         # ⚠️ We must now remove the generic error check to prevent the false failure ⚠️
        
#         if 'challenge' in current_url or 'security' in current_url:
#             print('Error! Stuck on a security challenge (e.g., CAPTCHA/MFA). Cannot proceed.')
#             print(f"DEBUG URL: {current_url}")
#             browser.quit()
#         elif current_title == '403: Forbidden':
#             print('LinkedIn is momentarily unavailable. Please wait a moment, then try again.')
#             browser.quit()
#         else:
#             # If we reached the feed URL and didn't hit a challenge, assume success
#             print('Success! Login confirmed and Bot is proceeding.')
#             print(f"DEBUG: Successfully landed on page: {current_title}")
            
#             # Navigate to the main workhorse function
#             LinkedInBot(browser)
            
#     except Exception as e:
#         print(f"\nCRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
#         if browser:
#             print(f"Final URL: {browser.current_url}")
#             browser.quit()
#         import sys
#         sys.exit(1)
def StartBrowser(browserChoice):
    """Launch broswer, handle driver, and perform login."""
    
    browser = None
    
    try:
        if browserChoice == 1:
            print('\nLaunching Chrome')
            options = webdriver.ChromeOptions()
            options.add_argument('--ignore-certificate-errors')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36")
            options.add_argument('--enable-system-dns-host-resolver')
            options.add_argument('--disable-dns-prefetching')
            options.add_argument('--no-sandbox')

            try:
                browser = webdriver.Chrome(options=options)
            except Exception as _e1:
                possible_paths = [
                    '/usr/local/bin/chromedriver',
                    '/opt/homebrew/bin/chromedriver',
                    './chromedriver'
                ]
                chromepath = None
                for p in possible_paths:
                    if os.path.exists(p) and os.access(p, os.X_OK):
                        chromepath = p
                        break

                if chromepath:
                    service = Service(chromepath)
                    browser = webdriver.Chrome(service=service, options=options)
                else:
                    try:
                        driver_path = ChromeDriverManager().install()
                        service = Service(driver_path)
                        browser = webdriver.Chrome(service=service, options=options)
                    except Exception as _e2:
                        print('webdriver_manager failed:', _e2)
                        browser = webdriver.Chrome(options=options)
        
        # ... (Keep the rest of the login and WebDriverWait logic as is) ...
        
        # Sign in
        browser.get('https://linkedin.com/uas/login')
        print('Navigated to login page.')
        
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(browser, TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        
        emailElement = browser.find_element(By.ID, 'username')
        emailElement.send_keys(EMAIL)
        passElement = browser.find_element(By.ID, 'password')
        passElement.send_keys(PASSWORD)
        passElement.submit()

        print('Signing in... Waiting for redirect.')
        
        # Wait for the search bar (or a stable element)
        try:
            # Increased timeout to 25 seconds for network resilience
            WebDriverWait(browser, 25).until(
                EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"]'))
            )
            print("Successfully found Search Bar. Login confirmed and stable.")
        except TimeoutException:
            # Check for challenge pages here
            pass
        
        # ... (The Login Verification / Debugging logic remains the same) ...
        current_url = browser.current_url
        current_title = browser.title
        
        if 'challenge' in current_url or 'security' in current_url:
            print('Error! Stuck on a security challenge (e.g., CAPTCHA/MFA). Cannot proceed.')
            print(f"DEBUG URL: {current_url}")
            browser.quit()
        elif current_title == '403: Forbidden':
            print('LinkedIn is momentarily unavailable. Please wait a moment, then try again.')
            browser.quit()
        else:
            print('Success! Login confirmed and Bot is proceeding.')
            print(f"DEBUG: Successfully landed on page: {current_title}")
            
            LinkedInBot(browser)
            
    except Exception as e:
        print(f"\nCRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
        if browser:
            print(f"Final URL: {browser.current_url}")
            browser.quit()
        import sys
        sys.exit(1)

        # Sign in
        browser.get('https://linkedin.com/uas/login')
        print('Navigated to login page.')
        
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(browser, TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        
        emailElement = browser.find_element(By.ID, 'username')
        emailElement.send_keys(EMAIL)
        passElement = browser.find_element(By.ID, 'password')
        passElement.send_keys(PASSWORD)
        passElement.submit()

        print('Signing in... Waiting for redirect.')
        
        # --- NEW ROBUST WAIT CONDITION HERE ---
        # Wait for a stable element on the logged-in feed, such as the search bar
        try:
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"]'))
            )
            print("Successfully found Search Bar. Login confirmed.")
        except TimeoutException:
            print("WARNING: Timed out waiting for the homepage to load. Checking for errors...")


        # --- Login Verification / Debugging (The rest of the logic) ---
        current_url = browser.current_url
        current_title = browser.title
        
        if 'error' in browser.page_source.lower() or 'incorrect' in browser.page_source.lower():
            print('Error! Please verify your username and password.')
            print(f"DEBUG URL: {current_url}")
            browser.quit()
        elif 'challenge' in current_url or 'security' in current_url:
            print('Error! Stuck on a security challenge (e.g., CAPTCHA/MFA). Cannot proceed.')
            print(f"DEBUG URL: {current_url}")
            browser.quit()
        elif current_title == '403: Forbidden':
            print('LinkedIn is momentarily unavailable. Please wait a moment, then try again.')
            browser.quit()
        else:
            print('Success! Login confirmed.')
            print(f"DEBUG: Successfully landed on page: {current_title}")
            
            # Navigate to the main workhorse function
            LinkedInBot(browser)
            
    except Exception as e:
        print(f"\nCRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
        if browser:
            print(f"Final URL: {browser.current_url}")
            browser.quit()
        import sys
        sys.exit(1) # Ensure process exits after failure

def LinkedInBot(browser):
    """Run the main LinkedIn Bot logic."""

    T = 0 # Total pages loaded
    V = 0 # Unique profiles viewed
    profilesQueued = []
    error403Count = 0
    timer = time.time()

    # Wrap the entire logic in a try-except to catch unexpected runtime errors
    try:
        if ENDORSE_CONNECTIONS:
            EndorseConnections(browser)

        print('At the my network page to scrape user urls..\n')

        # --- Main Looping Logic ---
        while True:
            try:
                # 1. Scrape new URLs from the network page
                NavigateToMyNetworkPage(browser)
                T += 1

                soup = BeautifulSoup(browser.page_source, "html.parser")
                profilesQueued.extend(GetNewProfileURLS(soup, profilesQueued))
                profilesQueued = list(set(profilesQueued))
                
                if not profilesQueued:
                    print('|', end='', flush=True) # Indicate scraping in progress
                    time.sleep(random.uniform(5, 7))
                    continue # Try scraping again
                else:
                    break # Got initial queue, proceed

            except Exception as e:
                print(f"\n[ERROR] Scraping failed on Network Page. Retrying in 10s. Error: {type(e).__name__}: {e}")
                time.sleep(10)
                continue

        V += 1
        print('\n\nGot our users to start viewing with! Total in Queue:', len(profilesQueued), '\n')

        # 2. Iterate and visit profiles
        while profilesQueued:
            try:
                shuffle(profilesQueued)
                profileID = profilesQueued.pop()
                # Pause BEFORE navigating to the profile to avoid rapid-fire navigation
                time.sleep(random.uniform(7, 12))
                browser.get('https://www.linkedin.com'+profileID)
                # Wait for the profile to load
                time.sleep(random.uniform(3, 5))

                # Connect with users
                if CONNECT_WITH_USERS:
                    if not RANDOMIZE_CONNECTING_WITH_USERS or random.choice([True, False]):
                        ConnectWithUser(browser)

                # Log to visitedUsers.txt
                with open('visitedUsers.txt', 'a') as visitedUsersFile:
                    visitedUsersFile.write(str(profileID)+'\r\n')

                # Get new profiles ID from 'People Also Viewed'
                soup = BeautifulSoup(browser.page_source, "html.parser")
                profilesQueued.extend(GetNewProfileURLS(soup, profilesQueued))
                profilesQueued = list(set(profilesQueued))

                # Display info
                browserTitle = browser.title.replace(' | LinkedIn', '').encode('ascii', 'ignore')
                T += 1
                error403Count = 0
                print(f"{browserTitle.decode()} visited. T: {T} | V: {V} | Q: {len(profilesQueued)}")

                # Pause/Timer Logic
                if (T % 1000 == 0) or time.time()-timer > 3600:
                    print('\nPaused for 1 hour\n')
                    time.sleep(3600 + random.randrange(0, 10) * 60)
                    timer = time.time()
                else:
                    # Increase post-visit delay to reduce request rate and DNS issues
                    time.sleep(random.uniform(7, 10))
            
            except StaleElementReferenceException:
                print("\n[WARNING] Stale element, likely due to page dynamic loading. Skipping this iteration.")
            except NoSuchElementException as e:
                print(f"\n[WARNING] Element not found on profile. Continuing. Error: {e}")
            except WebDriverException as e:
                _title = ''
                try:
                    _title = browser.title
                except Exception:
                    _title = ''
                if '403 Forbidden' in _title or '403' in str(e):
                    error403Count += 1
                    print(f'\nLinkedIn is momentarily unavailable - Paused for {error403Count} hour(s)\n')
                    time.sleep(3600*error403Count + random.randrange(0, 10) * 60)
                    timer = time.time()
                else:
                    print(f"\n[ERROR] WebDriver exception on profile page. Skipping. Error: {e}")
            except Exception as e:
                print(f"\n[CRITICAL ERROR] Unknown error in main loop: {type(e).__name__}: {e}. Stopping profile queue.")
                break


        print('\nNo more profiles to visit. Everything restarts with the network page...\n')

    except Exception as e:
        print("\nCRITICAL BOT FAILURE: An unexpected error occurred in LinkedInBot.")
        print(f"Error Details: {type(e).__name__}: {e}")
        traceback.print_exc()
        try:
            print(f"Current URL at failure: {browser.current_url}")
            with open('bot_error_page.html', 'w', encoding='utf-8') as fh:
                fh.write(browser.page_source)
            print('Saved current page HTML to bot_error_page.html')
        except Exception as _ex:
            print('Could not capture current page or URL:', _ex)
        try:
            browser.quit()
        except Exception:
            pass


def NavigateToMyNetworkPage(browser):
    """
    Navigate to the my network page and scroll to the bottom.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    browser.get('https://www.linkedin.com/mynetwork/')
    print(f"Navigated to {browser.current_url}")
    
    # Wait for the network card content to load using a very general structural selector
    try:
        WebDriverWait(browser, TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.TAG_NAME, 'section'))
        )
    except TimeoutException:
        print("[WARNING] Timeout waiting for network page to load. Proceeding with scroll...")
        pass

    for counter in range(1, NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE + 1):
        if VERBOSE:
            print(f"Scrolling down... ({counter}/{NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE})")
        ScrollToBottomAndWaitForLoad(browser)


def ConnectWithUser(browser):
    """
    Connect with the user viewing if their job title is found in your list of roles.
    Uses robust selectors for the Connect button and job title extraction.
    """
    
    soup = BeautifulSoup(browser.page_source, "html.parser")
    jobTitleMatches = False
    current_job_title = "N/A"

    # 1. Try to find the job title using structural selectors
    try:
        # Target the top card where the job title is usually located (often an H2 or DIV near the name)
        # Using a broad XPath to find the second line of text in the profile header.
        job_title_element = browser.find_element(
            By.XPATH, 
            '//div[contains(@class, "pv-top-card")]//div[contains(@class, "text-body-medium")] | //h2[contains(@class, "top-card-layout__entity-info")]'
        )
        current_job_title = job_title_element.text.strip()
    except:
        pass

    if current_job_title != "N/A":
        for job in JOBS_TO_CONNECT_WITH:
            if job.upper() in current_job_title.upper():
                jobTitleMatches = True
                break

    if jobTitleMatches:
        try:
            if VERBOSE:
                print(f'Job Match: "{current_job_title}". Sending connection invitation.')

            # 2. Locate and click the Connect button (using ARIA or text)
            # Find a button that says 'Connect' or 'Invite' AND is a primary action button
            connect_button = browser.find_element(
                By.XPATH, 
                '//button[(contains(., "Connect") or contains(., "Invite")) and contains(@class, "artdeco-button--primary")]'
            )
            connect_button.click()
            time.sleep(random.uniform(2, 3))
            
            # 3. Locate and click the Send button in the modal
            # Find the primary button in the modal that says 'Send'
            send_button = browser.find_element(
                By.XPATH, 
                '//div[@role="dialog"]//button[contains(@class, "artdeco-button--primary") and (contains(., "Send") or contains(., "Done"))]'
            )
            send_button.click()
            
            if VERBOSE:
                 print('... Invitation Sent.')
            time.sleep(random.uniform(3, 5))
            
        except NoSuchElementException:
            if VERBOSE:
                print('... Connection button not found (already connected, pending, or "Follow" only).')
        except Exception as e:
            if VERBOSE:
                print(f'... Connection attempt failed unexpectedly: {type(e).__name__}: {e}')
            pass


def GetNewProfileURLS(soup, profilesQueued):
    """
    Get new profile urls to add to the navigate queue.
    """
    with open('visitedUsers.txt', 'r') as visitedUsersFile:
        visitedUsers = {line.strip() for line in visitedUsersFile}

    profileURLS = []
    
    # Use a broad search for profile links across the page
    for a in soup.find_all('a', href=re.compile(r'/in/')): 
        raw = a['href']
        url = urlparse(raw).path
        if ValidateURL(url, profileURLS, profilesQueued, visitedUsers):

            if VIEW_SPECIFIC_USERS:
                # This logic is kept for completeness but is the most fragile part of scraping
                parent_text = a.parent.get_text().lower() if a.parent else ''
                is_match = False
                for occupation in SPECIFIC_USERS_TO_VIEW:
                    if occupation.lower() in parent_text:
                        is_match = True
                        break
                        
                if is_match:
                    if VERBOSE:
                        print(f"Scrape Match: {url}")
                    profileURLS.append(url)
            else:
                profileURLS.append(url)
    
    return list(set(profileURLS))


def ValidateURL(url, profileURLS, profilesQueued, visitedUsers):
    """
    Validate the url meets requirement to be navigated to.
    """
    # Clean and normalize the URL (remove query params)
    url = urlparse(url).path
    
    return (
        url not in profileURLS and 
        url not in profilesQueued and 
        url not in visitedUsers and
        "/in/" in url and 
        "connections" not in url and 
        "skills" not in url and
        "/feed" not in url and
        "/sales" not in url
    )


def EndorseConnections(browser):
    """
    Endorse skills for your connections found.
    Uses stable selector for the Endorse button.
    """
    print("Gathering your connections url's to endorse their skills.")
    profileURLS = []
    
    try:
        browser.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
        time.sleep(5)

        for counter in range(1, NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE + 1):
            ScrollToBottomAndWaitForLoad(browser)
        
        soup = BeautifulSoup(browser.page_source, "html.parser")
        
        # Look for profile links in the connections list.
        for a in soup.find_all('a', href=re.compile(r'/in/')):
            raw = a['href']
            url = urlparse(raw).path
            if ValidateURL(url, [], [], []): 
                profileURLS.append(url)

        print(f"Found {len(profileURLS)} connections to endorse.")

        for url in profileURLS:
            if not RANDOMIZE_ENDORSING_CONNECTIONS or random.choice([True, False]):
                fullURL = 'https://www.linkedin.com'+url
                if VERBOSE:
                    print(f'Visiting {fullURL}')

                browser.get(fullURL)
                time.sleep(5)
                
                # Use data-control-name or a descriptive ARIA label for stability
                endorse_buttons = browser.find_elements(
                    By.XPATH, 
                    '//button[@data-control-name="endorse" or contains(@aria-label, "Endorse")]'
                )
                
                for button in endorse_buttons:
                    try:
                        # Check if the button is already active/endorsed to avoid unnecessary clicks
                        if 'Endorse' in button.text and 'aria-checked="false"' in button.get_attribute('outerHTML'):
                            button.click()
                            time.sleep(random.uniform(0.5, 1.5))
                    except Exception as e:
                        if VERBOSE:
                            print(f"Could not click endorse button on {url}: {e}")
                        continue
                        
            time.sleep(random.uniform(3, 5))
            
    except Exception as e:
        print(f'\nException occurred when endorsing connections: {type(e).__name__}: {e}')
        pass

    print('\nEndorsement process finished.')


def ScrollToBottomAndWaitForLoad(browser):
    """
    Scroll to the bottom of the page and wait for lazy loading.
    """
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)


if __name__ == '__main__':
    Launch()