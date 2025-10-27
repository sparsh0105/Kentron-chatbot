# Deployment Guide: Kentron Guardrails Chatbot

This guide explains how to deploy the Kentron Guardrails Chatbot (`streamlit_chatbot.py`) to Streamlit Community Cloud.

## Prerequisites

1. **GitHub Account** - Streamlit Community Cloud deploys from GitHub repositories
2. **Streamlit Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **API Credentials** - You'll need:
   - Kentron API Key
   - OpenAI API Key
   - Policy ID

## About the Kentron Guardrails Chatbot

This application provides a clean, user-friendly chatbot interface powered by:
- **OpenAI GPT-4o-mini** for AI responses
- **Kentron Guardrails** for content safety
- **BYOK (Bring Your Own Key)** proxy mode
- UI-driven credential management for flexibility

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit: Kentron Guardrails Chatbot"
git branch -M main

# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### 1.2 Required Files

Your repository should contain:
- `streamlit_chatbot.py` - Main application file
- `requirements.txt` or create minimal requirements for this app
- `.streamlit/config.toml` - Streamlit configuration
- `README.md` - Project documentation

### 1.3 Update requirements.txt

For the Streamlit chatbot, you can use a minimal `requirements.txt`:

```txt
streamlit>=1.28.0
openai>=1.12.0
python-dotenv>=1.0.0
```

**OR** rename `requirements.txt` to `requirements_comparative.txt` and use:
```bash
# Rename the current requirements.txt
mv requirements.txt requirements_comparative.txt

# Create new simple requirements.txt
echo "streamlit>=1.28.0" > requirements.txt
echo "openai>=1.12.0" >> requirements.txt
echo "python-dotenv>=1.0.0" >> requirements.txt
```

## Step 2: Deploy to Streamlit Community Cloud

### 2.1 Access Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"** and authenticate with GitHub
3. Click **"New app"**

### 2.2 Configure Your App

Fill in the deployment form:

**Repository:** Select your repository
```
yourusername/your-repo-name
```

**Branch:** Usually `main` or `master`
```
main
```

**Main file path:**
```
streamlit_chatbot.py
```

### 2.3 Set Secrets (Optional - Recommended for Convenience)

Click **"Advanced settings"** → **"Secrets"** and optionally add:

```toml
[default]
KENTRON_API_KEY = "your_kentron_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
POLICY_ID = "your_policy_id_here"
```

**Important Notes:**
- Secrets are **optional** - users can override them via the UI
- If set, they pre-populate the input fields for convenience
- Users can change credentials anytime to use different policies or keys
- This allows flexibility for organizations with multiple policies or rotating API keys

### 2.4 Deploy

Click **"Deploy"** and wait for the build to complete (usually 1-2 minutes for this simple app).

## Step 3: Verify Deployment

### 3.1 Test the App

1. Visit your deployed app URL (e.g., `https://appname.streamlit.app`)
2. If secrets were configured, credentials are auto-loaded for convenience
3. Users can override or change credentials via the sidebar UI
4. Test a chat interaction to verify Kentron guardrails are working

### 3.2 Understanding the Flexible Configuration

The app supports multiple configuration approaches:

**Option 1: Use Secrets (Recommended for Organizations)**
- Set secrets in Streamlit Cloud
- They pre-populate the UI automatically
- Users can still override them

**Option 2: Manual Entry**
- Leave secrets empty
- Users enter credentials directly in the sidebar
- Perfect for testing or multi-policy environments

**Option 3: Mixed Approach**
- Set partial secrets (e.g., just OpenAI key)
- Users fill in remaining fields

This flexibility allows organizations to:
- Use different policies for different teams
- Rotate API keys without redeployment
- Test new policies without changing code

### 3.3 Check Logs

- View deployment logs in the Streamlit Cloud dashboard
- Any errors will be displayed there

## Step 4: Post-Deployment

### 4.1 Configure Custom Domain (Optional)

1. Go to app settings
2. Add your custom domain if desired

### 4.2 Monitor Usage

- Streamlit Community Cloud shows usage statistics
- Free tier has resource limits

## Troubleshooting

### Issue: App Won't Deploy

**Symptoms:** Build fails

**Solutions:**
- Check `requirements.txt` - use minimal dependencies for this app
- Ensure Python 3.8+ is supported
- Check deployment logs for specific errors

### Issue: API Keys Not Working

**Symptoms:** Authentication errors

**Solutions:**
- Verify secrets are set correctly in Streamlit dashboard
- Check that secret names match exactly: `KENTRON_API_KEY`, `OPENAI_API_KEY`, `POLICY_ID`
- Re-deploy after updating secrets

### Issue: Slow Responses

**Symptoms:** Long loading times

**Solutions:**
- Check network connectivity from Streamlit Cloud
- Verify Kentron API endpoint is accessible
- Consider using streaming responses (currently disabled)

## Security Best Practices

1. ✅ **DO** use Streamlit secrets for default API keys (optional)
2. ✅ **DO** add `.streamlit/secrets.toml` to `.gitignore`
3. ❌ **DON'T** commit API keys to version control
4. ❌ **DON'T** hardcode credentials in your code
5. ✅ **DO** rotate API keys regularly
6. ✅ **DO** allow users to override credentials via UI for flexibility
7. ⚠️ **NOTE**: Credentials are stored in session state and can be changed anytime by users

## Alternative Deployment Options

### Option 1: Streamlit Cloud for Teams

For private/production apps, consider Streamlit Cloud for Teams (paid).

### Option 2: Self-Hosted

Deploy on your own infrastructure:
- Docker containers
- Cloud providers (AWS, GCP, Azure)
- Virtual private servers

### Option 3: Other Platforms

- **Heroku** - Platform-as-a-Service
- **Railway** - Modern deployment platform
- **Render** - Simple cloud hosting

## Support

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Streamlit Forums: https://discuss.streamlit.io
- GitHub Issues: Report bugs in your repository

## Example .gitignore

Make sure to exclude sensitive files:

```gitignore
# Secrets
.streamlit/secrets.toml

# Virtual environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*.pyc

# IDE
.vscode/
.idea/

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

