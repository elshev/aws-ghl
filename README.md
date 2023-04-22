# aws-ghl
GoHighLevel integration with AWS

aws-ghl Dev Setup
-----------------
* Dev setup is described for VSCode which has to be installed on your machine
* Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* Install [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
* Install Python 3.9 on your machine
* Setup AWS User
  * Sign in to your AWS account
  * Go to the AWS IAM console and create a new user.
  * Type a name for your user (e.g. `ghl-integration`) and choose `Programmatic access`.
  * Click `Next: Permissions` to continue to the next step.
  * Click `Attach existing policies directly` and choose `AdministratorAccess`.
  * Click `Next: Review`
  * Click `Next: Tags`
  * Click `Create User`
  * In the next screen, you’ll see your `Access key ID` and you will have the option to click `Show` to show the `Secret access key`. Store these credentials temporarily.
* Configure your AWS credentials Locally
  * Open a terminal window
  * Type: 'aws configure' to set up your environment.
    * AWS Access Key ID [None]: `<Access key ID here>`
    * AWS Secret Access Key [None]: `<Secret Access Key here>`
    * Default region name [None]: `us-east-1`
    * Default output format [None]: `<leave blank>`
* Get repo from [GitHub](https://github.com/dignava/aws-ghl)
* Open VSCode
  * Run terminal window
  * Go to the root project folder: `cd aws-ghl`
  * Run VSCode: `code .`
* Note! All steps are supposed to be done from the root project folder
* In VSCode create `.venv`
  * Ctrl+Shift+P -> Create Environment -> venv
  * Select `Python 3.9`
  * Open new Terminal window in VSCode. You should seee (.venv) prompt
* AWS CDK
  * Open a terminal window in root
  * Install AWS CDK: `python -m pip install aws-cdk-lib`
  * Bootstrap: `cdk bootstrap`
