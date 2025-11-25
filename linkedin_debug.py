#!/usr/bin/python
# -*- coding: utf-8 -*-
# Debug script to see what's on LinkedIn's current HTML

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

EMAIL = os.getenv("EMAIL", '')
PASSWORD = os.getenv("PASSWORD", '')

print("Starting debug session...")

# Setup Chrome
try:
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    browser = webdriver.Chrome(service=service)
except:
    browser = webdriver.Chrome()

# Login
browser.get('https://linkedin.com/uas/login')
time.sleep(2)

emailElement = browser.find_element(By.ID, 'username')
emailElement.send_keys(EMAIL)
passElement = browser.find_element(By.ID, 'password')
passElement.send_keys(PASSWORD)
passElement.submit()

print('Signing in...')
time.sleep(5)

# Navigate to My Network
print("\nNavigating to My Network page...")
browser.get('https://www.linkedin.com/mynetwork/')
time.sleep(5)

# Save the page source for inspection
with open('linkedin_page_debug.html', 'w', encoding='utf-8') as f:
    f.write(browser.page_source)
print("✅ Saved page source to: linkedin_page_debug.html")

# Try to find links
soup = BeautifulSoup(browser.page_source, "html.parser")

print("\n" + "="*60)
print("DEBUGGING: Looking for profile links")
print("="*60)

# Check old selectors
print("\n1. Checking old selector: 'discover-entity-type-card__link'")
old_links = soup.find_all('a', class_='discover-entity-type-card__link')
print(f"   Found: {len(old_links)} links")

print("\n2. Checking for ANY links with '/in/' in href")
all_links = soup.find_all('a', href=True)
profile_links = [link for link in all_links if '/in/' in link.get('href', '')]
print(f"   Found: {len(profile_links)} profile links")
if profile_links:
    print("   First 5 examples:")
    for i, link in enumerate(profile_links[:5]):
        print(f"   - {link.get('href')}")
        print(f"     Classes: {link.get('class')}")

print("\n3. Looking for common link patterns")
patterns_to_check = [
    'app-aware-link',
    'discover-person-card',
    'mn-connection-card',
    'scaffold-finite-scroll__content',
    'entity-result__title-text',
]

for pattern in patterns_to_check:
    found = soup.find_all('a', class_=lambda x: x and pattern in x)
    if found:
        print(f"\n   ✓ Found {len(found)} links with class containing '{pattern}'")
        print(f"     Example: {found[0].get('href')}")
        print(f"     Full classes: {found[0].get('class')}")

print("\n" + "="*60)
print("Check 'linkedin_page_debug.html' for full page source")
print("="*60)

input("\nPress Enter to close browser...")
browser.quit()
