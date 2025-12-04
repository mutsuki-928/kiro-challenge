# AWS Documentation Best Practices

When working with AWS services, always leverage official AWS documentation to ensure accuracy and best practices.

## When to Search AWS Documentation

Automatically search AWS documentation in these scenarios:

### 1. Working with AWS Services
- Before implementing any AWS service integration
- When encountering AWS-specific errors or issues
- When configuring AWS resources (Lambda, API Gateway, DynamoDB, etc.)
- When using AWS CDK constructs or CloudFormation

### 2. Troubleshooting
- AWS service errors or exceptions
- Permission or IAM-related issues
- Service limits or quotas questions
- Performance optimization for AWS services

### 3. Best Practices
- Security configurations
- Cost optimization
- Architecture patterns
- Service-specific recommendations

### 4. New Features
- When asked about recent AWS updates
- When implementing newly released features
- When checking service availability in regions

## How to Use AWS Documentation Tools

Use the MCP AWS documentation tools available:

```
# Search for general AWS topics
mcp_aws_knowledge_mcp_server_aws___search_documentation

# Read specific documentation pages
mcp_aws_knowledge_mcp_server_aws___read_documentation

# Check regional availability
mcp_aws_knowledge_mcp_server_aws___get_regional_availability

# Get documentation recommendations
mcp_aws_knowledge_mcp_server_aws___recommend
```

## Search Strategy

### For API/SDK Questions
Use topic: `reference_documentation`
- Example: "Lambda invoke API Python boto3"
- Example: "DynamoDB put_item parameters"

### For Troubleshooting
Use topic: `troubleshooting`
- Example: "Lambda timeout error"
- Example: "API Gateway 403 forbidden"

### For CDK
Use topics: `cdk_docs` and `cdk_constructs`
- Example: "CDK Lambda function Python"
- Example: "API Gateway Lambda integration CDK"

### For Architecture
Use topic: `general`
- Example: "Serverless API best practices"
- Example: "DynamoDB design patterns"

## Documentation Priority

1. **Always check documentation first** before providing AWS-related answers
2. Prefer official AWS documentation over general knowledge
3. Include documentation links in responses when relevant
4. Verify service availability in the target region
5. Check for recent updates or changes to services

## Example Workflow

When user asks about AWS:
1. Identify the AWS service(s) involved
2. Search relevant documentation
3. Verify current best practices
4. Check regional availability if needed
5. Provide answer with documentation references

## Common AWS Services to Document

- **Compute**: Lambda, EC2, ECS, Fargate
- **Storage**: S3, DynamoDB, RDS, ElastiCache
- **Networking**: API Gateway, VPC, CloudFront, Route53
- **Security**: IAM, Cognito, Secrets Manager, KMS
- **Monitoring**: CloudWatch, X-Ray, CloudTrail
- **Infrastructure**: CDK, CloudFormation, SAM

## Documentation Quality

When referencing AWS documentation:
- Cite specific documentation URLs when available
- Mention the service version or API version
- Note any regional limitations
- Include code examples from official docs
- Highlight important warnings or notes

## Staying Current

- AWS services update frequently
- Always search for latest information
- Check "What's New" for recent changes
- Verify deprecated features or APIs
- Look for migration guides when needed
