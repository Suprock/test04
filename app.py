from flask import *
import paramiko
from paramiko.client import AutoAddPolicy
from proj_info import *
import os, time
from flask_socketio import *
import _thread
from paramiko import SSHClient, SFTPClient
from ping3 import ping
from file import file_check, TransFile

global project_info_path
global pangu_install_zip_name
global file_path
global manager_node_ip
global manager_node_username
global manager_node_password
global files_to_upload
global is_in_company
global remote_pangu_auto_install_dir
global dongle_ip
global is_soft
global rac_file_path    # rac文件路径
global manager_node_info

remote_pangu_auto_install_dir = "pangu_auto_install-master"
manager_node_ip = ""
file_path = "file/"
pangu_install_zip_name = "pangu_auto_install.zip"
files_to_upload = []
is_in_company = True
dongle_ip = ""
is_soft = ""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

###
# topic  值1：盘古自动部署工具；
#        值2：小工具
# steps  盘古自动部署工具 值0-4 分别表示配置管理，镜像上传，授权证书，项目部署，信息下载；
#        小工具 值0-2 分别表示加密狗授权，证书下载，相机添加
###
def make_index_info(topic, steps):
    if topic == 1:
        index_info = {"topic":"盘古自动部署工具",
        "steps":[{"name":"项目配置", "is_active":False}, {"name":"镜像上传","is_active":False}, {"name":"devops安装","is_active":False},{"name":"授权证书","is_active":False},{"name":"项目部署","is_active":False},{"name":"信息下载", "is_active":False}],
        "navs":[{"name":"自动部署工具", "is_active":True, "herf":"/"}, {"name":"小工具", "is_active":False, "herf":"/tools"}]}
    elif topic == 2:
        index_info = {"topic":"小工具",
     "steps":[{"name":"加密狗配置", "is_active":False, "herf":"/tools"},{"name":"证书下载","is_active":False, "herf":"/cerf"},{"name":"添加相机", "is_active":False, "herf":"/add_device"}],
      "navs":[{"name":"自动部署工具", "is_active":False, "herf":"/"}, {"name":"小工具", "is_active":True, "herf":"/tools"}]}
    index_info["steps"][steps]["is_active"] = True
    return index_info

@app.route("/")
def index():
    return redirect("/proj_info")

