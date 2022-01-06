
proj_info_str = '''
# 项目名称，必填
project:{}

# 是否软狗:true/false，必填
soft_dog:{}

# 是否HA部署:true/false
HA:{}

# 集群虚拟ip，HA部署时必填
VIP:{}

# 加密狗ip,多个请用英文逗号隔开，与管理节点ip相同时可不填
dongleip:{}

# pangu版本:1.0.2rc1,1.0.2rc2,1.0.5rc1，必填
panguver:{}

# 要部署的服务：algowarehouseA*N,algowarehouseB*N,facedvideo*N,videoengine*N,facedcapture*N,captureengine*N,archer*N，部署core时必填
services:{}
# 是否部署一人一档:true/false
profilo:{}
# 是否需要脸人绑定:true/false
face_body_link:{}

# 算法仓镜像名称,megalarm:release_prod_101_3.0.0_hotfix2_8cbe827d_2070_hard-enc,megalarm:release_prod_101_3.0.0_hotfix2_8cbe827d_T4_hard-enc等
algowarehouseA:{}
algowarehouseB:{}

# 节点信息，ip，用户名，密码，标签：pangu,gsp,gmp,iot,core必填,algowarehouse需要指定时必填（一般所有显卡型号都一致时没必要填）newip仅在现有系统更改ip时填写即可(格式：192.168.1.1/24)。

'''

manager_node = '''
ManageNode{}:
    ip={}
    newip=
    newgw=
    user={}
    passwd={}
    tags={}
'''

agent_node = '''
AgentNode{}:
    ip={}
    newip=
    newgw=
    user={}
    passwd={}
    tags={}
'''