from flask import Flask, render_template, request, jsonify, redirect, url_for
from utils import allowed_file, upload_file_to_s3

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
            print(message, name)
            # 메시지 저장 로직
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
            print(letter, name)
            # 편지 저장 로직
            return jsonify({'message': '편지가 성공적으로 저장되었습니다.'})
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
                
            if not allowed_file(photo.filename):
                return jsonify({'error': '허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif만 가능)'}), 400
            
            # S3에 파일 업로드
            photo_url = upload_file_to_s3(name, photo)
            
            if not photo_url:
                return jsonify({'error': '파일 업로드에 실패했습니다.'}), 500
            
            print(f"업로드된 파일 URL: {photo_url}")
            
            return jsonify({
                'message': '성공적으로 업로드되었습니다.',
                'photo_url': photo_url
            })
            
        except Exception as e:
            print(f"업로드 처리 중 에러 발생: {str(e)}")
            return jsonify({'error': '서버 에러가 발생했습니다.'}), 500
    else:
        return render_template('upload/photo.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)