@app.route("/proj_info", methods=["POST", "GET"])
def proj_info():
    global manager_node_ip
    global manager_node_username
    global manager_node_password
    global project_info_path
    global is_in_company
    global dongle_ip
    global is_soft
    global manager_node_info
    if request.method == "GET":
        index_info = make_index_info(1, 0)
        return render_template("proj_info.html" ,index_info=index_info)
    else:
        data = request.get_json()
        # 拼接服务字符串如"faced-video*2,faced-capture*2"
        dongle_ip = data["dongle_ip"]
        is_soft = data["is_soft"]
        arr_service_info = data["arr_service_info"]
        str_services_info = ""
        for i, service_info in enumerate(arr_service_info):
            if service_info[1] == "":
                continue
            if i < len(arr_service_info) - 1:
                str_service_info = "{}*{},".format(core_sevices[service_info[0]], service_info[1])
            elif i == len(arr_service_info) - 1:
                str_service_info = "{}*{}".format(core_sevices[service_info[0]], service_info[1])
            str_services_info += str_service_info

        if data["is_in_company"] == "1":
            is_in_company = True
            devops_version = "21.5.2"
        else:
            is_in_company = False
            devops_version = ""
        # 分配服务所在节点，pangu,gsp,gmp,iot,core,algowarehouse
        # services_all = ["pangu","gsp","gmp","iot","core"]
        devices_info = ""
        devices = data["arr_devices_info"]
        if len(arr_service_info) == 1 and arr_service_info[0][1] == "":  # 没有core服务，只需要部署盘古服务
            local_service = "pangu,gsp"
            # 只需要一个节点，则第一个节点为devops-manager节点
            devices_info = manager_node.format(1, devices[0][0], devices[0][1], devices[0][2],local_service)
            manager_node_ip = devices[0][0]
            manager_node_username = devices[0][1]
            manager_node_password = devices[0][2]
            manager_node_info = ManagerNodeInfo(devices[0][0], devices[0][1], devices[0][2])
        elif arr_service_info[0][1] != "" and len(devices) == 1:
            local_service = "pangu,gmp,core,iot,gsp"
            devices_info = manager_node.format(1, devices[0][0], devices[0][1], devices[0][2],local_service)
            manager_node_ip = devices[0][0]
            manager_node_username = devices[0][1]
            manager_node_password = devices[0][2]
            manager_node_info = ManagerNodeInfo(devices[0][0], devices[0][1], devices[0][2])
        elif arr_service_info[0][1] != "" or len(arr_service_info) > 1:
            #只针对第一台算力和第一台业务分配服务
            is_first_busi = True
            is_first_calc = True
            for i, device in enumerate(devices):
                local_service = ""
                str_node = ""
                if i == 0:
                    str_node = manager_node
                    index = 1
                    manager_node_ip = device[0]
                    manager_node_username = device[1]
                    manager_node_password = device[2]
                    manager_node_info = ManagerNodeInfo(device[0],device[1], device[2])
                else:
                    str_node = agent_node
                    index = i
                if device[3] == "1" and is_first_busi == True:
                    local_service = "pangu,gmp"
                    is_first_busi = False
                if device[3] == "2" and is_first_calc == True:
                    local_service = "core,iot,gsp"
                    is_first_calc = False
                devices_info += str_node.format(index, device[0], device[1], device[2], local_service)
        real_proj_info = proj_info_str.format(data["proj_name"],
        data["is_soft"],
        data["is_HA"],
        data["VIP_ip"],
        data["dongle_ip"],
        devops_version,
        data["pangu_version"],
        str_services_info,
        "", # 共卡附属服务
        "", # 共卡附属服务
        data["is_profilo"],
        data["is_face_body"],
        data["algowarehouseA"],
        data["algowarehouseB"],
        data["algowarehouseC"],
        data["algowarehouseD"]
        )
        real_proj_info += devices_info
        
        # 生成文件
        path_date = time.strftime("%Y%m%d", time.localtime())
        path_proj = data["proj_name"]
        real_path = "file/" + path_date + "/" + path_proj
        if os.path.exists(real_path) == False:
            os.makedirs(real_path)
        file = open(real_path + "/" + "project_info", "w", encoding="utf-8")
        file.write(real_proj_info)
        file.close()

        project_info_path = "./" + real_path + "/" + "project_info"

        return jsonify({"status":200,"result":"OK"})

@app.route("/upload_img", methods=["POST", "GET"])
def upload_img():
    global manager_node_ip
    global remote_pangu_auto_install_dir
    global files_to_upload
    if request.method == "GET":
        # TBD 查看管理节点信息是否存在，不存在转到首页
        index_info = make_index_info(1, 1)
        return render_template("upload_img.html",index_info=index_info)
    else:
        if manager_node_ip == "":
            return jsonify({"status":302,"result":"to root"})
        data = request.get_json()
        ret, imgs = file_check(data["file_path"], 1)
        if ret == True:
            for img in imgs:
                if ".deb.run" in img[0]:
                    remote_img_path = "{}/{}".format(remote_pangu_auto_install_dir, img[0])
                else:
                    remote_img_path = "{}/images/{}".format(remote_pangu_auto_install_dir, img[0])
                files_to_upload.append([img[0], img[1], remote_img_path])   
            return jsonify({"status":200,"result":"OK"})
        else:
            return jsonify({"status":400,"result":"FALSE"})

@app.route("/install_devops", methods=["GET", "POST"])
def install_devops():
    if request.method == "GET":
        index_info = make_index_info(1, 2)
        return render_template("devops_install.html", index_info=index_info)
    else:
        return jsonify({"status":200, "result":"OK"})
    

@app.route("/auth_cert", methods=["GET", "POST"])
def auth_cert():
    if request.method == "GET":
        index_info = make_index_info(1, 3)
        return render_template("auth_cert.html", index_info=index_info)
    else:
        pass

