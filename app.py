from flask import Flask, render_template, request, jsonify
from config import id_key, secret_key, bucket_name
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import mimetypes
import boto3
import uuid

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('upload.html')

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
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_file_extension(file):
    """파일의 확장자를 안전하게 가져오는 함수"""
    # 파일 이름에서 확장자 추출 시도
    filename = secure_filename(file.filename)
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    
    # 파일 이름에서 확장자를 얻을 수 없는 경우, MIME 타입을 확인
    mime_type = file.content_type
    if mime_type:
        # MIME 타입에 따른 확장자 매핑
        extensions = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif'
        }
        return extensions.get(mime_type, 'jpg')  # 기본값으로 jpg 사용
    
    return 'jpg'  # 최후의 기본값

def upload_file_to_s3(name, file):
    """
    S3에 파일을 업로드하고 URL을 반환
    """
    try:
        # 파일 확장자 가져오기
        file_extension = get_file_extension(file)
        
        # UUID를 사용하여 고유한 파일명 생성
        new_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # 파일 경로 설정 (예: christmas-2024/image.jpg)
        file_path = f"{name}/{new_filename}"
        
        # 콘텐츠 타입 결정
        content_type = file.content_type or mimetypes.guess_type(new_filename)[0] or 'application/octet-stream'
        
        # S3에 업로드
        s3_client.upload_fileobj(
            file,
            bucket_name,
            file_path,
            ExtraArgs={
                'ContentType': content_type
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

@app.route("/upload", methods=['POST'])
def upload():
    try:
        message = request.form['message']
        letter = request.form['letter']
        photo = request.files['photo']
        name = request.form['name']
        
        # 파일 유효성 검사
        if not photo:
            return jsonify({'error': '파일이 없습니다.'}), 400
            
        if not allowed_file(photo.filename):
            return jsonify({'error': '허용되지 않는 파일 형식입니다.'}), 400
        
        # S3에 파일 업로드
        photo_url = upload_file_to_s3(name, photo)
        
        if not photo_url:
            return jsonify({'error': '파일 업로드에 실패했습니다.'}), 500
        
        print(photo_url)
        
        # 여기에 데이터베이스 저장 로직 추가
        # 예: save_to_database(message, letter, photo_url, name)
        
        return jsonify({
            'message': '성공적으로 업로드되었습니다.',
            'photo_url': photo_url
        })
        
    except Exception as e:
        print(f"업로드 처리 중 에러 발생: {str(e)}")
        return jsonify({'error': '서버 에러가 발생했습니다.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)