from flask import *
from proj_info import *
import os, time
from flask_socketio import *

project_info_path = ""
pangu_install_zip_path = "file/pangu_auto_install.zip"
manager_node_ip = ""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def index():
    # index_info = {"topic":"盘古自动部署工具",
    #  "steps":[{"name":"项目配置", "is_active":True},{"name":"项目部署","is_active":False},{"name":"信息下载", "is_active":False}],
    #   "navs":[{"name":"自动部署工具", "is_active":True, "herf":"/"}, {"name":"小工具", "is_active":False, "herf":"/tools"}]}
    # return render_template("proj_info.html" ,index_info=index_info)
    return redirect("/proj_info")

@app.route("/proj_info", methods=["POST", "GET"])
def proj_info():
    if request.method == "GET":
        index_info = {"topic":"盘古自动部署工具",
        "steps":[{"name":"项目配置", "is_active":True}, {"name":"镜像上传","is_active":False}, {"name":"项目部署","is_active":False},{"name":"信息下载", "is_active":False}],
        "navs":[{"name":"自动部署工具", "is_active":True, "herf":"/"}, {"name":"小工具", "is_active":False, "herf":"/tools"}]}
        return render_template("proj_info.html" ,index_info=index_info)
    else:
        data = request.get_json()
        # 拼接服务字符串如"faced-video*2,faced-capture*2"
        arr_service_info = data["arr_service_info"]
        str_services_info = ""
        for i, service_info in enumerate(arr_service_info):
            if i < len(arr_service_info) - 1:
                str_service_info = "{}*{},".format(core_sevices[service_info[0]], service_info[1])
            elif i == len(arr_service_info) - 1:
                str_service_info = "{}*{}".format(core_sevices[service_info[0]], service_info[1])
            str_services_info += str_service_info

        # 分配服务所在节点，pangu,gsp,gmp,iot,core,algowarehouse
        # services_all = ["pangu","gsp","gmp","iot","core"]
        devices_info = ""
        devices = data["arr_devices_info"]
        if len(arr_service_info) == 1 and arr_service_info[0][1] == "":  # 没有core服务，只需要部署盘古服务
            local_service = "pangu,gsp"
            # 只需要一个节点，则第一个节点为devops-manager节点
            devices_info = manager_node.format(1, devices[0][0], devices[0][1], devices[0][2],local_service)
            manager_node_ip = devices[0][0]
        elif arr_service_info[0][1] != "" and len(devices) == 1:
            local_service = "pangu,gmp,core,iot,gsp"
            devices_info = manager_node.format(1, devices[0][0], devices[0][1], devices[0][2],local_service)
            manager_node_ip = devices[0][0]
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
        data["pangu_version"],
        str_services_info,
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

        project_info_path = real_path

        return jsonify({"status":200,"result":"OK"})

@app.route("/upload_img", methods=["POST", "GET"])
def upload_img():
    if request.method == "GET":
        index_info = {"topic":"盘古自动部署工具",
            "steps":[{"name":"项目配置", "is_active":False}, {"name":"镜像上传","is_active":True}, {"name":"项目部署","is_active":False},{"name":"信息下载", "is_active":False}],
            "navs":[{"name":"自动部署工具", "is_active":True, "herf":"/"}, {"name":"小工具", "is_active":False, "herf":"/tools"}]}
        return render_template("upload_img.html",index_info=index_info)
    else:
        # TBD 传盘古部署工具zip，解压，初始化
        # TBD 传project_info文件
        # TBD 传镜像到images文件夹下
        data = request.get_json()
        print(data)
        return jsonify({"status":200,"result":"OK"})
        
@app.route("/tools")
def tools():
    index_info = {"topic":"小工具",
     "steps":[{"name":"加密狗配置", "is_active":True, "herf":"/tools"},{"name":"证书下载","is_active":False, "herf":"/cerf"},{"name":"添加相机", "is_active":False, "herf":"/add_device"}],
      "navs":[{"name":"自动部署工具", "is_active":False, "herf":"/"}, {"name":"小工具", "is_active":True, "herf":"/tools"}]}
    return render_template("dongle.html" ,index_info=index_info)

@app.route("/cerf")
def cerf():
    index_info = {"topic":"小工具",
     "steps":[{"name":"加密狗配置", "is_active":False, "herf":"/tools"},{"name":"证书下载","is_active":True, "herf":"/cerf"},{"name":"添加相机", "is_active":False, "herf":"/add_device"}],
      "navs":[{"name":"自动部署工具", "is_active":False, "herf":"/"}, {"name":"小工具", "is_active":True, "herf":"/tools"}]}
    return render_template("cerf.html", index_info=index_info)

@app.route("/add_device")
def add_device():
    index_info = {"topic":"小工具",
     "steps":[{"name":"加密狗配置", "is_active":False, "herf":"/tools"},{"name":"证书下载","is_active":False, "herf":"/cerf"},{"name":"添加相机", "is_active":True, "herf":"/add_device"}],
      "navs":[{"name":"自动部署工具", "is_active":False, "herf":"/"}, {"name":"小工具", "is_active":True, "herf":"/tools"}]}
    return render_template("add_device.html", index_info=index_info)

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/test1", methods=["POST", "GET"])
def test1():
    data = request.values
    print(data)
    return redirect("/test")


# socket 函数
@socketio.on("upload")
def upload_img_socket(data):
    print("socket 连接成功，信息：{},检查信息并上传文件。".format(data["data"]))
    # socketio.start_background_task()
    for i in range(1,100):
        socketio.emit("log_on", "第{}条信息。".format(i))
        time.sleep(1)


# # 常用函数
# def upload_img()

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
    