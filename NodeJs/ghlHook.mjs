// eslint-disable-next-line no-redeclare
/* global fetch */
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

const s3Client = new S3Client({ region: 'us-east-1' });

const apiToken = 'REPLACE_ACCESS_TOKEN_HERE';

export const timeToStr = (time) => {
  const timeValue = time && time instanceof Date ? time : new Date();
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  };
  const formatter = new Intl.DateTimeFormat('en-US', options);
  const formattedDate = formatter.format(timeValue);
  const dateString = formattedDate.replace(/\D/g, '-');
  return dateString;
};

export const writeToS3 = async (content) => {
  const bucketName = 'test-489440259680';
  const keyName = `${timeToStr()}.txt`;

  const commandParams = {
    Bucket: bucketName,
    Key: keyName,
    Body: content,
  };

  try {
    console.log('Starting S3.putObject...');
    const command = new PutObjectCommand(commandParams);
    const data = await s3Client.send(command);
    console.log(`Successfully saved object to ${bucketName}/${keyName}`);
    console.log(`Data returned: ${data.toString()}`);
  } catch (err) {
    console.log(err);
  }
  return keyName;
};

const request = async (path, options) => {
  const hostname = 'https://services.leadconnectorhq.com';
  const url = hostname + path;
  const response = await fetch(url, options);
  if (!response.ok) {
    console.error('Network response was not ok');
    return {
      statusCode: response.status,
      body: JSON.stringify({ message: 'Internal Server Error' }),
    };
  }
  return {
    statusCode: response.status,
    body: await response.text(),
  };
};

export const handler = async (event) => {
  const payload = event.body ? event.body : event;
  console.log(`Payload:\n${JSON.stringify(payload, null, 2)}`);
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiToken}`,
      Version: '2021-04-15',
    },
  };
  const path = '/conversations/9325cLcgqmhJVyfITS7g';
  const content = await request(path, options);
  const keyName = await writeToS3(content.body);
  console.log(`S3 Key: ${keyName}`);
  return keyName;
};