@app.route("/install_pangu", methods=["POST","GET"])
def install_pangu():
    global manager_node_ip
    if request.method == "GET":
        if manager_node_ip == "":
            return redirect("/") 
        index_info = make_index_info(1, 4)
        return render_template("pangu_install.html", index_info=index_info)
    else:
        return jsonify({"status":200})
        
@app.route("/tools")
def tools():
    index_info = make_index_info(2, 0)
    return render_template("dongle.html" ,index_info=index_info)

@app.route("/cerf")
def cerf():
    index_info = make_index_info(2, 1)
    return render_template("cerf.html", index_info=index_info)

@app.route("/add_device")
def add_device():
    index_info = make_index_info(2, 2)
    return render_template("add_device.html", index_info=index_info)

@app.route("/download_rac")
def download_rac():
    return send_from_directory(rac_file_path, "480.WibuCmRac", as_attachment=True)

@app.route("/upload_rau", methods=["POST", "GET"])
def upload_rau():
    global manager_node_ip
    global manager_node_username
    global manager_node_password
    if request.method == "POST":
        data = request.get_json()
        rau_path = data["path"]
        rau_name = os.path.splitext(rau_path)[-1]
        rau_to_upload = FileToUpload("rau", rau_path, rau_name)
        rau_to_upload.upload_file(manager_node_ip, manager_node_username, manager_node_password)
        return jsonify({"status":200, "result":"上传rau文件成功"})

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/test1", methods=["POST", "GET"])
def test1():
    data = request.values
    print(data)
    return redirect("/test")
# 查看文件夹中是否有文件
# TBD 文件验证或者文件放在指定版本文件夹
# def check_imgs(file_path):
#     global files_to_upload
#     if(os.path.exists(file_path)):
#         for img in os.listdir(file_path):
#             img_local_file_path = file_path + "/" + img
#             img_to_upload = FileToUpload(img, local_file_path=img_local_file_path, remote_file_path="")
#             files_to_upload.append(img_to_upload)
#         return True
#     else:
#         return False

class FileToUpload:
    def __init__(self, name, local_file_path, remote_file_path) -> None:
        self._name = name
        self._local_file_path = local_file_path
        self._remote_file_path = remote_file_path
        self._upload_status = False
    
    def upload_file(self, manager_node_ip, manager_node_username, manager_node_password):
        try:
            tran = paramiko.Transport((manager_node_ip,22))
            tran.connect(username=manager_node_username, password=manager_node_password)
            sftp = paramiko.SFTPClient.from_transport(tran)
            sftp.put(localpath=self._local_file_path, remotepath=self._remote_file_path, callback=self.upload_status)
            tran.close()
            sftp.close()
        except Exception as e:
            print("出错了，{}".format(e))
            tran.close()
            sftp.close()

    def upload_status(self, bytes, max_bytes):
        socketio.emit("upload_status", {"filename":self._name, "bytes":bytes, "max_bytes":max_bytes})
        if bytes == max_bytes:
            self._upload_status = True
            print("上传完毕")

class FileToDownload:
    def __init__(self, name, local_file_path, remote_file_path) -> None:
        self._name = name
        self._local_file_path = local_file_path
        self._remote_file_path = remote_file_path
        self.download_status = False
    
    def upload_file(self, manager_node_ip, manager_node_username, manager_node_password):
        try:
            tran = paramiko.Transport((manager_node_ip,22))
            tran.connect(username=manager_node_username, password=manager_node_password)
            sftp = paramiko.SFTPClient.from_transport(tran)
            sftp.get(localpath=self._local_file_path, remotepath=self._remote_file_path, callback=self.download_status)
            tran.close()
            sftp.close()
        except Exception as e:
            print("出错了，{}".format(e))
            tran.close()
            sftp.close()

    def download_status(self, bytes, max_bytes):
        socketio.emit("download_status", {"filename":self._name, "bytes":bytes, "max_bytes":max_bytes})
        if bytes == max_bytes:
            self.download_status = True
            print("上传完毕")

class ManagerNodeInfo:
    def __init__(self, manager_node_ip, manager_node_username, manager_node_password) -> None:
        self.manager_node_ip = manager_node_ip
        self.manager_node_username = manager_node_username
        self.manager_node_password = manager_node_password

