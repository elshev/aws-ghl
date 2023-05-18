# Run Example: 
# ./scripts/tools/AwsSsmGetParams.ps1 ./cdk/config/config-curlwisdom-dev.json
Param(
    [String] $configFile
)
 
$ErrorActionPreference = "Stop"

$awsProfileName = 'default';

# Read settings from config file
if (! $configFile){
    $configFile = './cdk/config/config-curlwisdom-dev.json';
}
$json = Get-Content $configFile | Out-String | ConvertFrom-Json;
$stage = $json.Stage;
$ghlAccountKey = $json.GhlAccountKey;
$ghlSubaccountKey = $json.ghlSubaccountKey;

$ssmStoreParameterPath = "/${stage}-ghl-${ghlAccountKey}-${ghlSubaccountKey}"

function PrintSsmValue($name) {
    $path = "${ssmStoreParameterPath}/$name"
    $hashTable = aws ssm get-parameter `
        --name $path `
        --with-decryption `
        --profile $awsProfileName `
    | ConvertFrom-Json -AsHashtable;
    
    $value = $hashTable.Parameter['Value'];
    Write-Output "${name}: ${value}"
}


# Get GoHighLevel parameters. See: https://highlevel.stoplight.io/docs/integrations/6d8a9d06190b0-fa-qs
PrintSsmValue 'AccessToken';
PrintSsmValue 'RefreshToken';
PrintSsmValue 'ClientId';
PrintSsmValue 'ClientSecret';
PrintSsmValue 'MailGunApiKey';
