#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

def examine_xml_endpoints():
    """Examine the XML endpoints that returned 200 status"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/xml,text/xml,*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs',
    }
    
    xml_endpoints = [
        "https://bah.wd1.myworkdayjobs.com/bah/BAH_Jobs/jobs",
        "https://bah.wd1.myworkdayjobs.com/bah/BAH_Jobs/job", 
        "https://bah.wd1.myworkdayjobs.com/api/jobs/bah/BAH_Jobs"
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    
    for url in xml_endpoints:
        print(f"\n=== EXAMINING: {url} ===")
        
        try:
            response = session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Try to parse as XML
                try:
                    root = ET.fromstring(response.content)
                    print(f"XML Root tag: {root.tag}")
                    print(f"XML attributes: {root.attrib}")
                    
                    # Look for job-related elements
                    job_elements = root.findall(".//job") + root.findall(".//posting") + root.findall(".//*[@*='job']")
                    print(f"Found {len(job_elements)} job-like elements")
                    
                    # Save the XML for inspection
                    filename = url.split('/')[-1] + '.xml'
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Saved XML to: {filename}")
                    
                    # Show a preview of the structure
                    xml_str = ET.tostring(root, encoding='unicode')
                    print(f"XML Preview (first 500 chars):\n{xml_str[:500]}...")
                    
                except ET.ParseError as e:
                    print(f"XML Parse Error: {e}")
                    # Maybe it's HTML disguised as XML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if soup.find('html'):
                        print("Content appears to be HTML, not XML")
                        print(f"Title: {soup.title.string if soup.title else 'No title'}")
                    else:
                        print("Content is not valid XML or HTML")
                        print(f"Raw content preview: {response.text[:200]}...")
                        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

def try_json_api_with_post():
    """Try making POST requests to the JSON API endpoints that returned 422/500"""
    
    print("\n\n=== TRYING POST REQUESTS TO JSON APIS ===")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs',
    }
    
    json_endpoints = [
        "https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/jobs",
        "https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/search"
    ]
    
    # Common Workday API request payloads
    payloads = [
        {},  # Empty payload
        {"limit": 20, "offset": 0},  # Pagination
        {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""},  # Search payload
        {"appliedFacets": {}, "limit": 20, "offset": 0},
        {"searchText": "", "limit": 20},
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    
    for url in json_endpoints:
        print(f"\nTrying POST to: {url}")
        
        for i, payload in enumerate(payloads):
            print(f"  Payload {i+1}: {payload}")
            
            try:
                response = session.post(url, json=payload, timeout=30)
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    Success! JSON response with {len(str(data))} chars")
                        
                        # Save successful response
                        filename = f"success_response_{url.split('/')[-1]}_{i}.json"
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"    Saved to: {filename}")
                        
                        # Show preview
                        print(f"    Preview: {str(data)[:300]}...")
                        
                        return  # Found working endpoint, stop here
                        
                    except json.JSONDecodeError:
                        print(f"    Response not JSON: {response.text[:100]}...")
                elif response.status_code == 422:
                    print("    Unprocessable Entity - wrong payload format")
                else:
                    print(f"    Error {response.status_code}: {response.text[:100]}...")
                    
            except requests.exceptions.RequestException as e:
                print(f"    Request failed: {e}")

if __name__ == "__main__":
    examine_xml_endpoints()
    try_json_api_with_post()