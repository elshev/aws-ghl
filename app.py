#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.cdk_stack import GoHighLevelStack


app = cdk.App()
GoHighLevelStack(app, "cdk-ghl", 'dev')

app.synth()
