# 🔧 Configuration Guide: Placeholders to Replace

## Required Configuration (Must Replace)

### 1. Azure OpenAI Configuration
```env
# Replace these with your actual Azure OpenAI values:
AZURE_OPENAI_API_KEY=8d8323bd8e584737a0ff9b9fee6a8da3  # ✅ You already have this
ENDPOINT_URL=https://netradyneinternalbizteams.openai.azure.com/  # ✅ You already have this
DEPLOYMENT_NAME=gpt-4o  # ✅ You already have this
AZURE_OPENAI_API_VERSION=2024-05-01-preview  # ✅ Default is correct
```

### 2. Email Configuration (MUST REPLACE)
```env
# Replace with your actual email credentials:
EMAIL_USERNAME=your_actual_email@gmail.com  # ❌ REPLACE THIS
EMAIL_PASSWORD=your_actual_app_password  # ❌ REPLACE THIS (Gmail App Password)
FROM_EMAIL=your_actual_email@gmail.com  # ❌ REPLACE THIS
OWNER_EMAIL=owner@yourdomain.com  # ❌ REPLACE THIS (who receives notifications)
```

### 3. Project Information (SHOULD REPLACE)
```env
# Customize for your project:
PROJECT_NAME=Your Actual Project Name  # ❌ REPLACE THIS
PROJECT_OWNER=Your Name  # ❌ REPLACE THIS
```

### 4. Database Configuration (MUST REPLACE)
```env
# Replace with your actual database connection:
DATABASE_URL=postgresql://username:password@host:port/database_name  # ❌ REPLACE THIS
```

## Optional Configuration (Can Keep Defaults)

### 5. GitHub Webhook (Recommended for Production)
```env
# Generate a random secret for webhook security:
GITHUB_WEBHOOK_SECRET=your_random_secret_here  # ⚠️ GENERATE A RANDOM SECRET
```

### 6. API Configuration (Usually Keep Defaults)
```env
API_URL=http://localhost:8000  # ✅ Keep for local development
LOG_LEVEL=INFO  # ✅ Keep default
```

### 7. SMTP Settings (Keep Defaults for Gmail)
```env
SMTP_SERVER=smtp.gmail.com  # ✅ Keep for Gmail
SMTP_PORT=587  # ✅ Keep for Gmail
```

## Step-by-Step Setup

### Step 1: Copy Environment File
```bash
cp .env.example .env
```

### Step 2: Update .env with Your Values
Based on your Azure OpenAI setup, your `.env` should look like:

```env
# Database Configuration - REPLACE WITH YOUR DATABASE
DATABASE_URL=postgresql://your_user:your_password@your_host:5432/your_database

# API Configuration
API_URL=http://localhost:8000
LOG_LEVEL=INFO

# Azure OpenAI Configuration - ✅ YOU HAVE THESE
AZURE_OPENAI_API_KEY=8d8323bd8e584737a0ff9b9fee6a8da3
ENDPOINT_URL=https://netradyneinternalbizteams.openai.azure.com/
DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-05-01-preview

# Email Configuration - ❌ REPLACE THESE
EMAIL_USERNAME=your.email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
FROM_EMAIL=your.email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Project Configuration - ❌ CUSTOMIZE THESE
PROJECT_NAME=Agentic CI/CD Task Manager
PROJECT_OWNER=Your Name
OWNER_EMAIL=your.email@gmail.com

# GitHub Webhook Configuration - ⚠️ GENERATE A SECRET
GITHUB_WEBHOOK_SECRET=generate_a_random_secret_here
```

### Step 3: Gmail App Password Setup (If Using Gmail)
1. Go to Google Account settings: https://myaccount.google.com/
2. Security → 2-Step Verification (enable if not already)
3. Security → App passwords
4. Generate app password for "Mail"
5. Use this app password in `EMAIL_PASSWORD` field

### Step 4: Test Configuration
```bash
python test_ai_agent.py
```

## What Each Placeholder Does

| Placeholder | Purpose | Required | Your Status |
|-------------|---------|----------|-------------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI authentication | ✅ Required | ✅ You have it |
| `ENDPOINT_URL` | Azure OpenAI endpoint | ✅ Required | ✅ You have it |
| `DEPLOYMENT_NAME` | Azure model deployment | ✅ Required | ✅ You have it |
| `EMAIL_USERNAME` | SMTP email login | ✅ Required | ❌ Need to set |
| `EMAIL_PASSWORD` | SMTP email password | ✅ Required | ❌ Need to set |
| `OWNER_EMAIL` | Who gets PR notifications | ✅ Required | ❌ Need to set |
| `DATABASE_URL` | Database connection | ✅ Required | ❌ Need to set |
| `PROJECT_NAME` | Your project name | ⚠️ Optional | ❌ Should customize |
| `PROJECT_OWNER` | Your name | ⚠️ Optional | ❌ Should customize |
| `GITHUB_WEBHOOK_SECRET` | Webhook security | ⚠️ Recommended | ❌ Should generate |

## Security Notes

1. **Never commit `.env` file to git** - it contains secrets
2. **Use app passwords, not regular passwords** for email
3. **Generate a strong webhook secret** (use random string generator)
4. **Keep Azure OpenAI key secure** - rotate periodically

## Verification Commands

After setup, verify your configuration:

```bash
# Test configuration
curl -X GET "http://localhost:8000/ai-email/status"

# Test email service
curl -X POST "http://localhost:8000/ai-email/test"
```

## Next Steps After Configuration

1. Start the API server: `python task_api.py`
2. Test the email service: `python test_ai_agent.py`
3. Set up GitHub webhook in your repository
4. Test with a real PR creation

## Troubleshooting

- **Email not sending**: Check Gmail app password and SMTP settings
- **AI not working**: Verify Azure OpenAI credentials and deployment name
- **Database errors**: Check DATABASE_URL format and connection
- **Webhook issues**: Verify GitHub webhook configuration and secret
