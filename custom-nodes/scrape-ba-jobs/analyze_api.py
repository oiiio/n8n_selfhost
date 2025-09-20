#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

def analyze_workday_api():
    """Analyze Workday's API endpoints by examining network requests"""
    
    # Let's try to find the API endpoints by looking at common Workday patterns
    base_url = "https://bah.wd1.myworkdayjobs.com"
    tenant = "bah"
    site_id = "BAH_Jobs"
    
    # Common Workday API patterns
    api_endpoints_to_try = [
        f"/wday/cxs/{tenant}/{site_id}/jobs",
        f"/wday/cxs/{tenant}/{site_id}/job",
        f"/{tenant}/{site_id}/jobs",
        f"/{tenant}/{site_id}/job",
        f"/ccx/api/v1/{tenant}/{site_id}/jobs",
        f"/api/jobs/{tenant}/{site_id}",
        f"/wday/cxs/{tenant}/{site_id}/search",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    print("=== WORKDAY API ENDPOINT DISCOVERY ===\n")
    
    for endpoint in api_endpoints_to_try:
        full_url = base_url + endpoint
        print(f"Trying: {full_url}")
        
        try:
            response = session.get(full_url, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"  JSON Response Preview: {str(data)[:200]}...")
                        
                        # Save the full response for analysis
                        with open(f'api_response_{endpoint.replace("/", "_")}.json', 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"  Saved full response to: api_response_{endpoint.replace('/', '_')}.json")
                        
                    except json.JSONDecodeError:
                        print(f"  Invalid JSON response")
                elif 'html' in content_type:
                    print(f"  HTML response (length: {len(response.content)})")
                else:
                    print(f"  Other response type")
            
            elif response.status_code == 405:
                print("  Method not allowed - try POST?")
            elif response.status_code == 403:
                print("  Forbidden - might need authentication/CSRF token")
            elif response.status_code == 404:
                print("  Not found")
            else:
                print(f"  Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
        
        print()
        time.sleep(1)  # Be respectful
    
    # Try to find the actual API by examining the main page's JavaScript
    print("=== ANALYZING JAVASCRIPT FOR API ENDPOINTS ===\n")
    
    try:
        main_page = session.get("https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs")
        if main_page.status_code == 200:
            content = main_page.text
            
            # Look for API endpoints in the JavaScript
            api_patterns = [
                r'"/wday/cxs/[^"]*"',
                r'"/api/[^"]*"',
                r'"/ccx/[^"]*"',
                r'"https://[^"]*api[^"]*"',
                r'endpoint["\s]*:["\s]*[^"]+',
                r'apiUrl["\s]*:["\s]*[^"]+',
                r'jobsUrl["\s]*:["\s]*[^"]+',
            ]
            
            found_endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Clean up the match
                    clean_match = re.sub(r'["\s]', '', match)
                    if clean_match and len(clean_match) > 3:
                        found_endpoints.add(clean_match)
            
            if found_endpoints:
                print("Found potential API endpoints in JavaScript:")
                for endpoint in sorted(found_endpoints):
                    print(f"  - {endpoint}")
            else:
                print("No obvious API endpoints found in JavaScript")
                
            # Save the main page content for manual inspection
            with open('main_page_content.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Saved main page content to: main_page_content.txt")
                
    except Exception as e:
        print(f"Error analyzing JavaScript: {e}")

if __name__ == "__main__":
    analyze_workday_api()