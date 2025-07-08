#!/usr/bin/env python3
"""
Test script for AI Email Agent
Run this script to test the email functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_email_agent import ai_email_agent

def test_configuration():
    """Test if all required configuration is present"""
    print("🔧 Testing Configuration...")
    
    required_vars = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "EMAIL_USERNAME": os.getenv("EMAIL_USERNAME"),
        "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD"),
        "OWNER_EMAIL": os.getenv("OWNER_EMAIL")
    }
    
    missing_vars = []
    for var, value in required_vars.items():
        if value:
            print(f"  ✅ {var}: Configured")
        else:
            print(f"  ❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file configuration.")
        return False
    else:
        print("\n✅ All required configuration is present!")
        return True

def test_ai_generation():
    """Test AI email content generation"""
    print("\n🧠 Testing AI Email Generation...")
    
    test_pr_data = {
        "title": "Add user authentication system",
        "number": 42,
        "author": "testdeveloper",
        "url": "https://github.com/example/repo/pull/42",
        "description": "This PR implements a comprehensive user authentication system with JWT tokens, password hashing, and session management.",
        "branch_from": "feature/auth-system",
        "branch_to": "main",
        "files_changed": ["auth.py", "models.py", "requirements.txt", "tests/test_auth.py"]
    }
    
    try:
        email_content = ai_email_agent.generate_pr_email_content(test_pr_data)
        
        print("  ✅ AI email generation successful!")
        print(f"  📧 Subject: {email_content['subject']}")
        print(f"  📝 Body length: {len(email_content['body'])} characters")
        
        # Save generated content to file for review
        with open('test_email_output.html', 'w') as f:
            f.write(email_content['body'])
        print("  💾 Email content saved to 'test_email_output.html'")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI email generation failed: {e}")
        return False

def test_email_sending():
    """Test email sending functionality"""
    print("\n📧 Testing Email Sending...")
    
    try:
        result = ai_email_agent.test_email_service()
        
        if result['success']:
            print("  ✅ Test email sent successfully!")
            print(f"  📬 Email sent to: {os.getenv('OWNER_EMAIL')}")
            print("  📋 Check your inbox for the test email.")
        else:
            print(f"  ❌ Email sending failed: {result['message']}")
        
        return result['success']
        
    except Exception as e:
        print(f"  ❌ Email sending test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Email Agent Test Suite")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_configuration()
    if not config_ok:
        print("\n⚠️  Configuration test failed. Please fix configuration before proceeding.")
        return
    
    # Test AI generation
    ai_ok = test_ai_generation()
    
    # Test email sending
    email_ok = test_email_sending()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"  AI Generation: {'✅ PASS' if ai_ok else '❌ FAIL'}")
    print(f"  Email Sending: {'✅ PASS' if email_ok else '❌ FAIL'}")
    
    if config_ok and ai_ok and email_ok:
        print("\n🎉 All tests passed! Your AI Email Agent is ready to use.")
        print("\n📋 Next steps:")
        print("  1. Set up GitHub webhook in your repository")
        print("  2. Configure webhook URL: https://your-domain.com/webhooks/github")
        print("  3. Test with a real PR creation")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above and fix the configuration.")
    
    print("\n📚 For detailed setup instructions, see: AI_EMAIL_AGENT_SETUP.md")

if __name__ == "__main__":
    main()
