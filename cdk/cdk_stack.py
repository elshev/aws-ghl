from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_apigateway as apigw,
    aws_applicationinsights as appinsights,
    aws_resourcegroups as rg,
)


class GoHighLevelStack(Stack):

    @property
    def python_runtime(self):
        return self._python_runtime

    def __init__(self, scope: Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._python_runtime = _lambda.Runtime.PYTHON_3_9

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
        lambda_logs_policy = iam.PolicyStatement(
            sid='LambdaLogs',
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
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

        # Add policies to the IAM role
        ghl_lambda_role.add_to_policy(lambda_logs_policy)
        ghl_lambda_role.add_to_policy(lambda_s3_object_policy)
        ghl_lambda_role.add_to_policy(lambda_s3_bucket_policy)

        # Add a schedule event to trigger the token refresh function
        refresh_token_schedule_rule = events.Rule(
            self, 'GhlRefreshTokenSchedule',
            schedule=events.Schedule.rate(Duration.hours(23)),
            enabled=True,
            description='A schedule for getting new Access and Rerfresh Tokens from GoHighLevel'
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
            architecture=_lambda.Architecture.X86_64
        )

        # Create the REST API using API Gateway
        ghl_api = apigw.LambdaRestApi(
            self, "GoHighLevelApi",
            rest_api_name="gohighlevel",
            deploy_options={
                "stage_name": stage
            },
            endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL]),
            handler=ghl_hook_function
        )

        resource_ghl = ghl_api.root.add_resource('gohighlevel')
        resource_ghl.add_method('POST')

        # Resource group
        app_resource_group = rg.CfnGroup(
            self, 'applicationResourceGroup',
            name=f'{construct_id}-ApplicationInsights',
        )

        # Application Insights monitoring
        appinsights.CfnApplication(
            self, 'ApplicationInsightsMonitoring',
            resource_group_name=app_resource_group.name,
            auto_configuration_enabled=True
        )

        # Outputs
        CfnOutput(
            self, 'GoHighLevelApiUrl',
            value=ghl_api.url_for_path('/'),
            description='API Gateway endpoint URL for GhlHook function'
        )

        CfnOutput(
            self, 'GhlRefreshTokenFunctionArn',
            value=ghl_refresh_token_function.function_arn,
            description='GhlRefreshToken Lambda Function ARN'
        )

        CfnOutput(
            self, 'GhlRefreshTokenFunctionIamRoleArn',
            value=ghl_refresh_token_function.role.role_arn,
            description='IAM Role for GhlHook function'
        )

        CfnOutput(
            self, 'GhlHookFunctionArn',
            value=ghl_hook_function.function_arn,
            description='GhlHook Lambda Function ARN'
        )

        CfnOutput(
            self, 'GhlHookFunctionIamRoleArn',
            value=ghl_hook_function.role.role_arn,
            description='IAM Role for GhlHook function'
        )
