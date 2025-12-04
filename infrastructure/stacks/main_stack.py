from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
from constructs import Construct
import os


class MainStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB Table for Events
        events_table = dynamodb.Table(
            self,
            "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For development - change for production
            point_in_time_recovery=True,
        )
        
        # DynamoDB Table for Registration System (single-table design)
        registration_table = dynamodb.Table(
            self,
            "RegistrationTable",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For development - change for production
            point_in_time_recovery=True,
        )
        
        # Add GSI for querying by user
        registration_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # Lambda Function with bundled dependencies
        api_lambda = lambda_.Function(
            self,
            "EventApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../../backend"),
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && " +
                        "cp -r *.py /asset-output/ && " +
                        "cp -r registration /asset-output/"
                    ],
                }
            ),
            environment={
                "EVENTS_TABLE_NAME": events_table.table_name,
                "REGISTRATION_TABLE_NAME": registration_table.table_name,
            },
            timeout=Duration.seconds(30),
            memory_size=512,
        )
        
        # Grant Lambda permissions to access DynamoDB
        events_table.grant_read_write_data(api_lambda)
        registration_table.grant_read_write_data(api_lambda)
        
        # API Gateway REST API
        api = apigateway.RestApi(
            self,
            "EventManagementApi",
            rest_api_name="Event Management API",
            description="REST API for Event Management",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["*"],
                allow_credentials=True,
            ),
        )
        
        # Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            api_lambda,
            proxy=True,
        )
        
        # Add proxy resource to handle all paths
        api.root.add_proxy(
            default_integration=lambda_integration,
            any_method=True,
        )
        
        # Outputs
        CfnOutput(
            self,
            "ApiUrl",
            value=api.url,
            description="Event Management API URL",
            export_name="EventManagementApiUrl"
        )
        
        CfnOutput(
            self,
            "EventsTableName",
            value=events_table.table_name,
            description="DynamoDB Events Table Name",
            export_name="EventsTableName"
        )
        
        CfnOutput(
            self,
            "LambdaFunctionName",
            value=api_lambda.function_name,
            description="Lambda Function Name",
            export_name="EventApiFunctionName"
        )
        
        CfnOutput(
            self,
            "RegistrationTableName",
            value=registration_table.table_name,
            description="DynamoDB Registration Table Name",
            export_name="RegistrationTableName"
        )
