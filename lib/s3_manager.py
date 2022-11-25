# -*- coding: utf-8 -*-
import boto3
import time


class S3Manager:

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_default_region="ap-northeast-2"):
        # account info ( be args )
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_default_region = aws_default_region
        # sts session
        self.s3_client = S3Manager.aws_client(
            's3',
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.aws_default_region,
        )
        # CF client
        self.cf_client = S3Manager.aws_client(
            'cloudfront',
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.aws_default_region
        )

    @staticmethod
    def aws_client(
            service:str,
            aws_access_key_id:str,
            aws_secret_access_key:str,
            aws_default_region:str
    ) -> boto3.client:
        client = boto3.client(service,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=aws_default_region
                              )
        return client

    def buckets(self, ) -> list:
        dict_buckets = self.s3_client.list_buckets()
        buckets = dict_buckets['Buckets']
        return [bucket['Name'] for bucket in buckets]

    def bucket_contents(self, bucket_name:str) -> list:
        if self.s3_client.list_objects_v2(Bucket=bucket_name).get('Contents'):
            return [content for content in self.s3_client.list_objects_v2(Bucket=bucket_name)['Contents']]
        return []

    def content_list(self, bucket_name:str, prefix: str='icon2') -> dict:
        if self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix).get('Contents'):
            return {content['Key']:content['LastModified'] for content in self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)['Contents']}
        return {}

    def upload(self, bucket:str, key:str, file_name:str, extra_args:object=None):
        if extra_args is None:
            self.s3_client.upload_file(file_name, bucket, key)
        else:
            self.s3_client.upload_file(file_name, bucket, key, ExtraArgs=extra_args)

    def cf_re_caching(self, dist_id:str):
        self.cf_client.create_invalidation(
            DistributionId=dist_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                        '/*',
                    ]
                },
                'CallerReference': str(time.time()).replace('.', '')
            }
        )

    def download(self, bucket:str, key:str, file_name:str):
        self.s3_client.download_file(bucket, key, file_name)

    def delete(self, bucket:str, key:str):
        self.s3_client.delete_object(Bucket=bucket, Key=key)