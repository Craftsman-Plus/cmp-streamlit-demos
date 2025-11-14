# Deploying to Streamlit Cloud

This guide will walk you through deploying the Brand Guidelines Validator to Streamlit Cloud.

## Prerequisites

1. A [Streamlit Cloud](https://streamlit.io/cloud) account (free)
2. A GitHub repository with your code
3. AWS credentials for authentication

## Step 1: Prepare Your Repository

Your repository should have the following structure:

```
cmp-streamlit-demos/
├── validation_app.py          # Main application
├── authenticate.py            # Authentication module
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit configuration
└── README.md                  # Documentation
```

## Step 2: Push to GitHub

If you haven't already, push your code to GitHub:

```bash
cd /Users/amitaig/Projects/Craftsman+/temp/cmp-streamlit-demos

# Initialize git if needed
git init

# Add files
git add validation_app.py authenticate.py requirements.txt .streamlit/config.toml README.md

# Commit
git commit -m "Add brand guidelines validation app"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/cmp-streamlit-demos.git

# Push
git push -u origin main
```

## Step 3: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure your app:**
   - **Repository**: Select your repository (e.g., `YOUR_USERNAME/cmp-streamlit-demos`)
   - **Branch**: `main` (or your preferred branch)
   - **Main file path**: `validation_app.py`

5. **Click "Advanced settings"** before deploying

## Step 4: Configure Secrets

In the "Advanced settings" section, add your secrets:

### Secrets Configuration

Click on "Secrets" and add the following in TOML format:

```toml
# AWS Credentials for Cognito Authentication
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
AWS_DEFAULT_REGION = "us-east-1"

# Optional: Pre-configured authentication (for demo purposes)
[auth]
email = "system.admin@craftsmanplus.com"
client_id = "4djrt5jve4ud0de66i75splf7l"
```

### How to Get AWS Credentials:

1. Log in to AWS Console
2. Go to IAM → Users → Your User
3. Security credentials tab
4. Create access key (if you don't have one)
5. Copy the Access Key ID and Secret Access Key

**Important**: The AWS user needs permissions for:
- `cognito-idp:InitiateAuth`
- Access to the Cognito User Pool

## Step 5: Deploy

1. Click **"Deploy!"**
2. Wait for the deployment to complete (usually 2-3 minutes)
3. Your app will be available at: `https://YOUR-APP-NAME.streamlit.app`

## Step 6: Update Environment Variables (Optional)

If you need to update authentication.py to use Streamlit secrets:

The authentication module will automatically use AWS credentials from the environment. Streamlit Cloud injects secrets as environment variables.

## Deployment Checklist

- [ ] Repository is pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] AWS credentials are added to Streamlit secrets
- [ ] App is deployed and accessible
- [ ] Authentication works correctly
- [ ] File uploads work (PDF and images)
- [ ] Validation endpoint is reachable

## Troubleshooting

### Authentication Fails

**Problem**: "Error during authentication" message

**Solutions**:
1. Verify AWS credentials in secrets
2. Check that the AWS region is correct (`us-east-1`)
3. Ensure the Cognito client ID is correct
4. Verify the AWS user has Cognito permissions

### App Crashes on Startup

**Problem**: App shows error on load

**Solutions**:
1. Check the logs in Streamlit Cloud
2. Verify all dependencies in `requirements.txt`
3. Check for syntax errors in the code
4. Ensure all imported modules are available

### File Upload Issues

**Problem**: Can't upload PDF or images

**Solutions**:
1. Check file size limits (Streamlit Cloud has limits)
2. Verify file formats are correct
3. Check browser console for errors

### API Connection Issues

**Problem**: Validation requests fail

**Solutions**:
1. Verify the API endpoint is accessible: `https://ai.dev.craftsmanplus.com`
2. Check authentication token is valid
3. Verify network connectivity from Streamlit Cloud

## Custom Domain (Optional)

To use a custom domain:

1. Go to your app settings in Streamlit Cloud
2. Navigate to "General" → "Custom subdomain"
3. Enter your desired subdomain
4. Click "Save"

Your app will be available at: `https://your-subdomain.streamlit.app`

## Updating Your App

To update your deployed app:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update validation app"
   git push
   ```
3. Streamlit Cloud will automatically detect changes and redeploy

## Resource Limits

Streamlit Cloud free tier has:
- **Resources**: 1 GB RAM
- **Storage**: Limited
- **Always on**: Apps sleep after inactivity
- **Public access**: Apps are public by default

For production use, consider [Streamlit Cloud for Teams](https://streamlit.io/cloud).

## Security Best Practices

1. **Never commit secrets** to your repository
2. **Use Streamlit secrets** for sensitive data
3. **Rotate credentials** regularly
4. **Monitor access logs** in Streamlit Cloud
5. **Use strong passwords** for authentication

## Multiple Apps in One Repository

If you want to deploy both `validation_app.py` and `playable_app.py`:

1. Deploy the first app (e.g., validation_app.py)
2. Click "New app" again
3. Select the same repository
4. Choose the different main file (e.g., playable_app.py)

Each app will have its own URL and can have different secrets.

## Monitoring and Logs

To view logs:

1. Go to your app in Streamlit Cloud
2. Click on the "☰" menu (hamburger menu)
3. Select "Manage app"
4. View logs in real-time

## Cost

- **Free tier**: 1 private app + unlimited public apps
- **For more apps**: Upgrade to Streamlit Cloud for Teams

## Support

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Discord](https://discord.gg/streamlit)

## Next Steps

After deployment:
1. Test all features thoroughly
2. Share the URL with your team
3. Monitor usage and performance
4. Collect feedback and iterate

