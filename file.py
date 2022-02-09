# 继承文件传递类、文件处理类

import paramiko
import os

class TransFile:
    def __init__(self, name, local_file_path, remote_file_path, service_info, callback_func) -> None:
        self.name = name
        self.local_file_path = local_file_path
        self.remote_file_path = remote_file_path
        self.status = False
        self.service_info = service_info
        self.trans_type = ""
        self.callback_func = callback_func
    
    #上传文件
    def upload(self):
        try:
            self.trans_type = "upload"
            tran = paramiko.Transport((self.service_info.manager_node_ip,22))
            tran.connect(username=self.service_info.manager_node_username, password=self.service_info.manager_node_password)
            sftp = paramiko.SFTPClient.from_transport(tran)
            sftp.put(localpath=self.local_file_path, remotepath=self.remote_file_path, callback=self.trans_status)
            tran.close()
            sftp.close()
            return True
        except Exception as e:
            print("出错了，{}".format(e))
            tran.close()
            sftp.close()
            return False
    
    # 下载文件
    def download(self):
        try:
            self.trans_type = "download"
            tran = paramiko.Transport((self.service_info.manager_node_ip,22))
            tran.connect(username=self.service_info.manager_node_username, password=self.service_info.manager_node_password)
            sftp = paramiko.SFTPClient.from_transport(tran)
            sftp.get(localpath=self.local_file_path, remotepath=self.remote_file_path, callback=self.trans_status)
            tran.close()
            sftp.close()
            return True
        except Exception as e:
            print("出错了，{}".format(e))
            tran.close()
            sftp.close()
            return False
    
    # 回调函数，接收传递文件数据
    def callback(self, args, func):
        func(args)

    # 接受文件传输的字节数和总字节数，回调传给外部函数
    def trans_status(self, bytes, total_bytes):
        if bytes == total_bytes:
            self.status = True
        self.callback_func(self.trans_type ,self.name, bytes, total_bytes)

# 检查文件
'''
参数说明：
files_dir:文件所在文件夹
file_type:文件类型，说明如下
          值1：镜像
          值2：加密狗授权升级文件
          值3：证书文件
'''
def file_check(files_dir, file_type):
    if file_type == 1:
        file_types = ["devops_release_pkg", "deb.run", "tar.gz", "tar.xz", ".tar"]
    elif file_type == 2:
        file_types = [".WibuCmRaU"]
    elif file_type == 3:
        file_types = [".devops_license"]
    files = []
    if(os.path.exists(files_dir)):
        return False, files
    for file in os.listdir(files_dir):
        for type in file_types:
            if type in file:
                name = file
                img_local_file_path = files_dir + "/" + file
                files.append([name, img_local_file_path])
                break
    return True, files
