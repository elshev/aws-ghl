$awsProfileName = 'default';
$buckets = @{
    'test-489440259680' = $false;
    'ghl-489440259680-curlwisdom' = $false;
    # 'ghl-489440259680-dfulfpb0vzwgurgr3ib3' = $true;
    # 'ghl-489440259680-none' = $true;
} 

foreach ($bucketName in $buckets.get_Keys()) {
    Write-Output "Bucket Name = $bucketName";
    aws s3 rm "s3://$bucketName" --recursive --profile $awsProfileName;

    $deleteBucket = $buckets[$bucketName]
    if ($deleteBucket) {
        Write-Output "Delete $bucketName bucket";
        aws s3api delete-bucket --bucket $bucketName --profile $awsProfileName;
    }
}
