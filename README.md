# Sanders Customer Platform CDK Infrastructure

AWS CDK infrastructure for the Sanders Customer Platform batch processing pipeline.

## Architecture Overview

This CDK application creates the following AWS resources:

### Core Resources
- **S3 Bucket**: `sanders-customer-platform-dev` - Data storage
- **DynamoDB Table**: `sanders_daily_customer_features_dev`
  - Partition key: `customer_id` (String)
  - Sort key: `date` (String)
  - Billing: PAY_PER_REQUEST
- **ECR Repository**: Docker image storage for batch jobs

### Compute Infrastructure
- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **AWS Batch**:
  - Fargate compute environment
  - Job queue
  - 3 job definitions (2GB, 8GB, 16GB memory configurations)
- **Step Functions**: Orchestrates batch job execution

### IAM Roles
- Batch service role
- ECS task execution role (for ECR access)
- Batch job role (with S3 and DynamoDB permissions)

## Prerequisites

- Python 3.9 or higher
- Node.js 18+ (required for AWS CDK)
- AWS CLI configured with appropriate credentials
- AWS CDK CLI: `npm install -g aws-cdk`
- UV package manager: `pip install uv`

## Setup

### 1. Install Node.js and CDK

```bash
# Install Node.js from https://nodejs.org/ (if not installed)

# Install AWS CDK CLI globally
npm install -g aws-cdk

# Verify installation
cdk --version
```

### 2. Install Python Dependencies

```bash
# Install uv (if not already installed)
pip install uv

# Install Python dependencies with uv
python -m uv pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Make sure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=eu-central-1
```

### 3. Bootstrap CDK (First time only)

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

## Usage

### Synthesize CloudFormation Template

```bash
cdk synth
```

### Deploy Infrastructure

Deploy to dev environment (default):
```bash
cdk deploy
```

Deploy to specific environment:
```bash
cdk deploy -c environment=dev
cdk deploy -c environment=prod
```

### View Differences

```bash
cdk diff
```

### Destroy Infrastructure

```bash
cdk destroy
```

## Docker Image Setup

After deployment, build and push your Docker image to ECR:

```bash
# Get ECR repository URI from outputs
ECR_URI=$(aws cloudformation describe-stacks \
  --stack-name SandersCustomerPlatformStack-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
  --output text)

# Login to ECR
aws ecr get-login-password --region eu-central-1 | \
  docker login --username AWS --password-stdin $ECR_URI

# Build and push image
docker build -t sanders-customer-platform .
docker tag sanders-customer-platform:latest $ECR_URI:latest
docker push $ECR_URI:latest
```

## Resource Naming Convention

All resources follow the pattern: `sanders-{resource-type}-{environment}`

Examples:
- S3: `sanders-customer-platform-dev`
- DynamoDB: `sanders_daily_customer_features_dev`
- VPC: `sanders-customer-platform-vpc-dev`
- Batch Queue: `sanders-batch-queue-dev`

## Outputs

After deployment, you'll see outputs including:

- `S3BucketName`: Name of the S3 bucket
- `DynamoDBTableName`: Name of the DynamoDB table
- `ECRRepositoryURI`: URI for pushing Docker images
- `VPCId`: VPC identifier
- `BatchJobQueueName`: Batch job queue name
- `StepFunctionsStateMachineARN`: State machine ARN for orchestration

## Step Functions Workflow

The default state machine orchestrates:

1. **Parallel Execution**:
   - Feature Extraction Job (8GB)
   - Data Processing Job (2GB)
2. **Sequential Execution**:
   - Model Training Job (16GB) - runs after parallel jobs complete

Modify [stepfunctions_statemachine.py](cdk/constructs/stepfunctions_statemachine.py) to customize the workflow.

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=cdk tests/
```

## Project Structure

```
sanders-customer-platform-cdk-infra/
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Poetry configuration
├── README.md                       # This file
├── cdk/
│   ├── __init__.py
│   ├── sanders_customer_platform_stack.py  # Main stack
│   └── constructs/                 # Reusable constructs
│       ├── __init__.py
│       ├── s3_bucket.py
│       ├── dynamodb_table.py
│       ├── ecr_repository.py
│       ├── vpc_network.py
│       ├── batch_iam_roles.py
│       ├── batch_environment.py
│       └── stepfunctions_statemachine.py
└── tests/
    └── unit/
        └── test_stack.py
```

## Security Notes

- All S3 buckets have encryption enabled and block public access
- DynamoDB has point-in-time recovery enabled for production
- ECR repositories scan images on push
- Batch jobs run in private subnets
- IAM roles follow least privilege principle

## Multi-Environment Support

The stack supports multiple environments (dev, prod) with appropriate configurations:

- **Dev**: More permissive deletion policies, auto-delete on stack removal
- **Prod**: Retain resources on stack deletion, enhanced backup/recovery

## License

Private - Internal use only

## Support

For issues or questions, contact the Sanders Platform team.