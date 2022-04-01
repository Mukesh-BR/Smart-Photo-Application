import json
import urllib.parse
import boto3
import datetime
import urllib3

#Making a change to lambda
rekognition = boto3.client('rekognition')

host = 'https://search-photos-7wewgttbjdvjbjycqxxhyioyli.us-west-2.es.amazonaws.com'
index = 'photos'
type = 'photo'
url = host + '/' + index + '/' + type
master_username= "ccbd"
master_password= "Ccbd@1234"
headers = { "Content-Type": "application/json" }



def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    output_tags = []
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        output_tags.append(label['Name'])
    return output_tags



def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    tags = detect_labels(bucket, key)
    
    opensearch_js = {"objectKey": key, 
                    "bucket": bucket,
                    "createdTimestamp": str(datetime.datetime.now().strftime("%Y-%m-%d"'T'"%H:%M:%S")),
                    "labels": list(tags)
    }
    
    print(opensearch_js)   

    http = urllib3.PoolManager()
    url = "%s/%s/%s/" % (host, index, type)
    headers = urllib3.make_headers(basic_auth='%s:%s' % (master_username, master_password))
    headers.update({
        'Content-Type': 'application/json',
        "Accept": "application/json"
    })
    payload = opensearch_js
    response = http.request('POST', url, headers=headers, body=json.dumps(payload))
    status = response.status
    data = json.loads(response.data)
    print("ES Response: [%s] %s" % (status, data))

    return {
        'statusCode': response.status,
        'body': json.loads(response.data)
    }
