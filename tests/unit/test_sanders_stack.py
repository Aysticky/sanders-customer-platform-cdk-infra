"""
Unit tests for Sanders Customer Platform Stack
"""
import aws_cdk as cdk
from aws_cdk.assertions import Template
from cdk.sanders_customer_platform_stack import SandersCustomerPlatformStack


def test_s3_bucket_created():
    """Test that S3 bucket is created"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert S3 bucket exists
    template.resource_count_is("AWS::S3::Bucket", 1)


def test_dynamodb_table_created():
    """Test that DynamoDB table is created with correct attributes"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert DynamoDB table exists
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
    # Check partition and sort keys
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST",
        "KeySchema": [
            {"AttributeName": "customer_id", "KeyType": "HASH"},
            {"AttributeName": "date", "KeyType": "RANGE"}
        ]
    })


def test_ecr_repository_created():
    """Test that ECR repository is created"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert ECR repository exists
    template.resource_count_is("AWS::ECR::Repository", 1)


def test_vpc_created():
    """Test that VPC is created"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert VPC exists
    template.resource_count_is("AWS::EC2::VPC", 1)


def test_batch_resources_created():
    """Test that Batch compute environment and queue are created"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert Batch resources exist
    template.resource_count_is("AWS::Batch::ComputeEnvironment", 1)
    template.resource_count_is("AWS::Batch::JobQueue", 1)
    # 3 job definitions (2g, 8g, 16g)
    template.resource_count_is("AWS::Batch::JobDefinition", 3)


def test_stepfunctions_created():
    """Test that Step Functions state machine is created"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert State Machine exists
    template.resource_count_is("AWS::StepFunctions::StateMachine", 1)


def test_iam_roles_created():
    """Test that IAM roles are created for Batch"""
    app = cdk.App()
    stack = SandersCustomerPlatformStack(
        app,
        "TestStack",
        environment="dev"
    )
    template = Template.from_stack(stack)
    
    # Assert IAM roles exist (3 for Batch + 1 for Step Functions)
    template.resource_count_is("AWS::IAM::Role", 4)
