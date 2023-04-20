$awsProfileName = 'default';

# Put GoHighLevel values here. See: https://highlevel.stoplight.io/docs/integrations/6d8a9d06190b0-fa-qs
$clientId = '';
$clientSecret = '';
$accessToken = '';
$refreshToken = '';

# Create parameters in AWS Parameter Store
aws ssm put-parameter `
    --name '/GHL/Dev/CurlWisdom/RefreshToken' `
    --type 'SecureString' `
    --value ${refreshToken} `
    --profile ${awsProfileName} `
    --overwrite
;

aws ssm put-parameter `
    --name '/GHL/Dev/CurlWisdom/AccessToken' `
    --type 'SecureString' `
    --value ${accessToken} `
    --profile ${awsProfileName} `
    --overwrite
;

aws ssm put-parameter `
    --name '/GHL/Dev/CurlWisdom/ClientId' `
    --type 'SecureString' `
    --value ${clientId} `
    --profile ${awsProfileName} `
    --overwrite
;

aws ssm put-parameter `
    --name '/GHL/Dev/CurlWisdom/ClientSecret' `
    --type 'SecureString' `
    --value ${clientSecret} `
    --profile ${awsProfileName} `
    --overwrite
;
