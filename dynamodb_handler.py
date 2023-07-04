import boto3
from flask import request
import key_config as keys


dynamodb_client = boto3.client(
    'dynamodb',
    aws_access_key_id     = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name           = keys.REGION_NAME,
)
dynamodb_resource = boto3.resource(
    'dynamodb',
    aws_access_key_id     = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name           = keys.REGION_NAME,
)
s3 = boto3.resource(
    's3',
    aws_access_key_id     = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name           = keys.REGION_NAME,
)


def create_user_table():
    
    table = dynamodb_resource.create_table(
        TableName = 'users', # Name of the table
        KeySchema = [
            {
               'AttributeName': 'email',
               'KeyType'      : 'HASH' #RANGE = sort key, HASH = partition key
            }
        ],
        AttributeDefinitions = [
           {
               'AttributeName': 'email', # Name of the attribute
               'AttributeType': 'S'   # N = Number (B= Binary, S = String)
           }
        ],
        ProvisionedThroughput={
           'ReadCapacityUnits'  : 10,
           'WriteCapacityUnits': 10
        }
    )
    return table


def create_bucket():
    
    AWS_REGION = "ap-southeast-1"
    client = boto3.client("s3", region_name=AWS_REGION)
    bucket_name = "profile-image-upload"
    location = {'LocationConstraint': AWS_REGION}
    client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)


user = dynamodb_resource.Table("users")

     
def add_item_to_user_table(fullname, registration_number, email, password, degree, contact, introduction, GPA, skills):
    
    profile_image = "https://profile-image-upload.s3.ap-southeast-1.amazonaws.com/default.png"
    
    response = user.put_item(
        Item={
             'fullname' : fullname,
             'registration_number' : registration_number,
             'email' : email,
             'password' : password,
             'degree' : degree,
             'contact' : contact,
             'introduction' : introduction,
             'GPA' : GPA,
             'skills' : skills,
             'profile_image' : profile_image
        }
    )
    return response
    
    
def upload_image():
    
    file = request.files['profile_image']
    filename = file.filename
    bucket_name = 'profile-image-upload'
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(
        Key=filename,
        Body=file,
        ContentType='image/jpeg',
        ContentDisposition='inline'
    ) 
    return filename, bucket_name
   
   
def update_image_url(object_url):
    
    email = request.form['email']
    
    response = user.update_item(
        
        Key = {
           'email': email
        },
        AttributeUpdates={
            
            'profile_image': {
               'Value'  : object_url,
               'Action' : 'PUT' 
            }
            
        },
        
        ReturnValues = "UPDATED_NEW"  # returns the new updated values
    )
    
    return response
    
    
def update_user_profile(email,data:dict):
    
    response = user.update_item(
        
        Key = {
           'email': email
        },
        AttributeUpdates={
            
            'fullname': {
               'Value'  : data['fullname'],
               'Action' : 'PUT' 
            },
            'registration_number': {
               'Value'  : data['registration_number'],
               'Action' : 'PUT'
            },
            'password': {
               'Value'  : data['password'],
               'Action' : 'PUT'
            },
            'degree': {
               'Value'  : data['degree'],
               'Action' : 'PUT'
            },
            'contact': {
               'Value'  : data['contact'],
               'Action' : 'PUT'
            },
            'introduction': {
               'Value'  : data['introduction'],
               'Action' : 'PUT'
            },
            'GPA': {
               'Value'  : data['GPA'],
               'Action' : 'PUT'
            },
            'skills': {
               'Value'  : data['skills'],
               'Action' : 'PUT'
            },
            
        },
        
        ReturnValues = "UPDATED_NEW"  # returns the new updated values
    )
    
    return response
    
    
def get_user_details(email):
    response = user.get_item(
        Key={
            'email': email
        })
    item = response["Item"]
    
    return item
    
    
def get_user_profile(registration_number):
    
    response = user.scan(
        FilterExpression=f'registration_number = :registration_number',
        ExpressionAttributeValues={':registration_number': registration_number}
    )
    item = response["Items"][0]
    return item

    

  
  
  