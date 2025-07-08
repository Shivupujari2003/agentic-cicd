# 🤖 AI Email Agent Setup Guide

## Overview
This AI Email Agent automatically generates and sends intelligent email notifications when pull requests are created in your GitHub repository. It uses OpenAI's GPT-4 to generate professional, context-aware emails.

## Features
- 🧠 **AI-Powered Email Generation**: Uses GPT-4 to create intelligent, context-aware emails
- 📧 **Automatic Email Sending**: Sends notifications to project owners via SMTP
- 🔗 **GitHub Integration**: Receives webhook events when PRs are created
- 🎨 **Professional Templates**: Generated emails include PR details, descriptions, and call-to-actions
- 🔒 **Secure Webhook Verification**: Validates GitHub webhook signatures
- 🧪 **Testing Endpoints**: Built-in testing functionality

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:

#### Required Configuration:
```env
# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-openai-api-key

# Email Settings (Gmail example)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
OWNER_EMAIL=owner@example.com

# Project Information
PROJECT_NAME=Your Project Name
PROJECT_OWNER=Your Name
```

#### Optional Configuration:
```env
# GitHub Webhook Secret (for security)
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# Custom SMTP Settings (if not using Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Gmail App Password Setup (if using Gmail)
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings → Security → App passwords
3. Generate an app password for "Mail"
4. Use this app password in `EMAIL_PASSWORD` (not your regular password)

### 4. Start the API Server
```bash
python task_api.py
```

The server will start on `http://localhost:8000`

## GitHub Webhook Setup

### 1. Configure Webhook in GitHub
1. Go to your GitHub repository
2. Navigate to Settings → Webhooks
3. Click "Add webhook"
4. Set the payload URL to: `https://your-domain.com/webhooks/github`
5. Content type: `application/json`
6. Select "Pull requests" events
7. Add your webhook secret (same as `GITHUB_WEBHOOK_SECRET` in .env)

### 2. Test the Webhook
After setup, create a test PR to verify the system works.

## API Endpoints

### Webhook Endpoint
- **POST** `/webhooks/github` - GitHub webhook receiver

### Testing Endpoints
- **POST** `/ai-email/test` - Test the email service with sample data
- **GET** `/ai-email/status` - Check configuration status
- **POST** `/ai-email/send-pr-notification` - Manually send a PR notification

### Example API Usage

#### Test the Email Service
```bash
curl -X POST "http://localhost:8000/ai-email/test"
```

#### Check Configuration Status
```bash
curl -X GET "http://localhost:8000/ai-email/status"
```

#### Manual PR Notification
```bash
curl -X POST "http://localhost:8000/ai-email/send-pr-notification" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Add new feature",
       "number": 123,
       "author": "developer",
       "url": "https://github.com/user/repo/pull/123",
       "description": "This PR adds a new feature",
       "branch_from": "feature/new-feature",
       "branch_to": "main"
     }'
```

## Email Template Customization

The AI generates dynamic email content, but you can customize the fallback template in `ai_email_agent.py`:

```python
def _generate_fallback_email(self, pr_data: Dict[str, Any]) -> Dict[str, str]:
    # Customize your fallback email template here
    pass
```

## Troubleshooting

### Common Issues

#### 1. Email Not Sending
- Check Gmail app password is correct
- Verify SMTP settings
- Check firewall/network restrictions
- Test with `/ai-email/test` endpoint

#### 2. Webhook Not Working
- Verify webhook URL is accessible from internet
- Check webhook secret matches
- Ensure repository has correct webhook configuration
- Check server logs for errors

#### 3. AI Content Generation Issues
- Verify OpenAI API key is valid
- Check OpenAI account has sufficient credits
- Monitor rate limits

### Debug Commands

Check configuration:
```bash
curl -X GET "http://localhost:8000/ai-email/status"
```

Test email service:
```bash
curl -X POST "http://localhost:8000/ai-email/test"
```

View server logs:
```bash
# Check the console output where you started the server
```

## Security Considerations

1. **Environment Variables**: Keep `.env` file secure and out of version control
2. **Webhook Secret**: Use a strong, unique webhook secret
3. **Email Credentials**: Use app passwords, not regular passwords
4. **API Keys**: Regularly rotate OpenAI API keys
5. **HTTPS**: Use HTTPS in production for webhook endpoints

## Production Deployment

### Environment Variables for Production
```env
# Production database
DATABASE_URL=postgresql://prod_user:password@prod_host:5432/prod_db

# Production API URL
API_URL=https://your-production-domain.com

# Reduced logging in production
LOG_LEVEL=WARNING

# Production email settings
FROM_EMAIL=noreply@your-company.com
PROJECT_NAME=Your Production App
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "task_api.py"]
```

## Monitoring and Logs

The system logs all important events:
- Email generation and sending
- Webhook processing
- Configuration issues
- Errors and exceptions

Monitor logs for:
- Failed email sends
- Webhook processing errors
- AI generation failures
- Configuration issues

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify configuration with `/ai-email/status`
3. Test individual components with test endpoints
4. Review environment variables and secrets

## License
This project is part of the Agentic CI/CD Task Manager system.
