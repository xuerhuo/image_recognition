import requests
import os

#此处路径自己修改， 
path='G:\py\identfying_code_recognize\imgs\\'
num=1000
# if os.path.exists(path):
#     pass
# else:
#     os.makedirs(path)
# for i in range(0,num):
#     print("下载第"+str(i)+"张验证码")
#     filePath=path+str(i)+'.png'
#     #这个地址下可以下载到普通的验证码
#     r=requests.get('http://jx.cqxscx.com/image')
#     with open(filePath,'bw') as f:
#         f.write(r.content)
#
