# Security Notes

## API Key Protection ✅

All sensitive credentials have been removed from public documentation and replaced with placeholders.

### Files Updated

**Documentation files (API key → `<YOUR_API_KEY>`):**
- ✅ `QUICK-REFERENCE.md` - 4 instances replaced
- ✅ `HACKATHON-DEMO.md` - 3 instances replaced
- ✅ `SYSTEM-STATUS.md` - 1 instance replaced
- ✅ `FINAL-VERIFICATION.md` - 2 instances replaced

**Protected files (.gitignore):**
- ✅ `.env` - Contains actual API key, excluded from git
- ✅ `setup/04_add_authentication.sh` - Saves API key to .env only

### How to Use Your API Key

Your actual API key is stored in:
```
/Users/arp2247/Desktop/aws-bedrock-challenge/HelmStream/.env
```

**To retrieve it:**
```bash
cd /Users/arp2247/Desktop/aws-bedrock-challenge/HelmStream
grep "API_KEY_VALUE" .env
```

**To use it in API calls:**
Replace `<YOUR_API_KEY>` in the documentation examples with your actual key from `.env`.

### Getting a New API Key

If you need to regenerate the API key:

```bash
cd /Users/arp2247/Desktop/aws-bedrock-challenge/HelmStream/setup
./04_add_authentication.sh
```

This will:
1. Create a new API key
2. Save it to `.env` file
3. Display it in the terminal (save it securely!)

### Security Best Practices ✅

**Implemented:**
- ✅ API keys stored in `.env` (gitignored)
- ✅ Documentation uses placeholder `<YOUR_API_KEY>`
- ✅ `.gitignore` prevents committing secrets
- ✅ IAM roles use least-privilege policies
- ✅ API Gateway rate limiting (50 req/sec)
- ✅ CloudWatch logging for audit trail

**For Production:**
- 🔒 Store API keys in AWS Secrets Manager
- 🔒 Enable AWS CloudTrail for API Gateway
- 🔒 Use AWS WAF for additional protection
- 🔒 Implement request signing (SigV4)
- 🔒 Add IP whitelisting if needed
- 🔒 Rotate API keys regularly

### Rate Limits

Current API key has the following limits:
- **Rate:** 50 requests/second
- **Burst:** 100 requests
- **Quota:** 10,000 requests/month

### Revoking Access

To revoke an API key:

```bash
# Get the API key ID
aws apigateway get-api-keys --query "items[?name=='helmstream-api-key'].id" --output text

# Delete the key
aws apigateway delete-api-key --api-key <KEY_ID>
```

---

## AWS Account Information

**Note:** The AWS Account ID (597293128974) is visible in documentation. This is generally acceptable for demo purposes, but for production:

- Consider using separate accounts for dev/staging/prod
- Enable AWS Organizations for better account management
- Use AWS Control Tower for governance

---

## For Hackathon Presentation

When demonstrating the API:

1. **Option 1 (Recommended):** Use the test scripts which read from `.env`
   ```bash
   python3 test_shipyard_queries.py
   python3 test_crisis_agent.py
   ```

2. **Option 2:** Export API key as environment variable
   ```bash
   export API_KEY=$(grep API_KEY_VALUE .env | cut -d= -f2)
   curl -H "x-api-key: $API_KEY" ...
   ```

3. **Option 3:** Use Postman with environment variables
   - Create environment variable: `api_key`
   - Set value from `.env` file
   - Use `{{api_key}}` in requests

---

*Last Updated: 2025-11-07*
*Security review completed*
