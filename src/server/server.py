# encoding: UTF-8
#!/usr/bin/env python2

from flask import Flask, request, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 设置 test.py 的绝对路径
SCRIPT_PATH = '/home/robuster/czc_robuster/Program/server/test.py'
# 设置文件保存目录
UPLOAD_FOLDER = '/home/robuster/czc_robuster/Program/server'  # 替换为实际路径
# 设置文件大小限制 16 MB
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
# 允许传输的文件类型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'json'}

# 配置 Flask 应用
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_valid_task_data(data):
    return len(data) == 8 and data.startswith("Task-") and data[5:].isdigit() and 0 <= int(data[5:]) <= 999

@app.route('/upload_string', methods=['POST'])
def upload_string():
    if not request.json or 'data' not in request.json:
        return jsonify({"error": "No data part"}), 400
    data = request.json['data']
        
    # 处理接收到的字符串标志位
    print("Received data:", data)

    if is_valid_task_data(data):
        try:
            # 非阻塞地执行Python脚本
            subprocess.Popen(['python2', SCRIPT_PATH, data])
            return jsonify({"success": True, "message": "Data received and script execution started"}), 200
        except Exception as e:
            print("Exception during script execution:", str(e))
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        print("Invalid data format:", data)
        return jsonify({"success": False, "error": "Invalid data format"}), 400

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            return jsonify({"success": True, "file_path": file_path}), 200
        except Exception as e:
            app.logger.error("Failed to save file: %s", str(e))
            return jsonify({"success": False, "error": "Failed to save file"}), 500
    else:
        return jsonify({"success": False, "error": "File type not allowed or exceeds size limit"}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
