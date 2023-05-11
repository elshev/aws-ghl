$awsProfileName = 'default';
$bucketName = 'ghl-489440259680-dfulfpb0vzwgurgr3ib3';
$bucketName = 'ghl-489440259680-none';
$deleteBucket = $true

aws s3 rm "s3://$bucketName" --recursive --profile $awsProfileName;

if ($deleteBucket) {
    aws s3api delete-bucket --bucket $bucketName --profile $awsProfileName;
}