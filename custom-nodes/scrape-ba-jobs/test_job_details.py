#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup

def test_job_details():
    """Test accessing individual job details"""
    
    # Load the job listings to get a sample job path
    with open('success_response_jobs_0.json', 'r') as f:
        data = json.load(f)
    
    sample_job = data['jobPostings'][0]
    job_path = sample_job['externalPath']
    
    print(f"Testing job details for: {sample_job['title']}")
    print(f"Job path: {job_path}")
    
    # Try different ways to access job details
    base_url = "https://bah.wd1.myworkdayjobs.com"
    
    urls_to_try = [
        f"{base_url}{job_path}",
        f"{base_url}/en-US/BAH_Jobs{job_path}",
        f"{base_url}/wday/cxs/bah/BAH_Jobs{job_path}",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    for url in urls_to_try:
        print(f"\nTrying: {url}")
        
        try:
            response = session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Check if it's the SPA loading page or actual content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for the job details section
                job_details_section = soup.find('section', {'data-automation-id': 'jobDetails'})
                if job_details_section:
                    print("✅ Found jobDetails section!")
                    print(f"Section content length: {len(job_details_section.get_text())}")
                    
                    # Save the job details page
                    with open('job_details_page.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    print("Saved job details page to: job_details_page.html")
                    
                    # Extract some basic info
                    title_elem = job_details_section.find('h1')
                    if title_elem:
                        print(f"Job title from details: {title_elem.get_text(strip=True)}")
                    
                    return True
                    
                elif soup.find('div', {'id': 'root'}):
                    print("⚠️  Found SPA root div - content loads dynamically")
                    
                else:
                    print("❌ No jobDetails section found")
                    # Show what we did find
                    print(f"Page title: {soup.title.string if soup.title else 'No title'}")
                    
                    # Look for any data-automation-id elements
                    automation_elements = soup.find_all(attrs={'data-automation-id': True})
                    if automation_elements:
                        print(f"Found {len(automation_elements)} elements with data-automation-id")
                        for elem in automation_elements[:5]:
                            print(f"  - {elem.get('data-automation-id')}: {elem.get_text(strip=True)[:50]}...")
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
    
    return False

def test_pagination():
    """Test pagination with the jobs API"""
    
    print("\n\n=== TESTING PAGINATION ===")
    
    url = "https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/jobs"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # Test different pagination payloads
    payloads = [
        {"limit": 20, "offset": 0},  # First page
        {"limit": 20, "offset": 20},  # Second page
        {"limit": 50, "offset": 0},   # Larger page size
    ]
    
    for i, payload in enumerate(payloads):
        print(f"\nTesting payload {i+1}: {payload}")
        
        try:
            response = session.post(url, json=payload, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Total jobs: {data.get('total', 'N/A')}")
                print(f"Jobs returned: {len(data.get('jobPostings', []))}")
                
                if data.get('jobPostings'):
                    first_job = data['jobPostings'][0]
                    print(f"First job: {first_job.get('title', 'N/A')} (ID: {first_job.get('bulletFields', ['N/A'])[0] if first_job.get('bulletFields') else 'N/A'})")
                
                # Save response for analysis
                filename = f"pagination_test_{i+1}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to: {filename}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    found_details = test_job_details()
    
    if not found_details:
        print("\n⚠️  Job details pages also load dynamically. Will need to use Selenium or find a details API.")
    
    test_pagination()