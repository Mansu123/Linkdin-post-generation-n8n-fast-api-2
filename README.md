# Linkdin-post-generation-n8n-fast-api-2

# LinkedIn Post Automation with Gemini AI

An automated workflow that generates and publishes LinkedIn posts using Google's Gemini AI and n8n automation platform.

## 🚀 Features

- **AI-Powered Content Generation**: Uses Google Gemini API to create engaging LinkedIn posts
- **Automated Publishing**: Automatically posts content to LinkedIn using LinkedIn API v2
- **User Authentication**: Retrieves LinkedIn user information for proper post attribution
- **Customizable Content**: Easy to modify prompts and content generation parameters
- **Error Handling**: Built-in validation and error checking
- **Secure Configuration**: Environment-based API key management

## 📋 Prerequisites

Before you begin, ensure you have:

- [n8n](https://n8n.io/) installed and running
- LinkedIn Developer Account with API access
- Google Cloud Platform account with Gemini API enabled
- Basic knowledge of REST APIs and JSON

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/linkedin-automation.git
cd linkedin-automation
```

### 2. Set Up n8n

If you haven't installed n8n yet:

```bash
npm install n8n -g
```

### 3. Import the Workflow

1. Start n8n: `n8n start`
2. Open n8n interface (usually at `http://localhost:5678`)
3. Import the workflow JSON file from this repository

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

### LinkedIn API Setup

1. **Create a LinkedIn App**:
   - Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
   - Create a new app
   - Request access to the following products:
     - Sign In with LinkedIn using OpenID Connect
     - Share on LinkedIn
     - Marketing Developer Platform (if needed)

2. **Get Access Token**:
   - Follow LinkedIn's OAuth 2.0 flow
   - Ensure your app has `w_member_social` and `r_liteprofile` permissions

3. **Configure Redirect URLs**:
   - Add your callback URLs in the LinkedIn app settings

### Google Gemini API Setup

1. **Enable the API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Generative Language API
   - Create API credentials

2. **Get API Key**:
   - Create a new API key in the Google Cloud Console
   - Restrict the API key to the Generative Language API

## 🎯 Usage

### Basic Workflow

1. **Start the Workflow**: The automation begins with a manual trigger or schedule
2. **Fetch User Info**: Retrieves LinkedIn user information for post attribution
3. **Generate Content**: Uses Gemini AI to create engaging post content
4. **Process Data**: Formats the content according to LinkedIn API requirements
5. **Publish Post**: Posts the content to LinkedIn
6. **Validation**: Checks if the post was successfully created

### Customizing Content Generation

Modify the Gemini API prompt in the workflow:

```json
{
  "text": "Create a professional LinkedIn post about [YOUR_TOPIC]. Make it engaging and include relevant hashtags. Keep it under 300 characters."
}
```

### Scheduling Posts

Configure n8n's cron trigger to run the workflow automatically:

```json
{
  "rule": {
    "interval": [
      {
        "field": "cronExpression",
        "expression": "0 9 * * 1-5"
      }
    ]
  }
}
```

## 📁 Project Structure

```
backend/
├── main.py                 ← Replace with complete file above
├── services/
│   ├── __init__.py        ← Should exist (empty file)
│   ├── gemini_service.py  ← Replace with simple version
│   └── linkedin_service.py ← Should exist (from earlier)
├── models/
│   ├── __init__.py        ← Should exist (empty file)  
│   └── schemas.py         ← Should exist (from earlier)
└── config/
    ├── __init__.py        ← Should exist (empty file)
    └── settings.py        ← Should exist (from earlier)
## 🔒 Security Best Practices

- **Never commit API keys** to version control
- Use environment variables for all sensitive data
- Regularly rotate your API keys and access tokens
- Implement proper error handling to avoid exposing sensitive information
- Use HTTPS for all API communications
- Follow LinkedIn's rate limiting guidelines

## 🚨 Important Security Notes

⚠️ **CRITICAL**: Never share your API keys publicly. If you accidentally expose them:

1. **Immediately revoke** the compromised keys
2. **Generate new credentials**
3. **Update your environment variables**
4. **Review your account** for any unauthorized activity

## 📊 API Endpoints Used

| Service | Endpoint | Method | Purpose |
|---------|----------|---------|---------|
| LinkedIn | `/v2/userinfo` | GET | Retrieve user information |
| LinkedIn | `/v2/ugcPosts` | POST | Create new posts |
| Gemini | `/v1beta/models/gemini-pro:generateContent` | POST | Generate content |

## 🔧 Troubleshooting

### Common Issues

**403 Forbidden Error**:
- Check if your LinkedIn app has the required permissions
- Verify your access token is valid and not expired

**Rate Limiting**:
- LinkedIn has rate limits; implement delays between requests
- Monitor your API usage in the developer console

**Invalid Content**:
- Ensure your post content meets LinkedIn's content policies
- Check character limits and formatting requirements

### Debug Mode

Enable n8n debug mode to see detailed logs:

```bash
N8N_LOG_LEVEL=debug n8n start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow JavaScript/JSON best practices
- Add comments to complex workflow nodes
- Test your changes thoroughly
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [n8n](https://n8n.io/) for the automation platform
- [Google Gemini](https://ai.google.dev/) for AI content generation
- [LinkedIn Developer Platform](https://developer.linkedin.com/) for API access

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/linkedin-automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/linkedin-automation/discussions)
- **Email**: your-email@example.com

## 🗺️ Roadmap

- [ ] Add support for image posts
- [ ] Implement content scheduling
- [ ] Add analytics tracking
- [ ] Support for multiple LinkedIn accounts
- [ ] Integration with other social media platforms
- [ ] Advanced content personalization

---

**⭐ If this project helped you, please give it a star on GitHub!**
