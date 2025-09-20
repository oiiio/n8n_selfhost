#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lambda_scrape_ba import lambda_handler
import json

def test_lambda_function():
    """Test the Lambda function locally"""
    
    print("Testing Lambda function with limited jobs...")
    
    # Test with limited jobs for faster testing
    test_event = {
        "max_jobs": 5,
        "include_details": True
    }
    
    test_context = {}
    
    try:
        result = lambda_handler(test_event, test_context)
        
        print(f"Status Code: {result['statusCode']}")
        print("Response Body:")
        
        # Parse and pretty-print the response
        body = json.loads(result['body'])
        print(json.dumps(body, indent=2))
        
        if body.get('success'):
            print(f"\n✅ SUCCESS: Found {body['jobs_count']} jobs")
            if body.get('jobs'):
                print(f"First job title: {body['jobs'][0].get('title', 'N/A')}")
                print(f"First job location: {body['jobs'][0].get('location', 'N/A')}")
                if 'description' in body['jobs'][0]:
                    desc_preview = body['jobs'][0]['description'][:100] + "..." if len(body['jobs'][0]['description']) > 100 else body['jobs'][0]['description']
                    print(f"Description preview: {desc_preview}")
        else:
            print(f"❌ FAILED: {body.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_lambda_function()