import json
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BAHJobScraper:
    def __init__(self):
        self.base_url = "https://bah.wd1.myworkdayjobs.com"
        self.jobs_api_url = "https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/jobs"
        self.job_details_api_base = "https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs"
        self.session = requests.Session()
        
        # Headers for API requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs'
        })
    
    def make_request(self, url: str, method: str = 'GET', json_payload: Optional[dict] = None, retries: int = 3, delay: float = 1.0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and enhanced error handling"""
        for attempt in range(retries):
            try:
                logger.info(f"Attempting {method} request {attempt + 1}/{retries} for: {url}")
                
                if method.upper() == 'POST':
                    response = self.session.post(url, json=json_payload, timeout=30)
                else:
                    response = self.session.get(url, timeout=30)
                    
                response.raise_for_status()
                
                logger.info(f"Successful {method} request for: {url}")
                return response
                        
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1} for {url}")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limited on attempt {attempt + 1} for {url}")
                    time.sleep(delay * (3 ** attempt))  # Longer delay for rate limiting
                elif e.response.status_code in [403, 404]:
                    logger.error(f"Client error {e.response.status_code} for {url}")
                    return None  # Don't retry client errors
                else:
                    logger.warning(f"HTTP error {e.response.status_code} on attempt {attempt + 1} for {url}")
            except Exception as e:
                logger.warning(f"Unexpected error on attempt {attempt + 1} for {url}: {str(e)}")
            
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
        
        logger.error(f"All {retries} attempts failed for {url}")
        return None
    
    def get_job_listings(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get job listings from the Workday API"""
        logger.info(f"Fetching job listings: limit={limit}, offset={offset}")
        
        payload = {
            "appliedFacets": {},
            "limit": limit,
            "offset": offset,
            "searchText": ""
        }
        
        response = self.make_request(
            self.jobs_api_url, 
            method='POST', 
            json_payload=payload
        )
        
        if not response:
            logger.error("Failed to fetch job listings")
            return {"total": 0, "jobPostings": []}
        
        try:
            data = response.json()
            logger.info(f"Retrieved {len(data.get('jobPostings', []))} jobs from API")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            return {"total": 0, "jobPostings": []}
    
    def get_all_job_listings(self, max_jobs: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all job listings with pagination"""
        logger.info("Fetching all job listings")
        
        all_jobs = []
        offset = 0
        limit = 20  # API seems to have a max limit around 20
        
        while True:
            data = self.get_job_listings(limit=limit, offset=offset)
            
            if not data or not data.get('jobPostings'):
                break
            
            jobs = data.get('jobPostings', [])
            all_jobs.extend(jobs)
            
            total = data.get('total', 0)
            logger.info(f"Retrieved {len(all_jobs)} of {total} total jobs")
            
            # Stop if we've reached the limit or all jobs
            if max_jobs and len(all_jobs) >= max_jobs:
                all_jobs = all_jobs[:max_jobs]
                break
            
            if len(all_jobs) >= total or len(jobs) < limit:
                break
            
            offset += limit
            time.sleep(0.5)  # Be respectful to the API
        
        logger.info(f"Total jobs retrieved: {len(all_jobs)}")
        return all_jobs
    
    def get_job_details(self, job_path: str) -> Dict[str, Any]:
        """Get detailed job information from the job details API"""
        # Clean the path - remove leading slash if present
        clean_path = job_path.lstrip('/')
        full_url = f"{self.job_details_api_base}/{clean_path}"
        
        logger.info(f"Fetching job details from: {full_url}")
        
        response = self.make_request(full_url)
        if not response:
            logger.error(f"Failed to fetch job details from {full_url}")
            return {}
        
        try:
            data = response.json()
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode job details JSON: {e}")
            return {}
    
    def extract_job_details_from_api(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure job details from API response"""
        job_posting_info = job_data.get('jobPostingInfo', {})
        
        details = {
            'id': job_posting_info.get('id'),
            'title': job_posting_info.get('title'),
            'description': job_posting_info.get('jobDescription', ''),
            'location': job_posting_info.get('location'),
            'posted_date': job_posting_info.get('postedOn'),
            'start_date': job_posting_info.get('startDate'),
            'end_date': job_posting_info.get('endDate'),
            'job_id': job_posting_info.get('jobReqId'),
            'job_type': job_posting_info.get('timeType'),
            'external_url': job_posting_info.get('externalUrl'),
            'time_left_to_apply': job_posting_info.get('timeLeftToApply'),
            'can_apply': job_posting_info.get('canApply')
        }
        
        # Add location details if available
        job_location = job_posting_info.get('jobRequisitionLocation', {})
        if job_location:
            details['detailed_location'] = job_location.get('descriptor')
            country = job_location.get('country', {})
            if country:
                details['country'] = country.get('descriptor')
                details['country_code'] = country.get('alpha2Code')
        
        # Add hiring organization
        hiring_org = job_data.get('hiringOrganization', {})
        if hiring_org:
            details['hiring_organization'] = hiring_org.get('name')
            details['organization_url'] = hiring_org.get('url')
        
        # Clean up the description to extract structured information
        description = details.get('description', '')
        if description:
            details.update(self.parse_job_description(description))
        
        return {k: v for k, v in details.items() if v is not None and v != ''}
    
    def parse_job_description(self, description: str) -> Dict[str, Any]:
        """Parse structured information from job description HTML"""
        # Remove HTML tags for text analysis
        import re
        
        # Extract salary information
        salary_patterns = [
            r'\$[\d,]+(?:\.\d{2})?\s*(?:to|\-)\s*\$[\d,]+(?:\.\d{2})?',
            r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:annually|per year|\/year))?'
        ]
        
        salary_info = None
        for pattern in salary_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                salary_info = match.group(0)
                break
        
        # Extract clearance requirements
        clearance_patterns = [
            r'TS\/SCI(?:\s+with\s+(?:poly|polygraph))?',
            r'Top\s+Secret(?:\/SCI)?(?:\s+with\s+(?:poly|polygraph))?',
            r'Secret(?:\s+clearance)?',
            r'Public\s+Trust',
        ]
        
        clearance_info = None
        for pattern in clearance_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                clearance_info = match.group(0)
                break
        
        # Extract experience requirements
        exp_pattern = r'(\d+)\+?\s*years?\s+of\s+(?:experience|exp)'
        exp_match = re.search(exp_pattern, description, re.IGNORECASE)
        experience_years = exp_match.group(1) if exp_match else None
        
        parsed_info = {}
        if salary_info:
            parsed_info['salary_range'] = salary_info
        if clearance_info:
            parsed_info['security_clearance'] = clearance_info
        if experience_years:
            parsed_info['experience_years'] = experience_years
        
        return parsed_info
    
    def scrape_all_jobs(self, max_jobs: Optional[int] = None, include_details: bool = True) -> List[Dict[str, Any]]:
        """Main method to scrape all jobs with optional detailed information"""
        logger.info(f"Starting job scraping: max_jobs={max_jobs}, include_details={include_details}")
        
        # Get all job listings
        job_listings = self.get_all_job_listings(max_jobs=max_jobs)
        logger.info(f"Found {len(job_listings)} job listings")
        
        if not include_details:
            # Return basic job info only
            return [self.extract_basic_job_info(job) for job in job_listings]
        
        # Get detailed information for each job
        complete_jobs = []
        
        for i, job in enumerate(job_listings):
            try:
                logger.info(f"Processing job {i+1}/{len(job_listings)}: {job.get('title', 'Unknown')}")
                
                # Start with basic info
                basic_info = self.extract_basic_job_info(job)
                
                # Get detailed information
                if job.get('externalPath'):
                    job_details = self.get_job_details(job['externalPath'])
                    if job_details:
                        detailed_info = self.extract_job_details_from_api(job_details)
                        # Merge basic and detailed info
                        complete_job = {**basic_info, **detailed_info}
                        complete_jobs.append(complete_job)
                    else:
                        logger.warning(f"No details found for job: {job.get('title')}")
                        complete_jobs.append(basic_info)
                else:
                    logger.warning(f"No external path for job: {job.get('title')}")
                    complete_jobs.append(basic_info)
                
                # Add delay between requests to be respectful
                if i < len(job_listings) - 1:  # Don't delay after the last job
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Error processing job {job.get('title', 'Unknown')}: {str(e)}")
                # Still add the basic job info even if details fail
                basic_info = self.extract_basic_job_info(job)
                complete_jobs.append(basic_info)
        
        return complete_jobs
    
    def extract_basic_job_info(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic job information from job listing"""
        return {
            'title': job.get('title', ''),
            'location': job.get('locationsText', ''),
            'posted_date': job.get('postedOn', ''),
            'job_id': job.get('bulletFields', [None])[0],
            'external_path': job.get('externalPath', ''),
            'url': f"https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs{job.get('externalPath', '')}" if job.get('externalPath') else None
        }


def lambda_handler(event, context):
    """AWS Lambda handler function"""
    start_time = time.time()
    
    try:
        logger.info("Starting BAH job scraping")
        scraper = BAHJobScraper()
        
        # Extract any parameters from the event
        max_jobs = event.get('max_jobs', 100)  # Limit for testing/performance
        include_details = event.get('include_details', True)
        
        logger.info(f"Configuration: max_jobs={max_jobs}, include_details={include_details}")
        
        # Get comprehensive job data
        jobs_data = scraper.scrape_all_jobs(max_jobs=max_jobs, include_details=include_details)
        
        # Clean and validate the data
        cleaned_jobs = []
        for job in jobs_data:
            cleaned_job = clean_job_data(job)
            if cleaned_job:
                cleaned_jobs.append(cleaned_job)
        
        execution_time = round(time.time() - start_time, 2)
        
        response_body = {
            'success': True,
            'jobs_count': len(cleaned_jobs),
            'jobs': cleaned_jobs,
            'metadata': {
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                'execution_time_seconds': execution_time,
                'source_url': scraper.jobs_api_url,
                'include_details': include_details
            }
        }
        
        logger.info(f"Successfully scraped {len(cleaned_jobs)} jobs in {execution_time}s")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # For web access
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_body, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        execution_time = round(time.time() - start_time, 2)
        error_msg = str(e)
        
        logger.error(f"Lambda function error after {execution_time}s: {error_msg}", exc_info=True)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__,
                'jobs': [],
                'jobs_count': 0,
                'metadata': {
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                    'execution_time_seconds': execution_time,
                    'source_url': 'https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/jobs'
                }
            }, ensure_ascii=False, indent=2)
        }


def clean_job_data(job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Clean and validate job data before returning"""
    if not job or not job.get('title'):
        return None
    
    cleaned = {}
    
    # Required fields
    cleaned['title'] = job.get('title', '').strip()
    cleaned['url'] = job.get('url', '').strip()
    
    # Optional basic fields
    if job.get('location'):
        cleaned['location'] = str(job.get('location')).strip()
    if job.get('posted_date'):
        cleaned['posted_date'] = str(job.get('posted_date')).strip()
    if job.get('job_id'):
        cleaned['job_id'] = str(job.get('job_id')).strip()
    if job.get('job_type'):
        cleaned['job_type'] = str(job.get('job_type')).strip()
    
    # Detailed fields (if available)
    detail_fields = [
        'description', 'qualifications', 'responsibilities', 'benefits',
        'experience_level', 'department', 'salary_range'
    ]
    
    for field in detail_fields:
        if job.get(field):
            content = job[field].strip()
            if content and len(content) > 10:  # Only include meaningful content
                cleaned[field] = content
    
    # Add any additional automation-id fields
    for key, value in job.items():
        if key not in cleaned and isinstance(value, str) and value.strip():
            content = value.strip()
            if len(content) > 10 and not key.startswith('_'):
                cleaned[key] = content
    
    return cleaned if cleaned.get('title') else None


# For local testing
if __name__ == "__main__":
    # Test the function locally
    test_event = {}
    test_context = {}
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))
