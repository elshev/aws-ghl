import json
from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_apigateway as apigw,
    aws_applicationinsights as appinsights,
    aws_resourcegroups as rg,
    aws_sqs as sqs,
)
import boto3


class GoHighLevelStack(Stack):

    @property
    def python_runtime(self):
        return self._python_runtime

    def __init__(self, scope: Construct, config_file_path: str, **kwargs) -> None:
        
        config_json: dict = {}
        with open(config_file_path) as f:
            config_json = json.load(f)
        ghl_account_key = config_json['GhlAccountKey']
        ghl_subaccount_key = config_json['GhlSubAccountKey']
        stage = config_json.get('Stage', 'dev')
        is_prod = stage == 'prod'
        stage_suffix = '' if is_prod else f'-{stage}'
        construct_id = f'ghl-{ghl_account_key}-{ghl_subaccount_key}{stage_suffix}'

        super().__init__(scope, construct_id, **kwargs)

        self._python_runtime = _lambda.Runtime.PYTHON_3_9

        # Load other settings from config
        aws_bucket_region = config_json.get('AwsBucketRegion', 'us-east-1')
        mailgun_api_url = config_json.get('MailGunApiUrl', 'https://api.mailgun.net/v3')
        mailgun_domain = config_json['MailGunDomain']

        # S3 bucket name should be unique around the world 
        # but we don't know the AWS Account ID until the deployment
        # So, use boto3 that relies on .aws [default] profile as a workaround here
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        s3_bucket_name = f'ghl-{account_id}-{ghl_subaccount_key}{stage_suffix}'
        ssm_parameter_store_path = f'/{stage}/ghl/{ghl_account_key}/{ghl_subaccount_key}'
        
        # Define Environment Variables for Lambda functions
        env_vars = {
            'GHL_BUCKET_NAME': s3_bucket_name,
            'TEMP_FOLDER': f'/tmp/ghl-{ghl_account_key}-{ghl_subaccount_key}',
            'AWS_BUCKET_REGION': aws_bucket_region,
            'MAILGUN_API_URL': mailgun_api_url,
            'MAILGUN_DOMAIN': mailgun_domain,
            'SSM_PARAMETER_STORE_PATH': ssm_parameter_store_path
        }
        
        # Create IAM role for Lambda functions
        ghl_lambda_role = iam.Role(
            self, "GhlLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(scope=self, id='LambdaRole', managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaRole'),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaExecute"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess")
            ]
        )

        # Create IAM policy for Lambda logs
        cloudwatch_logs_policy = iam.PolicyStatement(
            sid='CloudWatchLogs',
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:CreateLogDelivery",
                "logs:GetLogDelivery",
                "logs:UpdateLogDelivery",
                "logs:DeleteLogDelivery",
                "logs:ListLogDeliveries",
                "logs:PutResourcePolicy",
                "logs:DescribeResourcePolicies",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams"
            ],
            resources=["arn:aws:logs:*:*:*"]
        )

        # Create IAM policy for S3 Object access
        lambda_s3_object_policy = iam.PolicyStatement(
            sid='S3Object',
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:DeleteObjectTagging",
                "s3:GetObjectRetention",
                "s3:DeleteObjectVersion",
                "s3:GetObjectAttributes",
                "s3:PutObjectVersionTagging",
                "s3:DeleteObjectVersionTagging",
                "s3:PutObjectLegalHold",
                "s3:PutObject",
                "s3:GetObjectAcl",
                "s3:GetObject",
                "s3:PutObjectRetention",
                "s3:GetObjectTagging",
                "s3:PutObjectTagging",
                "s3:DeleteObject",
                "s3:GetObjectVersion"
            ],
            resources=["arn:aws:s3:::*/*"]
        )

        # Create IAM policy for S3 Bucket access
        lambda_s3_bucket_policy = iam.PolicyStatement(
            sid='S3Bucket',
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:PutBucketTagging",
                "s3:GetBucketLogging",
                "s3:ListBucket",
                "s3:GetBucketLocation",
                "s3:GetBucketPolicy"
            ],
            resources=["arn:aws:s3:::*"]
        )

        # Create IAM policy for Invoking Lambda Functions
        invoke_lambda_policy = iam.PolicyStatement(
            sid='InvokeLambdaPolicy',
            effect=iam.Effect.ALLOW,
            actions=[
                "lambda:InvokeFunction",
            ],
            resources=["*"]
        )
        
        # Create IAM policy for SQSInvoking Lambda Functions
        sqs_process_messages_policy = iam.PolicyStatement(
            sid='SqsProcessMessagesPolicy',
            effect=iam.Effect.ALLOW,
            actions=[
                "sqs:SendMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:ReceiveMessage"
            ],
            resources=["arn:aws:sqs:::ghl_*"]
        )
        

        # Add policies to the IAM role
        ghl_lambda_role.add_to_policy(cloudwatch_logs_policy)
        ghl_lambda_role.add_to_policy(lambda_s3_object_policy)
        ghl_lambda_role.add_to_policy(lambda_s3_bucket_policy)
        ghl_lambda_role.add_to_policy(invoke_lambda_policy)
        ghl_lambda_role.add_to_policy(sqs_process_messages_policy)

        # Create Client S3 bucket
        s3_bucket = s3.Bucket(
            self,
            id='GhlClientBucket',
            bucket_name=s3_bucket_name
        )

        # Create an SQS queue
        queue = sqs.Queue(
            self,
            id='MyQueue',
            queue_name='mailgun-events',
            visibility_timeout=Duration.seconds(300)
        )

        # Create the Lambda function for refreshing Access and Refresh tokens
        ghl_refresh_token_function = _lambda.Function(
            self, "GhlRefreshTokenFunction",
            code=_lambda.Code.from_asset("src"),
            handler="ghl_refresh_token.lambda_handler",
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(180),
            description="Refreshes token as described here https://highlevel.stoplight.io/docs/integrations/00d0c0ecaa369-get-access-token. Stores new Access and Refresh Token in SSM Parameter Store",
            architecture=_lambda.Architecture.X86_64,
        )

        # Add a schedule event to trigger the token refresh function
        refresh_token_schedule_rule = events.Rule(
            self, 'GhlRefreshTokenSchedule',
            schedule=events.Schedule.rate(Duration.hours(23)),
            enabled=True,
            description='A schedule for getting new Access and Rerfresh Tokens from GoHighLevel'
        )
        refresh_token_schedule_rule.add_target(event_targets.LambdaFunction(ghl_refresh_token_function))


        # Create the Lambda function as a WebHook for Conversation Unread event
        ghl_hook_function = _lambda.Function(
            self, "GhlHookFunction",
            code=_lambda.Code.from_asset("src"),
            handler="ghl_hook.lambda_handler",
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(180),
            description="WebHook for GoHighLevel ConversationUnread event",
            architecture=_lambda.Architecture.X86_64,
            environment=env_vars,
        )

        # Create the REST API using API Gateway
        ghl_api = apigw.LambdaRestApi(
            self, 
            id="GoHighLevelApi",
            rest_api_name="gohighlevel",
            deploy_options={
                "stage_name": stage
            },
            endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL]),
            handler=ghl_hook_function
        )
        resource_ghl = ghl_api.root.add_resource('gohighlevel')
        resource_ghl.add_method('POST')


        # Create the Lambda function for MailGun polling
        mg_store_messages_function = _lambda.Function(
            self, 
            id="MgStoreMessagesFunction",
            code=_lambda.Code.from_asset("src"),
            handler="mg_store_messages.handler",
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(300),
            description="Gets events from MailGun and then stores messages to S3 bucket",
            architecture=_lambda.Architecture.X86_64,
            environment=env_vars,
        )

        # Add a schedule event to trigger the mg_store_messages function
        mg_store_messages_schedule_rule = events.Rule(
            self, 'MgStoreMessagesSchedule',
            schedule=events.Schedule.rate(Duration.hours(6)),
            enabled=True,
            description='A schedule for polling MailGun, getting messages from there, and store them in S3'
        )
        mg_store_messages_schedule_rule.add_target(event_targets.LambdaFunction(mg_store_messages_function))



        # Resource group
        app_resource_group = rg.CfnGroup(
            self, 
            id='applicationResourceGroup',
            name=f'{construct_id}-ApplicationInsights',
        )

        # Application Insights monitoring
        appinsights.CfnApplication(
            self, 
            id='ApplicationInsightsMonitoring',
            resource_group_name=app_resource_group.name,
            auto_configuration_enabled=True
        )

        # Outputs
        CfnOutput(
            self, 
            id='GoHighLevelApiUrl',
            value=ghl_api.url_for_path('/'),
            description='API Gateway endpoint URL for GhlHook function'
        )

        CfnOutput(
            self, 
            id='S3BucketArn',
            value=s3_bucket.bucket_arn,
            description='S3 Client Bucket ARN'
        )

        CfnOutput(
            self, 
            id='GhlRefreshTokenFunctionArn',
            value=ghl_refresh_token_function.function_arn,
            description='GhlRefreshToken Lambda Function ARN'
        )

        CfnOutput(
            self, 
            id='GhlRefreshTokenFunctionIamRoleArn',
            value=ghl_refresh_token_function.role.role_arn,
            description='IAM Role for GhlHook function'
        )

        CfnOutput(
            self, 
            id='GhlHookFunctionArn',
            value=ghl_hook_function.function_arn,
            description='GhlHook Lambda Function ARN'
        )

        CfnOutput(
            self, 
            id='GhlHookFunctionIamRoleArn',
            value=ghl_hook_function.role.role_arn,
            description='IAM Role for GhlHook function'
        )

        CfnOutput(
            self, 
            id='MgStoreMessagesFunctionArn',
            value=mg_store_messages_function.function_arn,
            description='MgStoreMessages Lambda Function ARN'
        )

        CfnOutput(
            self, 
            id='MgStoreMessagesFunctionIamRoleArn',
            value=mg_store_messages_function.role.role_arn,
            description='IAM Role for MgStoreMessages function'
        )
