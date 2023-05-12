$awsProfileName = 'default';

function PrintSsmValue($paramName) {
    $name = ($paramName -split '/')[-1]
    $hashTable = aws ssm get-parameter `
        --name $paramName `
        --with-decryption `
        --profile $awsProfileName `
    | ConvertFrom-Json -AsHashtable;
    
    $value = $hashTable.Parameter['Value'];
    Write-Output "${name}: ${value}"
}

# Get GoHighLevel parameters. See: https://highlevel.stoplight.io/docs/integrations/6d8a9d06190b0-fa-qs
PrintSsmValue '/GHL/Dev/CurlWisdom/AccessToken';
# PrintSsmValue '/GHL/Dev/CurlWisdom/RefreshToken';
# PrintSsmValue '/GHL/Dev/CurlWisdom/ClientId';
# PrintSsmValue '/GHL/Dev/CurlWisdom/ClientSecret';
# PrintSsmValue '/GHL/Dev/CurlWisdom/MailGunApiKey';
