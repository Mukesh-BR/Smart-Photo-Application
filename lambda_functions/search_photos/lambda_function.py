import json
import urllib.parse
import boto3
import datetime

import urllib3

HOST = 'https://search-photos-7wewgttbjdvjbjycqxxhyioyli.us-west-2.es.amazonaws.com'
USERNAME= "ccbd"
PASSWORD= "Ccbd@1234"

INDEX = 'photos'
INDEX_TYPE = 'photo'

LEX_CLIENT = boto3.client('lex-runtime')

def lambda_handler(event, context):
    print("query: " + str(event["queryStringParameters"]["q"]))
    
    response = LEX_CLIENT.post_text(
        botName='myphotosbot',
        botAlias='Dev',
        userId='BPMOLRVQSF',
        inputText=event["queryStringParameters"]["q"]
    )
    
    if "slots" not in response:
        return {
        'statusCode': 200,
        'headers': {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'application/json'
            },
        'body': "Incorrect query"
    }
    print(response["slots"])
    
    http = urllib3.PoolManager()
    url = "%s/%s/%s/_search?" % (HOST, INDEX, INDEX_TYPE)
    headers = urllib3.make_headers(basic_auth='%s:%s' % (USERNAME, PASSWORD))
    headers.update({
        'Content-Type': 'application/json',
        "Accept": "application/json"
    })
    
    word1 = response['slots']['first_keyword']
    word2 = response['slots']['second_keyword']
    if word1[-1] == 's' and not word1[-2] == 's':
        word1 = word1[:-1]
    if word2 is not None and word2[-1] == 's' and not word2[-2] == 's':
        word2 = word2[:-1]
    query = {
              "query": {
                  "query_string": {
                        "query": f"(labels:{word1} OR labels:{word2})"
                    }
                }
            }
    response = http.request('GET', url, headers=headers, body=json.dumps(query))
    status = response.status
    data = json.loads(response.data)
    print("ES Response: [%s] %s" % (status, data))
    
    images = []
    for photo in data["hits"]["hits"]:
        print(photo['_source']['objectKey'])
        images.append({'image-url':'https://myphotos1234.s3.us-west-2.amazonaws.com/' + photo['_source']['objectKey']})

    if not images:
        images = "No images exist for this query."
        
    
    print(images)    
    
    return {
        'statusCode': 200,
        'headers': {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'application/json'
            },
        'body': json.dumps(images)
    }
