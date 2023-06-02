import json
from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    Tags,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_lambda_event_sources as event_sources,
    aws_apigateway as apigw,
    aws_applicationinsights as appinsights,
    aws_resourcegroups as rg,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions
)
import boto3
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_s3 import ObjectLockMode
from aws_cdk.aws_sns_subscriptions import EmailSubscription

class GoHighLevelStack(Stack):

    @property
    def python_runtime(self):
        return self._python_runtime
    
    @property
    def lambda_architecture(self):
        return self._lambda_architecture
    
    def __init__(self, scope: Construct, config_file_path: str, **kwargs) -> None:
        
        config: dict = {}
        with open(config_file_path) as f:
            config = json.load(f)
        ghl_account_key = config['GhlAccountKey']
        ghl_subaccount_key = config['GhlSubAccountKey']
        stage = config.get('Stage', 'dev')
        is_prod = stage == 'prod'
        stage_prefix = '' if is_prod else f'{stage}-'
        aws_unique_name = f'{stage_prefix}ghl-{ghl_account_key}-{ghl_subaccount_key}'
        construct_id = aws_unique_name
        s3_bucket_config = config['S3Bucket']
        sns_config = config['Sns']

        super().__init__(scope, construct_id, **kwargs)

        self._python_runtime = lambda_.Runtime.PYTHON_3_9
        self._lambda_architecture = lambda_.Architecture.X86_64

        # Load other settings from config
        mailgun_api_url = config.get('MailGunApiUrl', 'https://api.mailgun.net/v3')
        mailgun_domain = config['MailGunDomain']

        # S3 bucket name should be unique around the world 
        # but we don't know the AWS Account ID until the deployment
        # So, use boto3 that relies on .aws [default] profile as a workaround here
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        aws_region = sts_client.meta.region_name
        if 'global' in aws_region:
            raise Exception(f'Wrong region: "{aws_region}". Please specify a region in ~/.aws/config')
        s3_bucket_name = f'{aws_unique_name}-{account_id}'
        
        ssm_base_path = f'/{aws_unique_name}'
        sqs_queue_prefix = aws_unique_name
        
        SQS_MAILGUN_EVENTS_QUEUE_NAME = 'mailgun-events'

        # Define Environment Variables for Lambda functions
        env_vars = {
            'GHL_BUCKET_NAME': s3_bucket_name,
            'TEMP_FOLDER': f'/tmp/{aws_unique_name}',
            'MAILGUN_API_URL': mailgun_api_url,
            'MAILGUN_DOMAIN': mailgun_domain,
            'SSM_BASE_PATH': ssm_base_path,
            'SQS_QUEUE_PREFIX': sqs_queue_prefix,
            'SQS_MAILGUN_EVENTS_QUEUE_NAME': SQS_MAILGUN_EVENTS_QUEUE_NAME
        }
        env_vars_json = json.dumps(env_vars, indent=4)

        print(f'Account ID = {account_id}')
        print(f'Region = {aws_region}')
        print(f'Added Env vars:\n{env_vars_json}')
        
        
        # Create IAM role for Lambda functions
        ghl_lambda_role = iam.Role(
            self, 'GhlLambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(scope=self, id='LambdaRole', managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaRole'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaExecute'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMFullAccess')
            ]
        )

        # Create IAM policy for Lambda logs
        cloudwatch_logs_policy = iam.PolicyStatement(
            sid='CloudWatchLogs',
            effect=iam.Effect.ALLOW,
            actions=[
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents',
                'logs:CreateLogDelivery',
                'logs:GetLogDelivery',
                'logs:UpdateLogDelivery',
                'logs:DeleteLogDelivery',
                'logs:ListLogDeliveries',
                'logs:PutResourcePolicy',
                'logs:DescribeResourcePolicies',
                'logs:DescribeLogGroups',
                'logs:DescribeLogStreams'
            ],
            resources=['arn:aws:logs:*:*:*']
        )

        # Create IAM policy for S3 Object access
        lambda_s3_object_policy = iam.PolicyStatement(
            sid='S3Object',
            effect=iam.Effect.ALLOW,
            actions=[
                's3:DeleteObjectTagging',
                's3:GetObjectRetention',
                's3:DeleteObjectVersion',
                's3:GetObjectAttributes',
                's3:PutObjectVersionTagging',
                's3:DeleteObjectVersionTagging',
                's3:PutObjectLegalHold',
                's3:PutObject',
                's3:GetObjectAcl',
                's3:GetObject',
                's3:PutObjectRetention',
                's3:GetObjectTagging',
                's3:PutObjectTagging',
                's3:DeleteObject',
                's3:GetObjectVersion'
            ],
            resources=[f'arn:aws:s3:::{s3_bucket_name}/*']
        )

        # Create IAM policy for S3 Bucket access
        lambda_s3_bucket_policy = iam.PolicyStatement(
            sid='S3Bucket',
            effect=iam.Effect.ALLOW,
            actions=[
                's3:CreateBucket',
                's3:PutBucketTagging',
                's3:GetBucketLogging',
                's3:ListBucket',
                's3:GetBucketLocation',
                's3:GetBucketPolicy'
            ],
            resources=[f'arn:aws:s3:::{s3_bucket_name}']
        )

        # Create IAM policy for Invoking Lambda Functions
        invoke_lambda_policy = iam.PolicyStatement(
            sid='InvokeLambdaPolicy',
            effect=iam.Effect.ALLOW,
            actions=[
                'lambda:InvokeFunction',
            ],
            resources=['*']
        )
        
        # Create IAM policy for SQSInvoking Lambda Functions
        sqs_process_messages_policy = iam.PolicyStatement(
            sid='SqsProcessMessagesPolicy',
            effect=iam.Effect.ALLOW,
            actions=[
                'sqs:SendMessage',
                'sqs:DeleteMessage',
                'sqs:GetQueueAttributes',
                'sqs:ReceiveMessage'
            ],
            resources=[f'arn:aws:sqs:{aws_region}:{account_id}:{sqs_queue_prefix}*']
        )
        

        # Add policies to the IAM role
        ghl_lambda_role.add_to_policy(cloudwatch_logs_policy)
        ghl_lambda_role.add_to_policy(lambda_s3_object_policy)
        ghl_lambda_role.add_to_policy(lambda_s3_bucket_policy)
        ghl_lambda_role.add_to_policy(invoke_lambda_policy)
        ghl_lambda_role.add_to_policy(sqs_process_messages_policy)


        # Create Client S3 bucket
        object_lock_retention = None
        object_lock_mode = s3_bucket_config.get('ObjectLockMode')
        print(f'ObjectLockMode = {object_lock_mode}')
        if object_lock_mode:
            # Retention Period: Use 'ObjectRetentionYears' if specified, otherwise use 'ObjectRetentionDays'
            object_retention_years_str = s3_bucket_config.get('ObjectRetentionYears')
            object_retention_days = 0
            if object_retention_years_str and int(object_retention_years_str) > 0:
                object_retention_days = int(object_retention_years_str) * 365
            else:
                object_retention_days = int(s3_bucket_config['ObjectRetentionDays'])
            # Create Governance or Compliance Lock retention policy
            if ObjectLockMode[object_lock_mode] == ObjectLockMode.GOVERNANCE:
                object_lock_retention = s3.ObjectLockRetention.governance(Duration.days(object_retention_days))
            elif ObjectLockMode[object_lock_mode] == ObjectLockMode.COMPLIANCE:
                print(f'WARNING!!! The configuration specifies ObjectLockMode = "{object_lock_mode}". You will be not able remove object or bucket after creation!!!')
                object_lock_retention = s3.ObjectLockRetention.compliance(Duration.days(object_retention_days))
            else:
                raise ValueError(f'ObjectLockMode has a wrong value = {object_lock_mode}')
        s3_bucket = s3.Bucket(
            self,
            id='GhlSubAccountBucket',
            bucket_name=s3_bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=False,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            object_lock_enabled=True,
            object_lock_default_retention=object_lock_retention
        )

        # Create the Lambda function for refreshing Access and Refresh tokens
        ghl_refresh_token_function = lambda_.Function(
            self, 
            id='GhlRefreshTokenFunction',
            code=lambda_.Code.from_asset('src'),
            handler='ghl_refresh_token.handler',
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(180),
            description='Refreshes token as described here https://highlevel.stoplight.io/docs/integrations/00d0c0ecaa369-get-access-token. Stores new Access and Refresh Token in SSM Parameter Store',
            architecture=self.lambda_architecture,
            environment=env_vars
        )

        # Add a schedule event to trigger the token refresh function
        refresh_token_schedule_rule = events.Rule(
            self, 
            id='GhlRefreshTokenSchedule',
            schedule=events.Schedule.rate(Duration.hours(23)),
            enabled=True,
            description='A schedule for getting new Access and Rerfresh Tokens from GoHighLevel'
        )
        refresh_token_schedule_rule.add_target(event_targets.LambdaFunction(ghl_refresh_token_function))


        # Create the Lambda function as a WebHook for Conversation Unread event
        ghl_hook_function = lambda_.Function(
            self, 
            id='GhlHookFunction',
            code=lambda_.Code.from_asset('src'),
            handler='ghl_hook.handler',
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(180),
            description='WebHook for SMS events',
            architecture=self.lambda_architecture,
            environment=env_vars,
        )

        # Create the REST API using API Gateway
        ghl_api = apigw.LambdaRestApi(
            self, 
            id='GoHighLevelApi',
            rest_api_name='gohighlevel',
            deploy_options={
                'stage_name': stage
            },
            endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL]),
            handler=ghl_hook_function
        )
        resource_ghl = ghl_api.root.add_resource('gohighlevel')
        resource_ghl.add_method('POST')


        # Create the Lambda function for MailGun polling
        mg_process_mailgun_events_function = lambda_.Function(
            self, 
            id='MgProcessMailgunEventsFunction',
            code=lambda_.Code.from_asset('src'),
            handler='mg_process_mailgun_events.handler',
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(900),
            description='Pulls events from MailGun and then push them into mailgun-events queue',
            architecture=self.lambda_architecture,
            environment=env_vars,
        )

        # Add a schedule event to trigger the mg_store_messages function
        mg_process_mailgun_events_schedule_rule = events.Rule(
            self,
            id='MgProcessMailgunEventsSchedule',
            schedule=events.Schedule.rate(Duration.minutes(15)),
            enabled=True,
            description='A schedule for polling MailGun to get messages from there'
        )
        mg_process_mailgun_events_schedule_rule.add_target(event_targets.LambdaFunction(mg_process_mailgun_events_function))


        # Create the Lambda function for process SQS queue with MailGun events
        mg_process_mailgun_events_queue_function = lambda_.Function(
            self, 
            id='MgProcessMailgunEventsQueueFunction',
            code=lambda_.Code.from_asset('src'),
            handler='mg_process_mailgun_events_queue.handler',
            runtime=self.python_runtime,
            role=ghl_lambda_role,
            timeout=Duration.seconds(300),
            description='Gets MailGun events from SQS queue and stores them to S3',
            architecture=self.lambda_architecture,
            environment=env_vars,
        )

        
        mailgun_events_dead_letter_queue = sqs.Queue(
            self,
            id='MailGunEventsDeadLetterQueue',
            queue_name=f'{sqs_queue_prefix}-{SQS_MAILGUN_EVENTS_QUEUE_NAME}-DL'
        )
        
        # Create an SQS queue
        mailgun_events_queue = sqs.Queue(
            self,
            id='MailGunEventsQueue',
            queue_name=f'{sqs_queue_prefix}-{SQS_MAILGUN_EVENTS_QUEUE_NAME}',
            visibility_timeout=Duration.seconds(300),
            receive_message_wait_time=Duration.seconds(20),
            # retention_period=Duration.days(4),
            # delivery_delay=Duration.seconds(0),
            # max_message_size_bytes=262144,  # 256 KiB
            dead_letter_queue=sqs.DeadLetterQueue(
                queue=mailgun_events_dead_letter_queue,
                max_receive_count=3
            )
        )

        mg_process_mailgun_events_queue_function.add_event_source(event_sources.SqsEventSource(
            queue=mailgun_events_queue,
            batch_size=1,
            max_batching_window=Duration.minutes(5),
            report_batch_item_failures=True
        ))


        # Alarms
        # ghl_refresh_token_error_alarm = cloudwatch.Alarm(
        #     self,
        #     id='GhlRefreshTokenErrorAlarm',
        #     alarm_name=f'GhlRefreshTokenErrors',
        #     alarm_description=f'Alarm if the SUM of Errors is greater than or equal to the threshold (1) for 1 evaluation period in "ghl_refresh_token_function"',
        #     metric=ghl_refresh_token_function.metric_errors(),
        #     threshold=1,
        #     comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        #     evaluation_periods=1
        # )
        # ghl_refresh_token_error_alarm.add_alarm_action(cloudwatch_actions.SnsAction(topic))

        # Resource group
        app_resource_group = rg.CfnGroup(
            self, 
            id='applicationResourceGroup',
            name=f'{construct_id}-Insights',
        )

        # Application Insights monitoring
        sns_alarms_topic = sns.Topic(
            self,
            id='SnsAlarmsTopic',
            topic_name=f'{construct_id}-Alarms',
            display_name='SNS topic for alarms from CloudWatch',
        )
        alarms_email = sns_config.get('AlarmsEmail')
        if alarms_email:
            sns_alarms_topic.add_subscription(EmailSubscription(alarms_email))

        appinsights.CfnApplication(
            self, 
            id='ApplicationInsightsMonitoring',
            resource_group_name=app_resource_group.name,
            auto_configuration_enabled=True,
            ops_center_enabled=True,
            ops_item_sns_topic_arn=sns_alarms_topic.topic_arn
        )

        
        # Tags
        Tags.of(self).add("Account", ghl_account_key)
        Tags.of(self).add("SubAccount", ghl_subaccount_key)
        Tags.of(self).add("Stage", stage)


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
            id='GhlLambdaIamRoleArn',
            value=ghl_lambda_role.role_arn,
            description='IAM Role for Lambda functions'
        )

        CfnOutput(
            self, 
            id='MgProcessMailgunEventsFunctionArn',
            value=mg_process_mailgun_events_function.function_arn,
            description='MgStoreMessages Lambda Function ARN'
        )

        CfnOutput(
            self, 
            id='MailGunQueueEventsUrl',
            value=mailgun_events_queue.queue_url,
            description='MailGun Events Queue URL'
        )

        CfnOutput(
            self, 
            id='SmsBasePath',
            value=ssm_base_path,
            description='SSM Parameter Store base path'
        )

        CfnOutput(
            self, 
            id='SqsQueuePrefix',
            value=sqs_queue_prefix,
            description='SQS Queue prefix for all queues'
        )

        CfnOutput(
            self, 
            id='EnvVars',
            value=env_vars_json,
            description='Environment variables added'
        )
