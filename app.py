from flask import Flask, render_template, request, jsonify
from converter.nginx2caddy import convert_nginx_to_caddy
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 限制上传文件 16KB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # 获取上传文件或文本内容
    nginx_config = ""
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file.filename.endswith('.conf'):
            nginx_config = file.read().decode('utf-8')
    else:
        nginx_config = request.form.get('text', '')

    if not nginx_config:
        return jsonify({"error": "未提供有效输入"}), 400

    # 执行转换
    try:
        caddy_config = convert_nginx_to_caddy(nginx_config)
        return jsonify({"caddyfile": caddy_config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