def exec_shell_command(hostname, username, password, port, shell_command, func_type):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=hostname, username=username, password=password, port=port)
        stdin, stdout, stderr = ssh_client.exec_command(shell_command)
        while True:
            if func_type == "install":
                lines = stderr.readlines(20)
                if lines.__len__() != 0:
                    print(lines)
                    ssh_client.close()
                    break
            lines = stdout.readlines(20)
            if func_type == "upload":
                if lines.__len__() == 0:
                    break
            for line in lines:
                socketio.emit("log_on", line)
    except Exception as e:
        print(e)

def exec_shell_commands(hostname, username, password, port, shell_commands, func_type):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=hostname, username=username, password=password, port=port)
        for command in shell_commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            while True:
                if func_type == "install":
                    lines = stderr.readlines(20)
                    if lines.__len__() != 0:
                        print(lines)
                        ssh_client.close()
                        break
                lines = stdout.readlines(20)
                if func_type == "upload":
                    if lines.__len__() == 0:
                        break
                for line in lines:
                    socketio.emit("log_on", line)
    except Exception as e:
        print(e)



# socket 函数
@socketio.on("upload")
def upload_img_socket(data):
    global manager_node_ip
    global manager_node_username
    global manager_node_password
    global pangu_install_zip_name
    global files_to_upload
    global remote_pangu_auto_install_dir
    global project_info_path
    global manager_node_info
    func_type = "upload"
    print("socket 连接成功，信息：{},检查信息并上传文件。".format(data["data"]))
    
    if manager_node_ip == "":
        return redirect("/")
    
    try:
        port = 22
        # 在远程服务器创建以年月日时分秒（如20220120152559）的文件夹
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        remote_file_dir = "/home/security/{}/".format(timestamp)
        command_mkdir_remote_file_dir = "mkdir {}".format(remote_file_dir)
        exec_shell_command(hostname=manager_node_ip,
        username=manager_node_username,
        password=manager_node_password,
        port=port,
        shell_command=command_mkdir_remote_file_dir,
        func_type=func_type)

        def upload_log_print(func_type, name, bytes, total_btyes):
            socketio.emit("upload_status", {"filename":name, "bytes":bytes, "max_bytes":total_btyes})

        # 上传pangu_auto_install 工具包
        pangu_auto_install_zip_name = pangu_install_zip_name
        pangu_auto_install_zip_path = "file/pangu_auto_install/{}".format(pangu_auto_install_zip_name)
        remote_pangu_auto_install_zip_path = remote_file_dir + pangu_auto_install_zip_name
        name = "pangu_auto_install"
        # file_pangu_install_zip = FileToUpload(name, pangu_auto_install_zip_path, remote_pangu_auto_install_zip_path)
        # file_pangu_install_zip.upload_file(manager_node_ip, manager_node_username, manager_node_password)
        file_pangu_install_zip = TransFile(name, pangu_auto_install_zip_path, remote_pangu_auto_install_zip_path, manager_node_info, upload_log_print)
        file_pangu_install_zip.upload()

        # 对工具进行解压操作以及初始化操作
        commands = ["rm -rf {}".format(remote_pangu_auto_install_dir), "unzip {}".format(remote_pangu_auto_install_zip_path), 
        "sudo rm -rf /usr/bin/installctl", "bash ./{}/config.sh && source ~/.bashrc".format(remote_pangu_auto_install_dir)]
        for command in commands:
            exec_shell_command(hostname=manager_node_ip,
            username=manager_node_username,
            password=manager_node_password,
            port=port,
            shell_command=command,
            func_type=func_type)

        # 上传project_info文件
        remote_project_info_path = "{}/project_info".format(remote_pangu_auto_install_dir)
        # proj_info_to_load = FileToUpload("project_info", project_info_path, remote_project_info_path)
        # _thread.start_new_thread(proj_info_to_load.upload_file, (manager_node_ip, manager_node_username, manager_node_password,))
        proj_info_to_load = TransFile("project_info", project_info_path, remote_project_info_path, manager_node_info, upload_log_print)
        _thread.start_new_thread(proj_info_to_load.upload)

        trans_files =[]
        for img in files_to_upload:
            trans_file = TransFile(img[0], img[1], img[2], manager_node_info, upload_log_print)
            trans_files.append(trans_file)
            _thread.start_new_thread(trans_file.upload)
            # img._remote_file_path = "{}/images/{}".format(remote_pangu_auto_install_dir,img._name)
            # _thread.start_new_thread(img.upload_file, (manager_node_ip, manager_node_username, manager_node_password,))
        # 上传镜像文件到images文件夹
        # 判断是否所有文件都上传完毕
        is_upload_success = False
        while True:
            for trans_file in trans_files:
                if trans_file.status == False:
                    is_upload_success = False
                    break
                else:
                    is_upload_success = True
            if is_upload_success == True:
                socketio.emit("upload_success")
                break

    except Exception as e:
        print("有错误{}".format(e))

