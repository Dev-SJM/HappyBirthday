from flask import Flask, render_template, request, jsonify, redirect, url_for
from utils import allowed_file, upload_file_to_s3, save_to_dynamodb

app = Flask(__name__)

@app.route("/")
def index_redirct():
    return redirect(url_for('upload_message'))
    
@app.route("/upload-message", methods=['GET', 'POST'])
def upload_message():
    if request.method == 'POST':
        try:
            message = request.form['message']
            name = request.form['name']

            # DynamoDB에 저장
            success = save_to_dynamodb(
                name=name,
                type='message',
                data=message
            )
            
            if not success:
                return jsonify({'error': 'DB 저장 실패'}), 500
            
            return jsonify({'message': '메시지가 성공적으로 저장되었습니다.'})
        except Exception as e:
            print(f"메시지 업로드 중 에러: {str(e)}")
            return jsonify({'error': '서버 에러가 발생했습니다.'}), 500
    else:
        return render_template('upload/message.html')
    
@app.route("/upload-letter", methods=['GET', 'POST'])
def upload_letter():
    if request.method == 'POST':
        try:
            letter = request.form['letter']
            name = request.form['name']
            
            # 먼저 편지 내용을 DynamoDB에 저장
            letter_data = {
                'content': letter,
            }
            
            # 그림 파일이 있는 경우
            if 'drawing' in request.files:
                drawing = request.files['drawing']
                if drawing.filename != '':
                    # S3에 그림 업로드
                    path = f"{name}/letter/"
                    drawing_url = upload_file_to_s3(name, drawing, path)
                    letter_data['drawing_url'] = drawing_url
            
            # DynamoDB에 저장
            success = save_to_dynamodb(name=name, type='letter', data=letter_data)
            
            if not success:
                return jsonify({'error': '저장 실패'}), 500
                
            return jsonify({'message': '성공적으로 전송되었습니다.'})
        except Exception as e:
            print(f"편지 업로드 중 에러: {str(e)}")
            return jsonify({'error': '서버 에러가 발생했습니다.'}), 500
    else:
        return render_template('upload/letter.html')

@app.route("/upload-photo", methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST':
        try:
            if 'photo' not in request.files:
                return jsonify({'error': '파일이 전송되지 않았습니다.'}), 400
                
            photo = request.files['photo']
            if not photo or not photo.filename:
                return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

            name = request.form['name']
            if not name:
                return jsonify({'error': '이름이 입력되지 않았습니다.'}), 400
            
            path = f"{name}/photo/"
            
            # S3에 파일 업로드
            photo_url = upload_file_to_s3(name, photo, path)
            
            if not photo_url:
                return jsonify({'error': '파일 업로드에 실패했습니다.'}), 500
            
            # DynamoDB에 저장
            success = save_to_dynamodb(
                name=name,
                type='photo',
                data=photo_url  # S3 URL 저장
            )
            
            if not success:
                return jsonify({'error': 'DB 저장 실패'}), 500
            
            return jsonify({'message': '성공적으로 업로드되었습니다.'})
            
        except Exception as e:
            print(f"업로드 처리 중 에러 발생: {str(e)}")
            return jsonify({'error': '서버 에러가 발생했습니다.'}), 500
    else:
        return render_template('upload/photo.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)