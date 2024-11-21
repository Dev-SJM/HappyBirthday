from botocore.exceptions import ClientError
import os
import boto3
import uuid

id_key = os.environ.get('AWS_ACCESS_KEY')
secret_key = os.environ.get('AWS_SECRET_KEY')
bucket_name = os.environ.get('AWS_BUCKET_NAME')

# S3 클라이언트 설정
s3_client = boto3.client(
    's3',
    aws_access_key_id=id_key,
    aws_secret_access_key=secret_key,
    region_name="ap-northeast-2"
)

def allowed_file(filename):
    """파일 확장자 검사"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file_to_s3(name, file):
    """
    S3에 파일을 업로드하고 URL을 반환
    """
    try:
        # 원본 파일명에서 확장자 추출
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        # UUID를 사용하여 고유한 파일명 생성
        new_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # 파일 경로 설정
        file_path = f"{name}/{new_filename}"
        
        # S3에 업로드
        s3_client.upload_fileobj(
            file,
            str(bucket_name),
            file_path,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )
        
        # S3 URL 생성
        url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_path}"
        
        return url
        
    except ClientError as e:
        print(f"S3 업로드 에러: {str(e)}")
        return None
    except Exception as e:
        print(f"예상치 못한 에러: {str(e)}")
        return None