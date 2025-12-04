# Infrastructure

AWS CDK Infrastructure as Code for the project.

## Setup

```bash
pip install -r requirements.txt
```

## Useful Commands

* `cdk ls` - List all stacks
* `cdk synth` - Synthesize CloudFormation template
* `cdk deploy` - Deploy stack to AWS
* `cdk diff` - Compare deployed stack with current state
* `cdk destroy` - Remove stack from AWS

## Bootstrap

Before deploying, bootstrap your AWS environment:

```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```
