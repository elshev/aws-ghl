import json
import requests

def lambda_handler(event, context):
    api_token = 'PUT_API_TOKEN_HERE'
    conversation_id = '9325cLcgqmhJVyfITS7g'
    endpoint = 'https://services.leadconnectorhq.com'
    path = f'/conversations/{conversation_id}'
    url = endpoint + path
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}',
        'Version': '2021-04-15'
    }
    # data = {
    #     'param1': 'value1',
    #     'param2': 'value2'
    # }
    response = requests.post(url, headers=headers)

    result = ''
    if response.status_code == 200:
        result = response.content.decode('utf-8')
    else:
        result = f"Error {response.status_code}: {response.text}"
    print(result)

    result = json.loads(response.text)
    print(result)
    return result
