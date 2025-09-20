# BAH Jobs Scraper Lambda Function

This Lambda function scrapes job listings from Booz Allen Hamilton's careers page at `https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs` and returns comprehensive job data in JSON format.

## Features

- **Comprehensive Job Data**: Extracts both basic job information (title, location, URL) and detailed information from individual job pages
- **Pagination Support**: Automatically handles multiple pages of job listings
- **Detailed Job Information**: Extracts data from the `<section data-automation-id="jobDetails">` element including:
  - Job descriptions
  - Qualifications and requirements
  - Responsibilities
  - Benefits
  - Experience level
  - Department information
  - Salary ranges (when available)
- **Robust Error Handling**: Includes retry logic, timeout handling, and graceful degradation
- **Rate Limiting**: Respects the target website with appropriate delays between requests
- **Flexible Configuration**: Supports limiting job count and toggling detailed extraction

## Dependencies

- `requests==2.31.0` - HTTP requests
- `beautifulsoup4==4.12.2` - HTML parsing
- `lxml==4.9.3` - XML/HTML parser backend

## Lambda Configuration

### Required Settings
- **Handler**: `lambda_scrape_ba.lambda_handler`
- **Runtime**: Python 3.9 or later
- **Memory**: At least 512MB (recommended: 1024MB for better performance)
- **Timeout**: At least 5 minutes (300 seconds) - job scraping can take time
- **Permissions**: Only requires basic Lambda execution role (no special AWS permissions needed)

### Optional Environment Variables
You can set these as Lambda environment variables:
- `DEFAULT_MAX_JOBS`: Default limit for number of jobs to scrape (default: 100)
- `DEFAULT_INCLUDE_DETAILS`: Whether to include detailed job info by default (default: true)

## Usage

### Event Parameters
The Lambda function accepts the following optional parameters in the event:

```json
{
  "max_jobs": 50,
  "include_details": true
}
```

- `max_jobs` (int): Limit the number of jobs to return (useful for testing or performance)
- `include_details` (bool): Whether to scrape detailed job information from individual pages

### Response Format

```json
{
  "success": true,
  "jobs_count": 25,
  "jobs": [
    {
      "title": "Senior Software Engineer",
      "url": "https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs/job/...",
      "location": "McLean, VA",
      "posted_date": "2 days ago",
      "job_id": "R0123456",
      "description": "Full job description...",
      "qualifications": "Required qualifications...",
      "responsibilities": "Key responsibilities...",
      "benefits": "Benefits information...",
      "experience_level": "Senior Level",
      "department": "Technology",
      "job_type": "Full-time"
    }
  ],
  "metadata": {
    "scraped_at": "2025-09-19 10:30:00 UTC",
    "execution_time_seconds": 45.2,
    "source_url": "https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs",
    "include_details": true
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error description",
  "error_type": "RequestException",
  "jobs": [],
  "jobs_count": 0,
  "metadata": {
    "scraped_at": "2025-09-19 10:30:00 UTC",
    "execution_time_seconds": 12.5,
    "source_url": "https://bah.wd1.myworkdayjobs.com/en-US/BAH_Jobs"
  }
}
```

## Deployment

### Using the Deployment Script

1. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. Upload the generated `deployment/bah-job-scraper-lambda.zip` to your Lambda function.

### Manual Deployment

1. Install dependencies:
   ```bash
   pip install -r requirements.txt -t ./package
   ```

2. Copy the Lambda function to the package directory:
   ```bash
   cp lambda_scrape_ba.py ./package/
   ```

3. Create a ZIP file:
   ```bash
   cd package
   zip -r ../bah-job-scraper.zip .
   ```

4. Upload the ZIP file to AWS Lambda.

## Local Testing

You can test the function locally:

```python
python lambda_scrape_ba.py
```

This will run a test event and print the results.

## Performance Considerations

- **Execution Time**: Scraping detailed information can take 3-10 minutes depending on the number of jobs
- **Memory Usage**: 512MB is minimum, 1024MB recommended for better performance
- **Network Calls**: The function makes 1 request per job listing page + 1 request per job detail page
- **Rate Limiting**: Built-in delays prevent overwhelming the target server

## Notes

- The scraper is designed to be respectful of the target website with appropriate delays
- It handles common anti-scraping measures like rate limiting and connection errors
- The function will continue processing even if some individual jobs fail to scrape
- All extracted data is cleaned and validated before being returned

## Monitoring

Monitor these CloudWatch metrics:
- **Duration**: Should be under your timeout setting
- **Memory Usage**: Should stay under your allocated memory
- **Errors**: Check for timeout or memory limit errors
- **Throttles**: Indicates rate limiting issues

For production use, consider setting up CloudWatch alarms for these metrics.