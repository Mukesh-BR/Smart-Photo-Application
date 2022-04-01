import json
import urllib.parse
import boto3
import datetime
import urllib3

#Adding Comment for Demo
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

def get_s3_metadata(bucket, file):
    print("Get custom labels for %s - %s" % (bucket, file))
    s3 = boto3.client("s3", region_name='us-east-1')
    response = s3.head_object(Bucket=bucket, Key=file)
    print("S3 head obj:", response)
    custom_labels = response["Metadata"].get("customlabels", "")
    custom_labels = list(filter(lambda x: x, map(lambda x: x.strip(), custom_labels.split(","))))
    print("Custom labels:", custom_labels)
    return custom_labels


def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    tags = detect_labels(bucket, key)
    custom =  get_s3_metadata(bucket, key)
    tags = tags+custom
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
