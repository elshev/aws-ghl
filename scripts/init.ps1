$awsProfileName = 'default';

## Secret Values here
# Put GoHighLevel values here. See: https://highlevel.stoplight.io/docs/integrations/6d8a9d06190b0-fa-qs
$clientId = '';
$clientSecret = '';
$accessToken = '';
$refreshToken = '';
# MailGun
$mailgunApiKey = '';

function PutParameter($name, $value, $type) {
    if ($value) {
        Write-Output "Put '$type' parameter '${name}' = '${value}' ...";
        aws ssm put-parameter `
            --name ${name} `
            --type $type `
            --value ${value} `
            --profile ${awsProfileName} `
            --overwrite
        ;
    } else {
        Write-Output "Skipping parameter ${name} because its value is empty...";
    }

}

# Create parameters in AWS Parameter Store
PutParameter -name '/GHL/Dev/CurlWisdom/RefreshToken' -value ${refreshToken} -type 'SecureString';
PutParameter -name '/GHL/Dev/CurlWisdom/AccessToken' -value ${accessToken} -type 'SecureString';
PutParameter -name '/GHL/Dev/CurlWisdom/ClientId' -value ${clientId} -type 'SecureString';
PutParameter -name '/GHL/Dev/CurlWisdom/ClientSecret' -value ${clientSecret} -type 'SecureString';

PutParameter -name '/GHL/Dev/CurlWisdom/MailGunApiKey' -value ${mailgunApiKey} -type 'SecureString';
