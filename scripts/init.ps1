# Run Example: 
# ./scripts/Init.ps1 ./cdk/config/config-curlwisdom-dev.json
Param(
    [Parameter(Mandatory=$True)][String] $configFile
)
 
$ErrorActionPreference = "Stop"

$awsProfileName = 'default';

## Secret Values here
# Put GoHighLevel values here. See: https://highlevel.stoplight.io/docs/integrations/6d8a9d06190b0-fa-qs
$clientId = '';
$clientSecret = '';
$accessToken = '';
$refreshToken = '';
# MailGun
$mailgunApiKey = '';

# Read settings from config file
$json = Get-Content $configFile | Out-String | ConvertFrom-Json
$stage = $json.Stage
$ghlAccountKey = $json.GhlAccountKey
$ghlSubaccountKey = $json.ghlSubaccountKey

$ssmStoreParameterPath = "/${stage}/ghl/${ghlAccountKey}/${ghlSubaccountKey}"

function PutParameter($name, $value, $type) {
    $path = "${ssmStoreParameterPath}/$name"
    if ($value) {
        Write-Output "Put '$type' parameter '${path}' = '${value}' ...";
        aws ssm put-parameter `
            --name ${path} `
            --type $type `
            --value ${value} `
            --profile ${awsProfileName} `
            --overwrite
        ;
    } else {
        Write-Output "Skipping parameter ${path} because its value is empty...";
    }

}

# Create parameters in AWS Parameter Store
PutParameter -name 'RefreshToken' -value ${refreshToken} -type 'SecureString';
PutParameter -name 'AccessToken' -value ${accessToken} -type 'SecureString';
PutParameter -name 'ClientId' -value ${clientId} -type 'SecureString';
PutParameter -name 'ClientSecret' -value ${clientSecret} -type 'SecureString';

PutParameter -name 'MailGunApiKey' -value ${mailgunApiKey} -type 'SecureString';
