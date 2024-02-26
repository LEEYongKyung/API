import boto3
from botocore.exceptions import ClientError

class awsS3:

    @staticmethod
    def create_bucket(bucket_name):
        s3 = boto3.client('s3')        
        try:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-2'})
        except ClientError as e:
            print(e)
            return False
        return True

    @staticmethod
    def select_bucket_list():
        s3 = boto3.client('s3')        
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return buckets

    @staticmethod
    def select_object_list(bucket_name, prefix='/', includeChild="N"):
        delimiter = '/'
        prefix = prefix[1:] if prefix.startswith(delimiter) else prefix
        bucket = boto3.resource('s3').Bucket(bucket_name)        
        bucketObj = bucket.objects.filter(Prefix=prefix)

        objList = list()

        if bucketObj:            
            for index, file in enumerate(bucketObj):

                tmp = file.key[len(prefix):]
                tmp = tmp[len(delimiter):] if tmp.startswith(delimiter) else tmp
                tmp2 = tmp.find(delimiter)
                
                # 파일, 폴더 구분
                isFile = file.key[-len(delimiter):] != delimiter

                # 검색값 과 키값이 같고 폴더이면 제외
                if len(tmp) == 0 and not isFile:
                    continue

                if includeChild != "Y":
                    # 검색값을 포함하고 있는 하위 폴더 정보이면 제외
                    if tmp2 != -1:                   
                        if tmp2 != len(tmp) - 1:
                            continue

                print(file.key)
                tr_dict = dict()
                tr_dict['key'] = file.key
                tr_dict['type'] = 'file' if isFile else 'folder'
                objList.append(tr_dict)

        return objList

    @staticmethod
    def exists(bucket_name, prefix='/'):
        delimiter = '/'
        prefix = prefix[1:] if prefix.startswith(delimiter) else prefix
        bucket = boto3.resource('s3').Bucket(bucket_name)        
        bucketObj = bucket.objects.filter(Prefix=prefix)

        result = False

        if bucketObj:            
            for index, file in enumerate(bucketObj):

                tmp = file.key[len(prefix):]
                tmp = tmp[len(delimiter):] if tmp.startswith(delimiter) else tmp                
               
                # 검색값 과 키값이 같으면 True
                if len(tmp) == 0:
                    return True
                else:
                    continue

        return result

    @staticmethod
    def upload_file(file_name, bucket_name, object_name=None):
        if object_name is None:
            object_name = file_name

        delimiter = '/'
        object_name = object_name[1:] if object_name.startswith(delimiter) else object_name

        s3 = boto3.client('s3')
        try:            
            s3.upload_file(file_name, bucket_name, object_name)
        except ClientError as e:
            print(e)
            return False
        return True

    @staticmethod
    def upload_image(file_name, bucket_name, object_name=None):
        if object_name is None:
            object_name = file_name

        delimiter = '/'
        object_name = object_name[1:] if object_name.startswith(delimiter) else object_name
        content_type = "image/" + object_name.split('.')[1]

        s3 = boto3.client('s3')
        try:            
            s3.upload_file(file_name, bucket_name, object_name, ExtraArgs={ "ContentType": content_type })
        except ClientError as e:
            print(e)
            return False
        return True

    @staticmethod
    def delete_file(bucket_name, object_name=None):
        if object_name is None:
            return False

        s3 = boto3.resource('s3')
        try:            
            obj = s3.Object(bucket_name, object_name)
            obj.delete()
        except ClientError as e:
            print(e)
            return False
        return True