@socketio.on("install_devops")
def install_devops_begin():
    global is_in_company
    global manager_node_ip
    global manager_node_username
    global manager_node_password

    port = 22
    func_type = "install"
    
    if manager_node_ip == "":
        return redirect("/")
    
    if is_in_company == True:
        command_install = ["installctl -in", "installctl -l"]
    else:
        command_install = ["installctl -i", "installctl -l"]
    exec_shell_commands(hostname=manager_node_ip, username=manager_node_username, password=manager_node_password, port=port, shell_commands=command_install,func_type=func_type)
    
    
@socketio.on("install_begin")
def install_begin():
    global is_in_company
    global manager_node_ip
    global manager_node_username
    global manager_node_password
    global remote_pangu_auto_install_dir
    global is_soft
    global dongle_ip  
    global file_path
    global rac_file_path

    port = 22
    func_type = "install"
    if manager_node_ip == "":
        return redirect("/")
    
    if is_in_company == True:
        command_install = ["installctl -in", "installctl -l", "installctl -L", "installctl -I", "installctl -c"]
        exec_shell_commands(hostname=manager_node_ip, username=manager_node_username, password=manager_node_password, port=port, shell_commands=command_install,func_type=func_type)
    else:
        command_install = ["installctl -i", "installctl -l"]
        # 产生加密狗授权申请文件
        command_dongle = "{}/bin/dongle export {} 480"
        if is_soft == "true":
            dongle_type = "soft"
            context = "5000468"
        else:
            dongle_type = "hard"
            context = "102507"
        command_dongle.format(remote_pangu_auto_install_dir, dongle_type)
        command_install.append(command_dongle)
        exec_shell_commands(hostname=manager_node_ip, username=manager_node_username, password=manager_node_password, port=port, shell_commands=command_install,func_type=func_type)
        # 下载加密狗授权文件
        name = "加密狗授权文件下载"
        path_date = time.strftime("%Y%m%d", time.localtime())
        local_rac_file_path = "{}{}/480.WibuCmRac".format(file_path,path_date)
        remote_rac_file_path = "dongle-{}-*.WibuCmRac".format(context)
        rac_file_download = FileToDownload(name, local_rac_file_path, remote_rac_file_path)
        rac_file_download.upload_file(manager_node_ip, manager_node_username, manager_node_password)
        rac_file_path = "{}{}".format(file_path,path_date)
        if rac_file_download.download_status == True:
            socketio.emit("download_rac")
            socketio.event("upload_rau")
        
@socketio.on("layout_begin")
def layout_begin():
    func_type = "install"
    layout_addr = "10.122.48.15"
    ping_ret = ping(layout_addr)
    # 判断本机是否能到达编排服务器
    if ping_ret == None:
        # 不能ping通编排服务器
        pass
    else:
        # 可以ping通编排服务器，执行全部命令
        pass
    # TBD 下载指纹文件，导入证书文件，启动服务

if __name__ == "__main__":
    socketio.run(app)

core_sevices = {
    "1":"faced-video",
    "2":"faced-capture",
    "3":"videod-engine",
    "4":"videod-capture",
    "5":"algowarehouseA",
    "6":"algowarehouseB",
    "7":"archer",
    "8":"algowarehouseC",
    "9":"algowarehouseD"
}
    