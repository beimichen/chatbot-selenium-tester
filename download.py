import boto3


def download_position_lookup_latest():
    filename = "positions.json"
    bucket_name = "YOUR_S3_BUCKET"
    object_name = "positions.json"

    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_name, filename)
    print("success")
