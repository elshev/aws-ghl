import { handler } from './ghlHook.mjs';

const runHandler = async (event) => {
  let result;
  try {
    const response = await handler(event);
    console.log(`Status Code = ${response.statusCode}`);
    try {
      const responseObject = JSON.parse(response.body);
      result = JSON.stringify(responseObject, null, 2);
      console.log('Body:');
      console.log(result);
    } catch (error) {
      console.error(`JSON parsing error: ${error}`);
    }
  } catch (error) {
    console.error(error);
  }
  return result;
};

const eventBody = {
  type: 'ContactCreate',
  locationId: 'locacion123',
  id: 'id12345',
  email: 'mail@example.com',
  country: 'US',
  firstName: 'John',
  lastName: 'Testoff',
};

const event = JSON.stringify({
  resource: '/gohighlevel',
  path: '/gohighlevel',
  httpMethod: 'POST',
  headers: {
    Accept: 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=utf-8',
    Host: 'sxmz4whd3h.execute-api.us-east-1.amazonaws.com',
    'User-Agent': 'axios/0.21.1',
  },
  queryStringParameters: null,
  requestContext: {
    resourceId: '5lllcr',
    resourcePath: '/gohighlevel',
    httpMethod: 'POST',
  },
  body: eventBody,
  isBase64Encoded: false,
});

await runHandler(JSON.stringify(eventBody));
// const content = runHandler(event);
