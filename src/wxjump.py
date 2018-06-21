import os
import cv2
import math
import numpy as np
import time
import shutil
import random

path = os.getcwd()

#拷贝手机截屏到电脑中
def captureScreenShotToImg(path):
    os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
    os.system("adb pull /sdcard/screenshot.png ~/study/pythonadb/img/%s.png" % path)

#检测跳一跳的结果是否正确
def checkIsFail(result_shot_img):
    return False

#寻找棋盘落点
def findDropPoint(current_screen_img_gray, start_h, end_h, step, hold_x):
    fetch_w = 0
    fetch_h = 0
    for h in range(start_h, end_h, step):
        # print("start:%d" % (current_screen_img_gray[h, 0]))
        line0 = current_screen_img_gray[h, 0]
        for w in range(0, current_screen_img_gray.shape[1], step):
            linew = current_screen_img_gray[h, w]
            if line0 != linew:
                print("current_index:%d line0:%d  linew:%d" % (current_index, line0, linew))
                if abs(w - hold_x) > 50:
                    print("w:%d   hold_x:%d" % (w, hold_x))
                    for h2 in range(h - 20, h + 20, 1):
                        for w2 in range(w - 20, current_screen_img_gray.shape[1], 1):
                            if current_screen_img_gray[h2, 0] != current_screen_img_gray[h2, w2]:
                                if abs(w2 - hold_x) > 50:
                                    # 向下遍历
                                    h4 = h2
                                    for h3 in range(h2, h2 + 250):
                                        if current_screen_img_gray[h3, w2] == current_screen_img_gray[h2, w2]:
                                            h4 = h3
                                    print("h2 :%d   h4:%d" % (h2, h4))
                                    if h4 - h2 < 30:
                                        fetch_h = (h2 + 20)
                                    elif h4 - h2 > 250:
                                        fetch_h = h2 + 125
                                    else:
                                        fetch_h = (h2 + h4) / 2
                                    fetch_w = w2
                                    return fetch_h, fetch_w
    return fetch_h, fetch_w

#当前的循环次数
current_index = 1
#跳一跳跳跃距离和时间的常数比
DEF_TOUCH_TIME = 1.39
#小棋子的 w
mt_pixel_w = 0
#小旗子的 h
mt_pixel_h = 0

#删除img文件夹
shutil.rmtree(path + r"/img")
#新建img文件夹
os.mkdir(path + r"/img")

while current_index < 100:
    screenshot = 'screenshot%d' % current_index
    captureScreenShotToImg(screenshot)
    # read img form screenshot
    current_screen_img = cv2.imread(path + r'/img/%s.png' % screenshot)
    current_screen_img_gray = cv2.cvtColor(current_screen_img, cv2.COLOR_BGR2GRAY)

    # find flag position 寻找棋子的位置
    lower_color = np.array([67, 45, 50])  # 设定BGR的阈值
    upper_color = np.array([100, 70, 70])
    hsv = cv2.cvtColor(current_screen_img, cv2.COLOR_BGR2HSV)  # 转到HSV空间
    mask_color = cv2.inRange(current_screen_img, lower_color, upper_color)
    cnts = cv2.findContours(mask_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)  # 找到面积最大的轮廓
        ((x, y), radius) = cv2.minEnclosingCircle(c)  # 确定面积最大的轮廓的外接圆
        mt_pixel_h = y + 40
        mt_pixel_w = x
        center = (int(x), int(y + 40))
        cv2.circle(current_screen_img_gray, center, int(radius + 10), (0, 0, 255), 3)  # 画出圆心
        cv2.circle(current_screen_img_gray, center, 3, (0, 0, 255), -1)

    # 从1/3处开始扫描
    size = current_screen_img_gray.shape
    start_h = int(size[0] / 3)

    diff_h1, diff_w1 = findDropPoint(current_screen_img_gray, start_h, start_h * 2, 3, mt_pixel_w)

    print("位置:w:%d   h:%d" % (diff_w1, diff_h1))

    center1 = (int(diff_w1), int(diff_h1))

    cv2.circle(current_screen_img_gray, center1, 10, (0, 255, 0), 1)
    cv2.circle(current_screen_img_gray, center1, 1, (0, 255, 0), 1)

    # 计算两个点间的距离 并adb 长按事件 进行跳跃
    diff_two_dot = math.sqrt(int((mt_pixel_h - diff_h1) ** 2) + int((mt_pixel_w - diff_w1)) ** 2)
    print("diff_two_dot:%d" % diff_two_dot)

    cv2.imwrite(path + r"/img/%s.png" % screenshot, current_screen_img_gray)

    touch_time = diff_two_dot * DEF_TOUCH_TIME
    print("touchTime:%d" % touch_time)

    ran = random.random() * 100
    # os.system('adb shell input swipe %d %d %d %d %d' % (100 + ran, 200 + ran, 100 + ran, 200 + ran, touch_time))
    os.system('adb shell input swipe 200 300 200 300 %d' % touch_time)
    # wait shell run stop
    time.sleep(float(touch_time / 1000))

    # do next

    # check result is ok
    result_shot = 'result_shot%d' % current_index
    captureScreenShotToImg(result_shot)
    result_shot_img = cv2.imread(path + r'/img/%s.png' % result_shot, cv2.IMREAD_ANYCOLOR)

    # check is fail
    current_index += 1
    if checkIsFail(result_shot_img):
        break
