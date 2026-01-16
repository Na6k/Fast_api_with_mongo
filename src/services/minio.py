import asyncio
import aioboto3

async def upload_file_to_minio(
    endpoint_url: str,
    access_key: str,
    secret_key: str,
    bucket_name: str,
    file_path: str,
    object_name: str
):
    session = aioboto3.Session()
    async with session.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1',  # MinIO не требует региона, но boto3 требует указать
    ) as s3_client:

        # Проверяем, существует ли бакет
        buckets = await s3_client.list_buckets()
        bucket_names = [b['Name'] for b in buckets.get('Buckets', [])]
        if bucket_name not in bucket_names:
            await s3_client.create_bucket(Bucket=bucket_name)
            print(f"Создан бакет: {bucket_name}")
        else:
            print(f"Бакет {bucket_name} уже существует")

        # Загружаем файл
        with open(file_path, 'rb') as file_data:
            await s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=file_data)
            print(f"Файл '{file_path}' успешно загружен в '{bucket_name}/{object_name}'")

if __name__ == "__main__":
    MINIO_ENDPOINT = "https://minio.radis.pro"  # Обязательно с http:// или https://
    MINIO_ACCESS_KEY = "radis"
    MINIO_SECRET_KEY = "AmdHFR4SvtKaFxVGvgsX"
    BUCKET_NAME = "mybucket"
    FILE_PATH = "path/to/local/file.txt"
    OBJECT_NAME = "file.txt"

    asyncio.run(upload_file_to_minio(
        MINIO_ENDPOINT,
        MINIO_ACCESS_KEY,
        MINIO_SECRET_KEY,
        BUCKET_NAME,
        FILE_PATH,
        OBJECT_NAME
    ))
