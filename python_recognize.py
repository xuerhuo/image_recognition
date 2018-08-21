import json
import time
import pytesseract
from PIL import Image
import traceback
import random
import matplotlib.pyplot as plt
import python_getpic
import os
#此函数用于设置像素值的转换，
def set_table(a):
    table=[]
    for i in range(256):
        if i<a:
            table.append(0)
        else:
            table.append(1)
    return table
# 降噪
def noise(pixdata,width,height):
    for y in range(0, height):
        for x in range(0,width):
            count = 0
            # print(pixdata[x,y],end='')
            if y>0 and pixdata[x, y - 1] > 0: count = count + 1
            if y<height-1 and pixdata[x, y + 1] > 0: count = count + 1
            if x>0 and pixdata[x - 1, y] > 0: count = count + 1
            if x<width-1 and pixdata[x + 1, y] > 0 : count = count + 1
            if x<width-1 and y<height-1 and pixdata[x + 1, y+1] > 0 : count = count + 1
            if x>0 and y>0 and pixdata[x - 1, y-1] > 0 : count = count + 1
            if x>0 and y<height-1 and pixdata[x - 1, y+1] > 0 : count = count + 1
            if x<width-1 and y>0 and pixdata[x + 1, y-1] > 0 : count = count + 1
            if count >=5 or y==0 or y==height-1:
                pixdata[x, y] = 1
            pass
        # print('\n',end='')
    return  pixdata;
# 图像分割
def division(pixdata,width,height):
    result ={}
    xx = []
    ret = []
    fx = []
    divisionpoint = []
    # 线性
    for x in range(0, width):
        count = 0
        for y in range(0, height):
            if pixdata[x,y]==0:
                count+=1
        ret.append(count)
        xx.append((x,count))
    result['count'] = ret
    temp = 0
    tempret = xx.copy()
    # 锐化波谷
    for v in xx:
        temp+=1
        if xx.index(v)>0:
            w,y = xx[xx.index(v)-1]
            if v[1]==y:
                r = xx[xx.index(v)-1]
                tempret.remove(r)
    xx = tempret
    ret=[]
    #求波谷
    for v in xx:
        index = xx.index(v)
        if index==0:
           ret.append(v)
        elif index<len(xx)-1:
            if v[1]<xx[index-1][1] and v[1]<xx[index+1][1]:
                ret.append(v)
    ret.sort(key=lambda  x:x[1])
    xx=ret.copy()
    ret = []
    for v in xx:
        ret.append(v[0])
    ret = ret[0:5]
    ret.sort()
    result['fxpoint'] = ret
    return  result;
def plot(img,img1,data):
    w,h = img.size
    plt.subplot(1, 2, 1)
    plt.plot(data['count'])
    plt.subplot(2, 2, 2)
    plt.plot([0, 5, 5, 0,0], [0, 0, 5, 5,0],'r')
    plt.imshow(img1)
    plt.subplot(2, 2, 4)
    for dat in data['fxpoint']:
        plt.plot([dat,dat],[0,h],'r')
    plt.imshow(img)
    plt.show()
# 填充灰度
# 取样左上角5x5 然后灰度化
def filL(img):
    pdata = img.load()
    xy = {}
    for x in range(5):
        for y in range(5):
            l = pdata[x,y]
            if l in xy:
                xy[l]+=1
            else:
                xy[l]=0
    l = max(xy)
    (w,h) = img.size
    for x in range(w):
        for y in range(h):
            if pdata[x,y]!=l:
                pdata[x,y] = 0
            else:
                pdata[x, y] = 255
    return  img
# //切割图像
def dodivimg(img,diviarr):
    w,h = img.size
    imgs = []
    i=0
    for div in diviarr:
        if i==len(diviarr)-1:
            right = w
        else:
            right = diviarr[i+1]-div
            right+=div
        temp = img.crop((div,0,right,h))
        imgs.append(temp)
        i+=1
    return  imgs
# //生成基准数据
def writedata(imgs):
    i = 0
    for img in imgs:
        w,h = img.size
        pdata = img.load()
        temp = {}
        temp['data'] = []
        temp['width'] = w
        temp['height'] = h
        for x in range(w):
            for y in range(h):
                temp['data'].append(pdata[x,y])
                pass
        temp = json.dumps(temp)
        with open('data/x{num}.json'.format(num=str(i+1)), 'w') as f:
            f.write(temp)
        f.close()
        i+=1
    exit(0)
def readdata():
    ret = {}
    for dirpath, dirnames, filenames in os.walk('./data/'):
        for filepath in filenames:
            # print(os.path.join(dirpath, filepath))
            with open(os.path.join(dirpath, filepath),'r') as f:
                temp = f.read()
                ret[filepath.split('.')[0]]=json.loads(temp)
            f.close()
    return ret;
#汉明指纹 平均hash ahash
def recognize_1b(img, recdata):
    fx = []
    for k in recdata:
        dat = recdata[k]
        img = img.resize((dat['width'],dat['height']))
        pxdata = img.load()
        tempfx = []
        for x in range(dat['width']):
            for y in range(dat['height']):
                tempfx.append(pxdata[x,y])
        i=0
        count = 0
        for bit in dat['data']:
           # print(bit,tempfx[i])
           if bit!=tempfx[i]:
               count+=1
           i+=1
        fx.append((k,count))
    fx.sort(key=lambda  x:x[1])
    ret = fx[0:1]
    # print(ret[0])
    return ret[0][0]
def recognize_imgs(imgs):
    recdata = readdata()
    ret = ""
    for img in imgs:
        temp = recognize_1b(img,recdata)
        ret+=temp
    return  ret
def recognize_picture(p,r):
    readdata()
     # 这个识别函数的过程是：首先对图像进行灰度处理，然后对验证码中每个数字进行切割，如果有四个数字，就切割成四份
     # 每一个数字相是由一个像素矩阵组成，然后求取每个数字的像素矩阵的特征值，然后再通过特征向量来匹配验证码。
    img=Image.open(p)
    img1=img.convert("L")
    img1=filL(img1)
    imgl=img1
    #convert函数的作用：将图片转化为其他种类的色彩模式，如灰度图（将黑白之间分成若干个等级），
    #二值图（非黑即白），相关的模式有‘1，L,P,RGB.....’，这里用到的模式为L 转化为灰度图，
    #set_table（140）140是一个分界线，大于这个值的像素色值设为1，小于140的设为0，
    img2=img1.point(set_table(200),'1')
    pix2=img2.load()
    #得到这个图片像素的宽高
    (width,heigh)=img2.size
    x0=[]
    y0=[]
    pix2 = noise(pixdata=pix2,width=width,height=heigh)
    pix2 = noise(pixdata=pix2,width=width,height=heigh)
    data = division(pixdata=pix2,width=width,height=heigh)
    plot(img2,img,data)
    imgs = dodivimg(img2,data['fxpoint'])
    # writedata(imgs)
    text = recognize_imgs(imgs)
    print("第{i}张图 为:{t}".format(i=str(r),t=text))
    return True
global_path=python_getpic.path+r"recognize/"
if __name__=='__main__':
    q=0
    end=python_getpic.num
    if os.path.exists(global_path):  
        pass
    else:
        os.makedirs(global_path)
    for i in range(5):
        i = random.randint(1,end)
        print(i)
        try:                
            p=python_getpic.path+str(i)+".png"
            recognize_picture(p,i)
        except:
            print('something wrong')
            traceback.print_exc()
            break;
    # print("识别了"+str(q)+"张验证码",'正确率为'+str((q/end)*100)+"%")