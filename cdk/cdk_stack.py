from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_applicationinsights as appinsights,
    aws_resourcegroups as rg,
    aws_ssm as ssm,
    core
)


class GoHighLevelStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create IAM role for Lambda functions
        lambda_role = iam.Role(
            self, "GhlLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaExecute"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess")
            ]
        )

        # Create IAM policy for Lambda logs
        lambda_logs_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            resources=["arn:aws:logs:*:*:*"]
        )

        # Create IAM policy for S3 access
        lambda_s3_policy = iam.PolicyStatement(
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
        lambda_s3_policy.add_resources("arn:aws:s3:::*")

        # Add policies to the IAM role
        lambda_role.add_to_policy(lambda_logs_policy)
        lambda_role.add_to_policy(lambda_s3_policy)

        # Create the REST API using API Gateway
        rest_api = apigw.RestApi(
            self, "GoHighLevelApi",
            rest_api_name="gohighlevel",
            deploy_options={
                "stage_name": stage
            }
        )

        # Create the Lambda function for refreshing tokens
        refresh_token_function = lambda_.Function(
            self, "GhlRefreshTokenFunction",
            code=lambda_.Code.from_asset("src"),
            handler="ghl_refresh_token.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            role=lambda_role,
            timeout=core.Duration.seconds(120),
            memory_size=128,
            description="Refreshes token as described here https://highlevel.stoplight.io/docs/integrations/00d0c0ecaa369-get-access-token. Stores new Access and Refresh Token in SSM Parameter Store",
            
        )

        # Add a schedule event to trigger the token refresh function
        # refresh_token_function.add_event_source(
        #     lambda_.events.Rule(
        #         self, "GhlRefreshTokenSchedule",
        #         schedule=lambda_.events.Schedule.rate(core.Duration.hours(23))
