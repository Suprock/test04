
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

# devops版本：仅公司内部署时指定
devopsver:{}

# pangu版本:1.0.2rc1,1.0.2rc2,1.0.5rc1,1.0.6rc1,1.0.6rc3,1.0.6.1,1.1.0rc1，必填
panguver:{}

# 要部署的服务：algowarehouseA*N,algowarehouseB*N,algowarehouseC*N,algowarehouseD*N,facedvideo*N,videoengine*N,
# facedcapture*N,captureengine*N,archer*N,facedvideo_800W*N,facedimage*N,facedfeature*N,imageengine*N,captureengine_800W*N，部署core时必填
# algowarehouseA警戒，algowarehouseB安监，algowarehouseC物品，algowarehouseD人数统计
services:{}

# 要部署的共卡附属服务，facedvideo*N与facedvideo_800W*N，algowarehouseA*N与algowarehouseC*N
extra_services:{}
# 要部署的共卡附属服务，facedvideo*N与facedvideo_800W*N，algowarehouseA*N与algowarehouseC*N
PPL:{}

# 是否部署一人一档:true/false
profilo:{}

# 是否需要脸人绑定:true/false
face_body_link:{}

# 算法仓镜像名称,megalarm:release_prod_101_3.0.0_hotfix2_8cbe827d_2070_hard-enc,megalarm:release_prod_101_3.0.0_hotfix2_8cbe827d_T4_hard-enc等
algowarehouseA:{}
algowarehouseB:{}
algowarehouseC:{}
algowarehouseD:{}
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