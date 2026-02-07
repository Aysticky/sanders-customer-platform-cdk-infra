# Sanders Customer Platform CDK Infrastructure

AWS CDK infrastructure for the Sanders Customer Platform batch processing pipeline.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment Workflow](#deployment-workflow)
- [Verify Deployed Resources](#verify-deployed-resources)
- [Cost Management](#cost-management)
- [Usage](#usage)
- [Project Structure](#project-structure)

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

Bootstrap your AWS account for CDK (only needed once per account/region):

```bash
cdk bootstrap
```

## Deployment Workflow

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Aysticky/sanders-customer-platform-cdk-infra.git
cd sanders-customer-platform-cdk-infra

# Install Python dependencies
python -m uv pip install -r requirements.txt
```

### Step 2: Synthesize CloudFormation Template

Validate your CDK code by synthesizing the CloudFormation template:

```bash
cdk synth
```

### Step 3: Deploy Infrastructure

Deploy all resources to AWS:

```bash
cdk deploy --all
```

This will create:
- S3 bucket for data storage
- DynamoDB table for customer features
- ECR repository for Docker images
- VPC with public/private subnets and NAT Gateway
- AWS Batch compute environment, job queue, and job definitions
- Step Functions state machine for orchestration
- IAM roles with necessary permissions

Deployment takes approximately 2-3 minutes.

### Step 4: View Deployment Outputs

After successful deployment, note the outputs:

```
Outputs:
- S3BucketName: sanders-customer-platform-dev
- DynamoDBTableName: sanders_daily_customer_features_dev
- ECRRepositoryURI: 120569615884.dkr.ecr.eu-central-1.amazonaws.com/sanders-customer-platform-dev
- BatchJobQueueName: sanders-batch-queue-dev
- StepFunctionsStateMachineARN: arn:aws:states:eu-central-1:120569615884:stateMachine:sanders-orchestrator-dev
- VPCId: vpc-xxxxxxxxx
```

## Verify Deployed Resources

### Using AWS CLI

List all deployed resources:

```bash
# Disable pager for clean output
export AWS_PAGER=""

# View all stack outputs
aws cloudformation describe-stacks \
  --stack-name SandersCustomerPlatformStack-dev \
  --region eu-central-1 \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output text
```

### Using AWS Console

1. **CloudFormation**: https://console.aws.amazon.com/cloudformation/ - View stack details
2. **S3**: https://console.aws.amazon.com/s3/ - Search for `sanders-customer-platform-dev`
3. **DynamoDB**: https://console.aws.amazon.com/dynamodb/ - Click "Tables" to find `sanders_daily_customer_features_dev`
4. **ECR**: https://console.aws.amazon.com/ecr/ - Look for `sanders-customer-platform-dev`
5. **Batch**: https://console.aws.amazon.com/batch/ - View compute environments and job queues
6. **Step Functions**: https://console.aws.amazon.com/states/ - Find `sanders-orchestrator-dev`
7. **VPC**: https://console.aws.amazon.com/vpc/ - View your VPC and networking resources

## Cost Management

### Monthly Cost Estimate

**Always Running (24/7):**
- NAT Gateway: ~$32-35/month ($0.045/hour + data processing)

**Pay Per Use (Only when used):**
- S3: $0.023/GB/month + request costs
- DynamoDB (PAY_PER_REQUEST): $0.25 per million reads, $1.25 per million writes
- ECR: $0.10/GB/month for stored images
- Batch (Fargate): Only when jobs run (~$0.04/vCPU/hour + $0.004/GB/hour)
- Step Functions: $0.025 per 1,000 state transitions
- CloudWatch Logs: $0.50/GB ingested

**Free Resources:**
- VPC, Subnets, Route Tables, Internet Gateway, Security Groups, IAM Roles

### Cost Optimization Tips

1. **Delete NAT Gateway** if not needed for production (saves $32/month)
2. **Use S3 Lifecycle Policies** to move old data to cheaper storage tiers
3. **Enable DynamoDB auto-scaling** or reserved capacity for predictable workloads
4. **Clean up old ECR images** regularly
5. **Use CloudWatch alarms** to monitor unexpected usage

### Budget Setup

A budget configuration is included to set spending limits:

```bash
# Review budget configuration
cat budget-config.json

# Create budget (already configured for $10/month)
aws budgets create-budget --account-id YOUR-ACCOUNT-ID --budget file://budget-config.json

# Update existing budget limit
aws budgets update-budget --account-id YOUR-ACCOUNT-ID --new-budget file://budget-config.json
```

The budget tracks costs for resources tagged with `Project=sanders-customer-platform` and alerts when approaching the limit.

### View Current Costs

```bash
# View current month billing (requires Cost Explorer to be enabled)
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --region us-east-1
```

Or visit the AWS Billing Dashboard: https://console.aws.amazon.com/billing/

## Usage

### Working with ECR (Docker Images)
### Working with ECR (Docker Images)

Build and push your Docker image to ECR:

```bash
# Get ECR repository URI
ECR_URI=$(aws cloudformation describe-stacks \
  --stack-name SandersCustomerPlatformStack-dev \
  --region eu-central-1 \
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

### Working with S3

Upload data to the S3 bucket:

```bash
# Upload a file
aws s3 cp data.csv s3://sanders-customer-platform-dev/

# Upload a directory
aws s3 sync ./data/ s3://sanders-customer-platform-dev/data/

# List bucket contents
aws s3 ls s3://sanders-customer-platform-dev/
```

### Working with DynamoDB

Write and read data from DynamoDB:

```python
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('sanders_daily_customer_features_dev')

# Put item
table.put_item(
    Item={
        'customer_id': '12345',
        'date': '2026-02-07',
        'feature_1': 100,
        'feature_2': 'value'
    }
)

# Get item
response = table.get_item(
    Key={
        'customer_id': '12345',
        'date': '2026-02-07'
    }
)
print(response['Item'])
```

### Submitting Batch Jobs

Submit a job to AWS Batch:

```bash
# Submit a job using 8GB job definition
aws batch submit-job \
  --job-name my-feature-extraction-job \
  --job-queue sanders-batch-queue-dev \
  --job-definition sanders-job-8g \
  --region eu-central-1

# Check job status
aws batch describe-jobs --jobs <JOB-ID> --region eu-central-1
```

### Running Step Functions

Execute the state machine:

```bash
# Start execution
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:eu-central-1:120569615884:stateMachine:sanders-orchestrator-dev \
  --name execution-$(date +%s) \
  --input '{"param1":"value1"}' \
  --region eu-central-1

# List executions
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:eu-central-1:120569615884:stateMachine:sanders-orchestrator-dev \
  --region eu-central-1
```

### Infrastructure Management

Update stack after code changes:

```bash
# View what will change
cdk diff

# Deploy changes
cdk deploy --all

# Destroy all resources (WARNING: Deletes everything)
cdk destroy --all
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
├── cdk.json                        # CDK configuration with AZ context
├── requirements.txt                # Python dependencies (aws-cdk-lib, constructs)
├── pyproject.toml                  # Python project metadata
├── budget-config.json              # AWS Budget configuration ($10/month limit)
├── README.md                       # This file
├── Dockerfile.example              # Sample Dockerfile for Batch jobs
├── .gitignore                      # Git ignore patterns
├── cdk/
│   ├── __init__.py
│   ├── sanders_customer_platform_stack.py  # Main stack orchestrating all resources
│   └── constructs/                 # Reusable infrastructure components
│       ├── __init__.py
│       ├── s3_bucket.py            # S3 bucket with encryption
│       ├── dynamodb_table.py       # DynamoDB table with PAY_PER_REQUEST billing
│       ├── ecr_repository.py       # ECR repository for Docker images
│       ├── vpc_network.py          # VPC with public/private subnets
│       ├── batch_iam_roles.py      # IAM roles for Batch, ECS, and jobs
│       ├── batch_environment.py    # Batch compute, queue, and 3 job definitions
│       └── stepfunctions_statemachine.py  # Step Functions orchestration
└── tests/
    └── unit/
        ├── __init__.py
        └── test_sanders_stack.py   # Unit tests for CDK stack
```

## Batch Job Definitions

Three job definitions are created with different resource allocations:

| Job Definition | vCPU | Memory | Use Case |
|---------------|------|--------|----------|
| sanders-job-2g | 0.5 (512) | 2GB (2048 MB) | Light data processing |
| sanders-job-8g | 2 (2048) | 8GB (8192 MB) | Feature extraction |
| sanders-job-16g | 4 (4096) | 16GB (16384 MB) | Model training |

These are valid AWS Fargate vCPU/memory combinations.

These are valid AWS Fargate vCPU/memory combinations.

## Step Functions Workflow

The state machine orchestrates batch job execution:

1. **Parallel Execution**:
   - Feature Extraction Job (8GB memory, 2 vCPU)
   - Data Processing Job (2GB memory, 0.5 vCPU)
2. **Sequential Execution**:
   - Model Training Job (16GB memory, 4 vCPU) - runs after parallel jobs complete

Customize the workflow by modifying [stepfunctions_statemachine.py](cdk/constructs/stepfunctions_statemachine.py).

## Troubleshooting

### Git Bash PATH Issues

If commands like `aws`, `node`, or `cdk` are not found in Git Bash, the universal PATH loader should already be configured in `~/.bash_profile`. If not, run:

```bash
source ~/.bash_profile
```

This loads all Windows system PATH entries into Git Bash automatically.

### CDK Bootstrap Errors

If you see bootstrap-related errors, ensure:
1. Your IAM user has `AdministratorAccess` or equivalent permissions
2. Run `cdk bootstrap` before deploying

### Fargate vCPU/Memory Errors

The job definitions use validated Fargate combinations. If you modify them, refer to AWS Fargate documentation for valid vCPU/memory pairs.

### NAT Gateway Costs

To reduce costs during development, you can temporarily remove the NAT Gateway from [vpc_network.py](cdk/constructs/vpc_network.py) by setting `nat_gateways=0`. Note: Private subnets won't have internet access without NAT Gateway.

## Testing

Run unit tests:

```bash
pytest tests/ -v

# With coverage
pytest --cov=cdk tests/
```

## Security Notes

- All S3 buckets have encryption enabled and block public access
- DynamoDB has point-in-time recovery enabled for production
- ECR repositories scan images on push
- Batch jobs run in private subnets
- IAM roles follow least privilege principle

## Multi-Environment Support

The stack supports multiple environments (dev, prod) with appropriate configurations:

- **Dev**: Permissive deletion policies, auto-delete on stack removal, suitable for testing
- **Prod**: Retain resources on stack deletion, enhanced backup/recovery, production-ready

## Destroying Infrastructure

When you're done and want to remove all resources to stop incurring costs:

### Using CDK (Recommended)

```bash
# Destroy all resources created by the stack
cdk destroy --all

# Or destroy specific stack
cdk destroy SandersCustomerPlatformStack-dev
```

This will:
- Delete VPC, subnets, NAT Gateway, Internet Gateway
- Delete Batch compute environment, job queue, job definitions
- Delete Step Functions state machine
- Delete IAM roles
- Delete S3 bucket (if empty or configured with auto-delete)
- Delete DynamoDB table
- Delete ECR repository

### Important Notes

**Before destroying:**
1. **Backup data** from S3 and DynamoDB if needed
2. **Empty S3 bucket** manually if CDK fails to delete it
3. **Delete ECR images** if the repository fails to delete

**Manual cleanup (if needed):**

```bash
# Empty and delete S3 bucket manually
aws s3 rm s3://sanders-customer-platform-dev --recursive
aws s3 rb s3://sanders-customer-platform-dev

# Delete ECR images
aws ecr batch-delete-image \
  --repository-name sanders-customer-platform-dev \
  --image-ids imageTag=latest \
  --region eu-central-1

# Delete DynamoDB table manually (if needed)
aws dynamodb delete-table \
  --table-name sanders_daily_customer_features_dev \
  --region eu-central-1
```

**Cost Impact:**
- NAT Gateway stops charging immediately (saves ~$32/month)
- All other pay-per-use resources stop incurring costs
- S3 storage costs stop once bucket is empty

### Verify Deletion

```bash
# Verify stack is deleted
aws cloudformation describe-stacks \
  --stack-name SandersCustomerPlatformStack-dev \
  --region eu-central-1

# Should return: "Stack with id SandersCustomerPlatformStack-dev does not exist"
```

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS Batch Documentation](https://docs.aws.amazon.com/batch/)
- [AWS Step Functions Documentation](https://docs.aws.amazon.com/step-functions/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

## Contributing

This is an internal project. For changes or improvements:
1. Create a feature branch
2. Make your changes
3. Test with `cdk synth` and `cdk diff`
4. Submit for review

## License

Private - Internal use only

## Support

For issues or questions, contact the Sanders Platform team.