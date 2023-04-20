$profileName = 'default';

# Create parameters in AWS Parameter Store
aws ssm put-parameter `
    --name "/GHL/Dev/CurlWisdom/AccessToken" `
    --type "String" `
    --value "PUT_ACCESS_TOKEN_HERE" `
    --profile ${profileName} `
    --overwrite
;

aws ssm put-parameter `
    --name "/GHL/Dev/CurlWisdom/RefreshToken" `
    --type "String" `
    --value "PUT_REFRESH_TOKEN_HERE" `
    --profile ${profileName} `
    --overwrite
;
