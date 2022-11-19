import base64

from flask import Flask, request, Response, render_template
import json

from core.api.clone import clone_voice

# 初始化flaskAPP
app = Flask(__name__)


# 返回JSON字符串
def return_json(data):
    return Response(json.dumps(data, ensure_ascii=False), mimetype='application/json')


# 音色转换
@app.route('/voice/clone', methods=['POST'])
def clone_voice1():
    role = request.form.get('role')
    data = request.form.get('data')
    # 直接把音频信息保存为文件
    path = "./web/static"
    row = path+"/origin.wav"
    data = data.replace("data:audio/wav;base64,", "")
    with open(row, "wb") as f:
        f.write(base64.b64decode(data))
    res = clone_voice(row, path, [int(role)])
    if len(res) == 1:
        return return_json({
            'audio': '/static/{}'.format(res[0])
        })
    # 返回json类型字符串
    return return_json({})


# 声音克隆
@app.route('/voice/clone2', methods=['POST'])
def clone_voice2():
    path = "./web/static"
    origin_path = path+"/origin.wav"
    refer_path = path+"/refer.wav"
    origin = request.form.get('origin')
    refer = request.form.get('refer')
    # 直接把音频信息保存为文件
    data = origin.replace("data:audio/wav;base64,", "")
    refer = refer.replace("data:audio/wav;base64,", "")
    with open(origin_path, "wb") as f:
        f.write(base64.b64decode(data))
    with open(refer_path, "wb") as f:
        f.write(base64.b64decode(refer))
    res = clone_voice(origin_path, path, [], refer_path)
    if len(res) == 1:
        return return_json({
            'audio': '/static/{}'.format(res[0])
        })
    # 返回json类型字符串
    return return_json({})


# 主页显示HTML
@app.route('/', methods=['GET'])
def index():
    return render_template('content.html')
