$awsProfileName = 'default';

aws sns publish `
    --message "Test Alarm Message" `
    --topic-arn "arn:aws:sns:us-east-1:489440259680:dev-ghl-dignava-curlwisdom-Alarms" `
    --profile $awsProfileName;

    