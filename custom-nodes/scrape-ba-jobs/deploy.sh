#!/bin/bash

# BAH Jobs Scraper Lambda Deployment Script

echo "Creating Lambda deployment package..."

# Create deployment directory
mkdir -p deployment
cd deployment

# Copy the Lambda function
cp ../lambda_scrape_ba.py .

# Install dependencies
pip install -r ../requirements.txt -t .

# Create deployment package
zip -r bah-job-scraper-lambda.zip .

echo "Deployment package created: deployment/bah-job-scraper-lambda.zip"
echo ""
echo "To deploy to AWS Lambda:"
echo "1. Upload the zip file to your Lambda function"
echo "2. Set the handler to: lambda_scrape_ba.lambda_handler"
echo "3. Set memory to at least 512MB"
echo "4. Set timeout to at least 5 minutes (300 seconds)"
echo "5. Consider adding environment variables for configuration"