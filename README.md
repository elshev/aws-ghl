# aws-ghl
GoHighLevel integration with AWS

## AWS Setup
* Setup AWS User
  * Sign in to your AWS account
  * Go to the AWS IAM console and create a new user.
  * Type a name for your user (e.g. `cicd`) and choose `Programmatic access`.
  * Click `Next: Permissions` to continue to the next step.
  * Click `Attach existing policies directly` and choose `AdministratorAccess`.
  * Click `Next: Review`
  * Click `Next: Tags`
  * Click `Create User`
  * In the next screen, you’ll see your `Access key ID` and you will have the option to click `Show` to show the `Secret access key`. Store these credentials in a safe place.


## Linux Dev Setup (Amazon Linux 2023)

* Note! [dignava-dev1](https://dignava-dev1.signin.aws.amazon.com/console) AWS Account already has `deploy-base` EC2 instance which was set up using the steps below.

* Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
```
cd ~
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

* Install NodeJS and AWS-CDK
```
sudo yum install nodejs
sudo npm install -g aws-cdk
```

* Install Python 3.9 on your machine
```
sudo yum install gcc openssl-devel bzip2-devel libffi-devel
cd /opt
sudo wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
sudo tar xzf Python-3.9.16.tgz
cd Python-3.9.16
sudo ./configure --enable-optimizations
sudo yum -y install zlib-devel
sudo make altinstall
sudo rm -f /opt/Python-3.9.16.tgz
python3.9 -V
cd ~
```

* Configure your AWS credentials
```
# Run `aws configure` and enter access keys for your user:
# AWS Access Key ID [None]: `<Access key ID here>`
# AWS Secret Access Key [None]: `<Secret Access Key here>`
# Default region name [None]: `us-east-1`
# Default output format [None]: `<leave blank>`
aws configure
```    

* Install GitHub and get [aws-ghl](https://github.com/dignava/aws-ghl) repo 
```
sudo yum -y install git-all
# Manual steps:
# Generate ssh keys for GitHub or upload id_rsa.pub to ~/.ssh dir
# ssh-keygen -t rsa -b 4096 -C "email@example.com"
# Add id_rsa.pub to GitHub -> Settings -> Keys
eval "$(ssh-agent -s)"
ssh -T git@github.com
git clone git@github.com:dignava/aws-ghl.git
```

* Create a virtual environment
```
cd aws-ghl
python3.9 -m venv env
source env/bin/activate
```  

* Install AWS CDK
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
cdk bootstrap
```

* Deploy CDK Stack to AWS
```
# Note! The next command will deploy to AWS using the command from cdk.json
# Example: python app.py --config ./cdk/config/config-curlwisdom-dev.json
# Please, verify a config file to understand what it will deploy
cdk deploy
```

## Windows Dev Setup

* Dev setup is described for VSCode which has to be installed on your machine

* Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

* Install [NodeJs](https://nodejs.org/en/download)

* Install `aws-cdk` package. Open Terminal and run:
```
npm install -g aws-cdk
```

* Install [Python 3.9.13+](https://www.python.org/downloads/release/python-3913/) on your machine

* Configure your AWS credentials Locally
  * Open a terminal window
  * Type: `aws configure` to set up your environment.
    * AWS Access Key ID [None]: `<Access key ID here>`
    * AWS Secret Access Key [None]: `<Secret Access Key here>`
    * Default region name [None]: `us-east-1`
    * Default output format [None]: `<leave blank>`

* Get repo from [GitHub](https://github.com/dignava/aws-ghl)
```
git clone git@github.com:dignava/aws-ghl.git
```

* Open VSCode
  * Run terminal window
  * Go to the root project folder and run VSCode: 
```
cd aws-ghl
code .
```

* In VSCode create `.venv`
  * Ctrl+Shift+P -> Create Environment -> venv
  * Select `Python 3.9`
  * Open new Terminal window in VSCode. You should seee (.venv) prompt

* AWS CDK
  * In Terminal Window:
```  
# Install AWS CDK and dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
# Bootstrap
cdk bootstrap
```

* Deploy CDK Stack to AWS
```
# Note! The next command will deploy to AWS using the command from cdk.json
# Example: python app.py --config ./cdk/config/config-curlwisdom-dev.json
# Please, verify a config file to understand what it will deploy
cdk deploy
```

