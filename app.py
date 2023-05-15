#!/usr/bin/env python3

from argparse import ArgumentParser
import aws_cdk as cdk
from cdk.cdk_stack import GoHighLevelStack

parser = ArgumentParser()
parser.add_argument(
    '-c', 
    '--config_file',
    help='Configuration file with deployment settings',
)
args = parser.parse_args()
config_file_path = args.config_file
print(f'Configuration file: {config_file_path}')

app = cdk.App()

GoHighLevelStack(app, config_file_path=config_file_path)

app.synth()
