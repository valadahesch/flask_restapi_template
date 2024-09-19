import uuid
import datetime 
from boto3.session import Session
from botocore.client import Config
from boto3.s3.transfer import TransferConfig


class OSSUtil:
    url = "https://oss.cn-north-3.inspurcloudoss.com"
    transfer_config = TransferConfig(multipart_threshold=200*1024**2)

    def __init__(self, access_key, access_secret):
        access_key = access_key
        secret_key = access_secret
        session = Session(access_key, secret_key)
        self.client = session.client(
            's3', region_name='cn-north-3', endpoint_url=self.url,
            config=Config(signature_version='s3', s3={'addressing_style': 'path'})
        )

    def uploadFileStream(self, file_stream, bucket, extra_args=None, object_name=None):
        if extra_args is None:
            extra_args = {}

        if object_name is None:
            object_name = str(uuid.uuid4())
            for _ in range(5):
                if not self.isExist(object_name, bucket):
                    break
                object_name = str(uuid.uuid4())

        self.client.upload_fileobj(file_stream, bucket, object_name, ExtraArgs=extra_args, Config=self.transfer_config)

        return object_name

    def generatePreSignedUrl(self, filename, bucket, s=600):
        """
        生成文件下载的URL
        :param s:
        :param filename: 文件名
        :param bucket: S3中桶的名称
        """
        if not self.isExist(filename, bucket):
            return
        params = {'Bucket': bucket, 'Key': filename}
        file_url = self.client.generate_presigned_url('get_object', Params=params, HttpMethod='GET', ExpiresIn=int(s))
        return file_url

    def getObject(self, bucket, object_name):
        try:
            resp = self.client.get_object(Bucket=bucket, Key=object_name)
            if resp["ResponseMetadata"]['HTTPStatusCode'] == 200:
                file_stream = resp['Body'].read()
                resp_header = {
                    "Last-Modified": resp['LastModified'],
                    "Content-Length": resp['ContentLength'],
                    "ETag": resp['ETag'],
                    "Content-Disposition": resp['ContentDisposition'] if resp.get('ContentDisposition') else "",
                    "Content-Type": resp["ContentType"]
                }
                return file_stream, resp_header
            return None, None
        except Exception:
            return None, None

    def isExist(self, object_name, bucket):
        try:
            self.client.head_object(Bucket=bucket, Key=object_name)
            return True
        except Exception:
            return False

    def putObject(self, bucket_name, object_name, data):
        self.client.put_object(Body=data, Bucket=bucket_name, Key=object_name)

    def updateContentDisposition(self, bucket_name: str, object_name: str, content_disposition: str) -> bool:
        try:
            response = self.client.head_object(Bucket=bucket_name, Key=object_name)
            self.client.copy_object(
                Bucket=bucket_name,
                CopySource={'Bucket': bucket_name, 'Key': object_name},
                Key=object_name,
                MetadataDirective='REPLACE',
                ContentDisposition =content_disposition,
                Metadata=response.get("Metadata")
                )
            return True
        except Exception:
            return False


class AliyunOSSUtil(OSSUtil):

    url = "https://oss-cn-shanghai.aliyuncs.com"
    config = TransferConfig(multipart_threshold=5 * 1024 ** 3)

    def __init__(self, access_key, access_secret):
        super().__init__(access_key, access_secret)
        self.access_key = access_key
        self.secret_key = access_secret
        self.session = Session(self.access_key, self.secret_key)
        self.client = self.session.client(
            's3', endpoint_url=self.url, region_name='oss-cn-shanghai',
            config=Config(s3={"addressing_style": "virtual", "signature_version": 's3v4'})
        )
        

class OSSUtilCommon(OSSUtil):

    def uploadFileStream(self, file_stream, bucket, extra_args=None):
            if extra_args is None:
                extra_args = {}
                
            object_name=str(datetime.datetime.now().year)+"/"+str(uuid.uuid4())
            for _ in range(5):
                if not self.isExist(object_name, bucket):
                    break
                object_name = str(datetime.datetime.now().year)+"/"+str(uuid.uuid4())

            self.client.upload_fileobj(file_stream, bucket, object_name, ExtraArgs=extra_args, Config=self.transfer_config)

            return object_name
