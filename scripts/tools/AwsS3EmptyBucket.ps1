$awsProfileName = 'default';
$bucketName = 'test-489440259680';

aws s3 rm "s3://$bucketName" --recursive --profile $awsProfileName;
