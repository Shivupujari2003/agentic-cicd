"""
AI Email Agent for PR Notifications
Generates intelligent emails using AI and sends them when PRs are created
"""

import os
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class AIEmailAgent:
    """AI-powered email generation and sending agent for PR notifications"""
    
    def __init__(self):
        """Initialize the AI Email Agent with necessary configurations"""
        # Azure OpenAI API setup
        endpoint = os.getenv("ENDPOINT_URL", "https://netradyneinternalbizteams.openai.azure.com/")
        deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
        
        # Create Azure OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=subscription_key,
            api_version=api_version
        )
        self.deployment_name = deployment
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.email_username)
        
        # Project configuration
        self.project_name = os.getenv("PROJECT_NAME", "Agentic CI/CD Task Manager")
        self.project_owner = os.getenv("PROJECT_OWNER", "Project Owner")
        self.owner_email = os.getenv("OWNER_EMAIL")
        
        # Validate required environment variables
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration is present"""
        required_vars = {
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
            "EMAIL_USERNAME": self.email_username,
            "EMAIL_PASSWORD": self.email_password,
            "OWNER_EMAIL": self.owner_email
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def generate_pr_email_content(self, pr_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate intelligent email content using AI based on PR data
        
        Args:
            pr_data: Dictionary containing PR information
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        try:
            # Extract PR information
            pr_title = pr_data.get('title', 'New Pull Request')
            pr_number = pr_data.get('number', 'Unknown')
            pr_author = pr_data.get('author', 'Unknown Author')
            pr_url = pr_data.get('url', '#')
            pr_description = pr_data.get('description', 'No description provided')
            branch_from = pr_data.get('branch_from', 'feature-branch')
            branch_to = pr_data.get('branch_to', 'main')
            files_changed = pr_data.get('files_changed', [])
            
            # Create AI prompt for email generation
            prompt = f"""
            Generate a professional and informative email notification for a new pull request in the {self.project_name} project.
            
            PR Details:
            - Title: {pr_title}
            - PR Number: #{pr_number}
            - Author: {pr_author}
            - From Branch: {branch_from}
            - To Branch: {branch_to}
            - Description: {pr_description}
            - Files Changed: {', '.join(files_changed) if files_changed else 'Not specified'}
            - PR URL: {pr_url}
            
            Requirements:
            1. Create a compelling subject line (max 80 characters)
            2. Generate a professional email body that includes:
               - Greeting to the project owner
               - Summary of the PR
               - Key changes or features
               - Call to action for review
               - Professional closing
            3. Use a professional but friendly tone
            4. Include relevant technical details
            5. Format as HTML for better presentation
            
            Return the response in JSON format with 'subject' and 'body' keys.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.deployment_name,  # Use Azure deployment name
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant specialized in generating professional technical email notifications for software development projects. Always respond with valid JSON containing 'subject' and 'body' keys."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                email_content = json.loads(ai_response)
                if 'subject' not in email_content or 'body' not in email_content:
                    raise ValueError("AI response missing required keys")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse AI response as JSON: {e}")
                # Fallback to manual parsing or default content
                email_content = self._generate_fallback_email(pr_data)
            
            logger.info(f"Generated AI email content for PR #{pr_number}")
            return email_content
            
        except Exception as e:
            logger.error(f"Error generating AI email content: {e}")
            # Return fallback email content
            return self._generate_fallback_email(pr_data)
    
    def _generate_fallback_email(self, pr_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback email content when AI generation fails"""
        pr_title = pr_data.get('title', 'New Pull Request')
        pr_number = pr_data.get('number', 'Unknown')
        pr_author = pr_data.get('author', 'Unknown Author')
        pr_url = pr_data.get('url', '#')
        
        subject = f"🔔 New PR #{pr_number}: {pr_title}"
        
        body = f"""
        <html>
        <body>
            <h2>🚀 New Pull Request Notification</h2>
            
            <p>Hello {self.project_owner},</p>
            
            <p>A new pull request has been created for the <strong>{self.project_name}</strong> project:</p>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3>📋 PR Details</h3>
                <ul>
                    <li><strong>Title:</strong> {pr_title}</li>
                    <li><strong>PR Number:</strong> #{pr_number}</li>
                    <li><strong>Author:</strong> {pr_author}</li>
                    <li><strong>From:</strong> {pr_data.get('branch_from', 'feature-branch')}</li>
                    <li><strong>To:</strong> {pr_data.get('branch_to', 'main')}</li>
                </ul>
            </div>
            
            <p><strong>Description:</strong><br>
            {pr_data.get('description', 'No description provided')}</p>
            
            <p style="text-align: center; margin: 20px 0;">
                <a href="{pr_url}" style="background: #1f77b4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    👀 Review Pull Request
                </a>
            </p>
            
            <p>Please review this pull request at your earliest convenience.</p>
            
            <p>Best regards,<br>
            AI Agent - {self.project_name}</p>
            
            <hr>
            <p style="font-size: 12px; color: #666;">
                This email was automatically generated by the AI Email Agent.
                Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            </p>
        </body>
        </html>
        """
        
        return {"subject": subject, "body": body}
    
    def send_email(self, subject: str, body: str, to_email: Optional[str] = None) -> bool:
        """
        Send email notification
        
        Args:
            subject: Email subject
            body: Email body (HTML format)
            to_email: Recipient email (defaults to owner email)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            recipient = to_email or self.owner_email
            if not recipient:
                logger.error("No recipient email specified")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient
            
            # Add HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, recipient, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def process_pr_notification(self, pr_data: Dict[str, Any]) -> bool:
        """
        Complete workflow: Generate and send PR notification email
        
        Args:
            pr_data: PR information dictionary
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            logger.info(f"Processing PR notification for PR #{pr_data.get('number', 'Unknown')}")
            
            # Generate AI email content
            email_content = self.generate_pr_email_content(pr_data)
            
            # Send email
            success = self.send_email(
                subject=email_content['subject'],
                body=email_content['body']
            )
            
            if success:
                logger.info("PR notification email sent successfully")
            else:
                logger.error("Failed to send PR notification email")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing PR notification: {e}")
            return False
    
    def test_email_service(self) -> Dict[str, Any]:
        """
        Test the email service with a sample PR
        
        Returns:
            Dictionary with test results
        """
        test_pr_data = {
            "title": "Add new feature for task analytics",
            "number": 42,
            "author": "TestDeveloper",
            "url": "https://github.com/example/repo/pull/42",
            "description": "This PR adds comprehensive analytics features for task management including completion rates, time tracking, and performance metrics.",
            "branch_from": "feature/task-analytics",
            "branch_to": "main",
            "files_changed": ["task_api.py", "analytics.py", "requirements.txt"]
        }
        
        try:
            # Generate email content
            email_content = self.generate_pr_email_content(test_pr_data)
            
            # Test email sending
            test_subject = f"[TEST] {email_content['subject']}"
            test_body = f"<p><strong>🧪 This is a test email</strong></p>{email_content['body']}"
            
            email_sent = self.send_email(test_subject, test_body)
            
            return {
                "success": email_sent,
                "message": "Test email sent successfully" if email_sent else "Failed to send test email",
                "email_content": email_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Test failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

# Global instance
ai_email_agent = AIEmailAgent()
