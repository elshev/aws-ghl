$awsProfileName = 'default';
$bucketName = 'test-489440259680';
$deleteBucket = True

aws s3 rm "s3://$bucketName" --recursive --profile $awsProfileName;

if ($deleteBucket) {
    aws s3 delete-bucket --bucket $bucketName --profile $awsProfileName;
}