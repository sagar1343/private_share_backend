import boto3
import urllib.parse
from django.conf import settings

session = boto3.Session(region_name="ap-south-1")
client = session.client("s3")


def generate_url(object_name):
    filename = object_name.split("/")[-1]
    safe_filename = urllib.parse.quote(filename)

    presigned_url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": object_name,
            "ResponseContentDisposition": f'attachment; filename="{safe_filename}"',
        },
        ExpiresIn=60,
    )
    return presigned_url
