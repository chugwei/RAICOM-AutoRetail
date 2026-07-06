#encoding: UTF-8
#!/usr/bin/env python2

import subprocess
import threading
import os
import signal
import json
import re

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.stdout = None  # Initialize stdout
        self.stderr = None  # Initialize stderr

    def run(self, timeout):
        def target():
            print('Thread started')
            self.process = subprocess.Popen(self.cmd, shell=True, preexec_fn=os.setsid,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.stdout, self.stderr = self.process.communicate()
            print('Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print('Terminating process')
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            thread.join()
        print(self.process.returncode)
        return self.stdout.decode('utf-8') if self.stdout else None

def parse_tf_echo_output(output):
    data = []
    current_entry = {}
    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("At time"):
            if current_entry:
                data.append(current_entry)
            current_entry = {"time": line.split()[-1]}
        elif line.startswith("- Translation:"):
            pattern = re.compile(r"(?<=\[).*?(?=\])")
            query = pattern.search(line)
            current_entry["translation"] = [float(x) for x in query.group().split(',')]
        elif line.startswith("- Rotation: in Quaternion"):
            pattern = re.compile(r"(?<=\[).*?(?=\])")
            query = pattern.search(line)
            current_entry["rotation"] = {"quaternion": [float(x) for x in query.group().split(',')]}
        elif line.startswith("in RPY (radian)"):
            pattern = re.compile(r"(?<=\[).*?(?=\])")
            query = pattern.search(line)
            current_entry["rotation"]["rpy_radian"] = [float(x) for x in query.group().split(',')]
        elif line.startswith("in RPY (degree)"):
            pattern = re.compile(r"(?<=\[).*?(?=\])")
            query = pattern.search(line)
            current_entry["rotation"]["rpy_degree"] = [float(x) for x in query.group().split(',')]
    if current_entry:
        data.append(current_entry)
    return data

class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        def compact_format(obj):
            if isinstance(obj, dict):
                return '{' + ', '.join('"{0}": {1}'.format(k, compact_format(v)) for k, v in obj.items()) + '}'
            elif isinstance(obj, list):
                return '[' + ', '.join(compact_format(elem) for elem in obj) + ']'
            else:
                return json.dumps(obj)

        json_str = super(CustomJSONEncoder, self).encode(obj)
        json_lines = json_str.splitlines()
        formatted_lines = []
        for line in json_lines:
            if line.startswith('{') and line.endswith('}'):
                formatted_lines.append(compact_format(json.loads(line)))
            else:
                formatted_lines.append(line)
        return '\n'.join(formatted_lines)

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建相对路径
    output_filename = os.path.join(script_dir, 'goal_1.json')
    
    # 删除文件命令
    command = Command("rm goal_1.json")
    command.run(timeout=1)  

    # 运行ROS命令并捕获输出
    command = Command("rosrun tf tf_echo /map /base_link")
    output = command.run(timeout=2)
    
    if output:
        parsed_data = parse_tf_echo_output(output)
        
        # 只保留第一次记录
        if parsed_data:
            parsed_data = [parsed_data[0]]
        
        # 将数据转换为JSON格式并保存到文件
        with open(output_filename, 'w') as json_file:
            json.dump(parsed_data, json_file, indent=4, cls=CustomJSONEncoder)
        print('Data successfully saved to {}'.format(output_filename))
    else:
        print('No output captured from the command.')
