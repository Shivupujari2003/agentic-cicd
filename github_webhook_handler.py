"""
GitHub Webhook Handler for PR Events
Handles GitHub webhooks and triggers AI email notifications
"""

import os
import logging
import hashlib
import hmac
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, BackgroundTasks
import json
from datetime import datetime

from ai_email_agent import ai_email_agent

logger = logging.getLogger(__name__)

class GitHubWebhookHandler:
    """Handles GitHub webhook events for PR notifications"""
    
    def __init__(self):
        """Initialize webhook handler with GitHub secret"""
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.webhook_secret:
            logger.warning("GITHUB_WEBHOOK_SECRET not set - webhook signature verification disabled")
    
    def verify_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """
        Verify GitHub webhook signature
        
        Args:
            payload_body: Raw request body
            signature_header: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured - skipping signature verification")
            return True
        
        if not signature_header:
            logger.error("No signature header provided")
            return False
        
        try:
            # GitHub sends signature as "sha256=<hash>"
            algorithm, signature = signature_header.split('=', 1)
            if algorithm != 'sha256':
                logger.error(f"Unsupported signature algorithm: {algorithm}")
                return False
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload_body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures securely
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def extract_pr_data(self, webhook_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract relevant PR data from GitHub webhook payload
        
        Args:
            webhook_payload: GitHub webhook payload
            
        Returns:
            Extracted PR data or None if not a valid PR event
        """
        try:
            action = webhook_payload.get('action')
            if action not in ['opened', 'reopened']:
                logger.info(f"Ignoring PR action: {action}")
                return None
            
            pr = webhook_payload.get('pull_request', {})
            repository = webhook_payload.get('repository', {})
            
            # Extract PR information
            pr_data = {
                'title': pr.get('title', 'Untitled PR'),
                'number': pr.get('number'),
                'author': pr.get('user', {}).get('login', 'Unknown'),
                'url': pr.get('html_url', ''),
                'description': pr.get('body', 'No description provided'),
                'branch_from': pr.get('head', {}).get('ref', 'unknown-branch'),
                'branch_to': pr.get('base', {}).get('ref', 'main'),
                'repository_name': repository.get('name', 'Unknown Repository'),
                'repository_url': repository.get('html_url', ''),
                'created_at': pr.get('created_at'),
                'updated_at': pr.get('updated_at'),
                'action': action,
                'files_changed': []  # This would require additional API call to get changed files
            }
            
            # Add some metadata
            pr_data['webhook_timestamp'] = datetime.utcnow().isoformat()
            pr_data['event_type'] = 'pull_request'
            
            logger.info(f"Extracted PR data for #{pr_data['number']}: {pr_data['title']}")
            return pr_data
            
        except Exception as e:
            logger.error(f"Error extracting PR data from webhook: {e}")
            return None
    
    async def handle_webhook(self, request: Request, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """
        Handle incoming GitHub webhook
        
        Args:
            request: FastAPI request object
            background_tasks: Background tasks for async processing
            
        Returns:
            Response dictionary
        """
        try:
            # Get request body and headers
            payload_body = await request.body()
            signature_header = request.headers.get('X-Hub-Signature-256', '')
            event_type = request.headers.get('X-GitHub-Event', '')
            
            logger.info(f"Received GitHub webhook: {event_type}")
            
            # Verify signature if secret is configured
            if not self.verify_signature(payload_body, signature_header):
                logger.error("Invalid webhook signature")
                raise HTTPException(status_code=403, detail="Invalid signature")
            
            # Parse JSON payload
            try:
                webhook_payload = json.loads(payload_body.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
            
            # Handle pull request events
            if event_type == 'pull_request':
                pr_data = self.extract_pr_data(webhook_payload)
                if pr_data:
                    # Process notification in background
                    background_tasks.add_task(self.process_pr_notification, pr_data)
                    
                    return {
                        'status': 'success',
                        'message': f'PR notification queued for processing',
                        'pr_number': pr_data['number'],
                        'pr_title': pr_data['title'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        'status': 'ignored',
                        'message': 'PR event not relevant for notification',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            # Handle ping events (webhook test)
            elif event_type == 'ping':
                return {
                    'status': 'success',
                    'message': 'Webhook endpoint is working',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Ignore other event types
            else:
                logger.info(f"Ignoring webhook event type: {event_type}")
                return {
                    'status': 'ignored',
                    'message': f'Event type {event_type} not handled',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def process_pr_notification(self, pr_data: Dict[str, Any]):
        """
        Process PR notification in background
        
        Args:
            pr_data: Extracted PR data
        """
        try:
            logger.info(f"Processing background PR notification for #{pr_data['number']}")
            
            # Use AI email agent to generate and send notification
            success = ai_email_agent.process_pr_notification(pr_data)
            
            if success:
                logger.info(f"Successfully sent PR notification for #{pr_data['number']}")
            else:
                logger.error(f"Failed to send PR notification for #{pr_data['number']}")
                
        except Exception as e:
            logger.error(f"Error in background PR notification processing: {e}")

# Global instance
github_webhook_handler = GitHubWebhookHandler()
