from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify, abort
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import os
import re
import uuid
from datetime import datetime
import chardet
import tempfile
import shutil
import itertools
from country_operators import (
    COUNTRY_OPERATORS, get_country_list, get_operators_by_country,
    filter_by_country_and_operator, get_statistics, identify_operator,
    get_country_list_flat
)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 增加到500MB max upload size

# 功能描述
FUNCTION_DESCRIPTIONS = {
    1: """
    1. 数据清洗（注：以下三个功能需同时实现）
        （1）保留指定位数号码：例：输入11，除11位手机号全部删除
        （2）错误前缀国码：  例：输入84，除84前缀手机号全部删除
        （3）*?等错误字符    例：无。
    """,
    2: """
    2. 一键加国码：
        例：输入84，所有号码前添加84。
    """,
    3: """
    3. 数据拆分：
        例：输入10000，10W数据拆分为10个1W数据
    """,
    4: """
    4. 文件去重：删除重复的数据。
        注意：带空格的数据会被处理为相同数据（如"123"和"123 "视为相同)
    """,
    5: """
    5. A去除B文本内容
        例：导入A,B文本，将A文本中包含B文本数据全部删除。
        示例:
        A文本：
        123
        234
        345
        B文本：
        123
        345
        输出文本：
        234
    """,
    6: """
    6. 指定前缀数据过滤
        可以添加多个前缀条件，删除包含这些前缀的数据
    """,
    7: """
    7. 国家运营商筛选
        根据国家和运营商筛选手机号码数据
        支持多个国家和运营商同时筛选
        提供详细的统计信息
    """
}

def check_file_extension(filename):
    """检查文件扩展名是否为txt"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'txt'

def custom_secure_filename(filename):
    """自定义安全文件名函数，保留中文等字符"""
    # 保留中文等Unicode字符
    filename = filename.encode('utf-8', 'ignore').decode('utf-8')
    # 替换不安全字符为下划线
    filename = re.sub(r'[^\w\u4e00-\u9fff\-_. ]', '_', filename)
    return filename.strip()

def generate_file_paths(func_num, original_filename):
    """生成输入输出文件路径"""
    now = datetime.now()
    time_str = now.strftime("%m.%d.%H.%M.%S")
    file_uuid = str(uuid.uuid4())[:8]  # 短UUID

    # 安全处理文件名
    safe_filename = custom_secure_filename(original_filename)

    # 输入文件路径
    input_dir = os.path.join(
        "test/data/input",
        str(func_num),
        f"{time_str}_{file_uuid}"
    )
    input_path = os.path.join(input_dir, safe_filename)

    # 输出文件路径
    output_dir = os.path.join(
        "test/data/output",
        str(func_num),
        f"{time_str}_{file_uuid}"
    )
    output_filename = f"{func_num}_{safe_filename}"
    output_path = os.path.join(output_dir, output_filename)

    return {
        'input_dir': input_dir,
        'input_path': input_path,
        'output_dir': output_dir,
        'output_path': output_path,
        'download_filename': output_filename,
        'uuid': file_uuid,
        'timestamp': time_str,
        'original_filename': original_filename
    }

def stream_text_file(file_path):
    """流式读取文本文件，逐行处理"""
    # 二进制模式读取文件检测编码
    with open(file_path, 'rb') as f:
        raw_data = f.read(1024*1024)  # 读取1MB用于检测编码

    encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

    # 重新打开文件逐行处理
    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
        for line in f:
            line = line.strip()
            if line and all(c.isdigit() for c in line):  # 严格纯数字检查
                yield line

def count_lines(file_path):
    """快速计算文件行数"""
    with open(file_path, 'rb') as f:
        return sum(1 for _ in f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/function_description')
def function_description():
    return render_template('function_description.html', descriptions=FUNCTION_DESCRIPTIONS)

@app.route('/function<int:func_num>', methods=['GET', 'POST'])
def function_page(func_num):
    if request.method == 'POST':
        if func_num == 1:
            return handle_function1()
        elif func_num == 2:
            return handle_function2()
        elif func_num == 3:
            return handle_function3()
        elif func_num == 4:
            return handle_function4()
        elif func_num == 5:
            return handle_function5()
        elif func_num == 6:
            return handle_function6()
        elif func_num == 7:
            return handle_function7()
    
    # GET请求，渲染对应的模板
    if func_num == 7:
        # 传递国家列表给模板
        countries = get_country_list()
        return render_template('function7.html', countries=countries)
    
    return render_template(f'function{func_num}.html')

# 功能处理函数将在下个提交中添加

if __name__ == '__main__':
    # 创建必要的目录结构
    os.makedirs("test/data/input", exist_ok=True)
    os.makedirs("test/data/output", exist_ok=True)
    for i in range(1, 8):  # 支持共7个功能
        os.makedirs(f"test/data/input/{i}", exist_ok=True)
        os.makedirs(f"test/data/output/{i}", exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)