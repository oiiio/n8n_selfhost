#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import time

def inspect_bah_jobs_page():
    """Inspect the actual BAH jobs page structure"""
    url = "https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content length: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save raw HTML for inspection
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("Saved raw HTML to: page_source.html")
        
        # Look for potential job-related elements
        print("\n=== ANALYZING PAGE STRUCTURE ===")
        
        # Check for common job listing patterns
        job_patterns = [
            ('div[data-automation-id*="job"]', 'Workday job automation IDs'),
            ('div[class*="job"]', 'Classes containing "job"'),
            ('li[class*="job"]', 'List items with job classes'),
            ('article', 'Article elements'),
            ('[data-automation-id]', 'All data-automation-id attributes'),
            ('[role="listitem"]', 'List item roles'),
            ('[role="link"]', 'Link roles'),
            ('a[href*="job"]', 'Links containing "job"'),
        ]
        
        for selector, description in job_patterns:
            elements = soup.select(selector)
            print(f"\n{description}: {len(elements)} found")
            if elements and len(elements) < 20:  # Only show details for manageable numbers
                for i, elem in enumerate(elements[:5]):  # Show first 5
                    print(f"  {i+1}. Tag: {elem.name}, Classes: {elem.get('class', [])}")
                    if elem.get('data-automation-id'):
                        print(f"     Automation ID: {elem.get('data-automation-id')}")
                    text_preview = elem.get_text(strip=True)[:100]
                    if text_preview:
                        print(f"     Text: {text_preview}...")
        
        # Look for specific Workday patterns
        print("\n=== WORKDAY-SPECIFIC ANALYSIS ===")
        workday_elements = soup.find_all(attrs={'data-automation-id': True})
        automation_ids = set()
        for elem in workday_elements:
            automation_ids.add(elem.get('data-automation-id'))
        
        print(f"Found {len(automation_ids)} unique data-automation-id values:")
        for aid in sorted(automation_ids):
            print(f"  - {aid}")
        
        # Check for pagination elements
        print("\n=== PAGINATION ANALYSIS ===")
        pagination_patterns = [
            ('button', 'Buttons'),
            ('a[href*="page"]', 'Links with page in href'),
            ('[class*="page"]', 'Elements with page in class'),
            ('[class*="next"]', 'Elements with next in class'),
            ('[class*="previous"]', 'Elements with previous in class'),
        ]
        
        for selector, description in pagination_patterns:
            elements = soup.select(selector)
            if elements:
                print(f"{description}: {len(elements)} found")
                for elem in elements[:3]:
                    print(f"  - {elem.name}: {elem.get('class', [])} - {elem.get_text(strip=True)[:50]}")
        
        # Check page title and main structure
        print(f"\n=== PAGE INFO ===")
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        main_content = soup.find('main') or soup.find('div', {'role': 'main'})
        if main_content:
            print(f"Main content found: {main_content.name} with classes: {main_content.get('class', [])}")
        
        print(f"\nInspection complete. Check 'page_source.html' for full HTML structure.")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_bah_jobs_page()