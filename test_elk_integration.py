#!/usr/bin/env python3
"""
Test script for ELK stack integration
This script tests the Elasticsearch client and logging functionality
"""

import requests
import json
import time
from app.elasticsearch.client import es_client
from app.logging.logging import app_logger

def test_elasticsearch_connection():
    """Test Elasticsearch connection"""
    print("🔍 Testing Elasticsearch connection...")
    
    if es_client.health_check():
        print("✅ Elasticsearch is healthy!")
        return True
    else:
        print("❌ Elasticsearch connection failed!")
        return False

def test_application_logging():
    """Test application logging"""
    print("📝 Testing application logging...")
    
    # Test different log levels
    app_logger.info("Test info message", test_field="test_value")
    app_logger.warning("Test warning message", test_field="test_value")
    app_logger.error("Test error message", test_field="test_value")
    
    print("✅ Application logging test completed!")

def test_elasticsearch_logging():
    """Test Elasticsearch logging"""
    print("📊 Testing Elasticsearch logging...")
    
    # Test API request logging
    es_client.log_api_request(
        method="GET",
        endpoint="/test",
        status_code=200,
        duration=0.1,
        ip_address="127.0.0.1"
    )
    
    # Test user action logging
    es_client.log_user_action(
        user_id=999,
        action="test_action",
        details={"test": "data"}
    )
    
    # Test error logging
    es_client.log_error(
        error_type="TestError",
        error_message="This is a test error",
        user_id=999
    )
    
    print("✅ Elasticsearch logging test completed!")

def test_api_endpoints():
    """Test API endpoints"""
    print("🌐 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working!")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Please start it with: python run.py")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 ELK Stack Integration Test")
    print("=" * 40)
    
    # Test Elasticsearch connection
    if not test_elasticsearch_connection():
        print("\n❌ Elasticsearch tests failed. Make sure ELK stack is running.")
        print("   Run: ./start_elk.sh")
        return
    
    # Test application logging
    test_application_logging()
    
    # Test Elasticsearch logging
    test_elasticsearch_logging()
    
    # Test API endpoints
    if test_api_endpoints():
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Check your logs in:")
        print("   - Kibana: http://localhost:5601")
        print("   - Elasticsearch: http://localhost:9200")
        print("   - Log file: app_events.log")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
