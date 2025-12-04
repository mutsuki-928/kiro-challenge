# AWS Credentials Management

When working with AWS services (CDK, CLI, boto3), follow these guidelines to maintain proper authentication.

## Important Reminders

### Before Running AWS Commands

1. **Check for existing credentials**: Before running any AWS-related commands, check if AWS credentials are already set in the current environment.

2. **Prompt for credentials if needed**: If credentials are not available or might have expired, ask the user to provide:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_SESSION_TOKEN (if using temporary credentials)
   - AWS_DEFAULT_REGION

3. **Reuse environment**: When running multiple AWS commands in sequence, try to reuse the same shell environment by:
   - Using the same terminal session
   - Exporting credentials once at the beginning
   - Chaining commands with `&&` when appropriate (but avoid with `cd`)

### Example Pattern

When deploying or running AWS commands:

```bash
# Set credentials first
export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."

# Then run AWS commands
source venv/bin/activate && cdk deploy
```

### Credential Expiration

- Temporary credentials (with SESSION_TOKEN) typically expire after 1-12 hours
- If commands start failing with authentication errors, credentials may have expired
- Ask the user for fresh credentials when this happens

### Security Notes

- Never log or display full credentials
- Don't commit credentials to git
- Use environment variables or AWS profiles
- Consider using AWS SSO or IAM roles when possible

## Common AWS Commands

When running these commands, ensure credentials are set:

- `aws sts get-caller-identity` - Verify credentials
- `cdk bootstrap` - Bootstrap CDK
- `cdk deploy` - Deploy stack
- `cdk destroy` - Destroy stack
- `aws logs tail` - View Lambda logs
- Any boto3 operations in Python code

## Troubleshooting

If you encounter authentication errors:
1. Verify credentials are set: `echo $AWS_ACCESS_KEY_ID`
2. Check credential validity: `aws sts get-caller-identity`
3. Ask user for fresh credentials if expired
4. Ensure region is set correctly
