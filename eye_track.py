import cv2, dlib
import numpy as np
from imutils import face_utils
from keras.models import load_model
from keras.utils import load_img, img_to_array,array_to_img
import matplotlib.pyplot as plt
import time
import os 
import pickle

IMG_SIZE = (100, 100)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')

def crop_eye(gray, eye_points):
    x1, y1 = np.amin(eye_points, axis=0)
    x2, y2 = np.amax(eye_points, axis=0)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

    w = (x2 - x1) * 1.2
    h = w * IMG_SIZE[1] / IMG_SIZE[0]

    margin_x, margin_y = w / 2, h / 2

    min_x, min_y = int(cx - margin_x), int(cy - margin_y)
    max_x, max_y = int(cx + margin_x), int(cy + margin_y)

    eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(int)
    temp1 = eye_rect[3]-eye_rect[1]
    while  temp1 != 100:
        if temp1 < 100:
            eye_rect[3]+=0.5
            eye_rect[1]-=0.5
        else:
            eye_rect[3]-=0.5
            eye_rect[1]+=0.5
        temp1 =(eye_rect[3]-eye_rect[1])
    
    temp2 = eye_rect[2]-eye_rect[0]
    while  temp2 != 100:
        if temp2 < 100:
            eye_rect[2]+=0.5
            eye_rect[0]-=0.5
        else:
            eye_rect[2]-=0.5
            eye_rect[0]+=0.5
        temp2 =(eye_rect[2]-eye_rect[0])
    eye_img = gray[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]
    return eye_img, eye_rect

# main
# 동영상 넣으려면 아래 변수 0대신 동영상 파일 넣으면 됩니다.


# data 가져오기
awaken_list = [f for f in os.listdir('./nd1/') if not f.startswith('.')]
sleeping_list = [f for f in os.listdir('./drawsy/') if not f.startswith('.')]

videos = []  # 실제 데이터-> (각 영상으로부터 추출한 50장의 눈 사진 이미지)들의 배열 
video_labels = []  # 정답 데이터(1,0으로 분류) -> 0은 sleeping 1은 awaken


def capture(path): #video를 입력받아 image array를 return(numpy ndarray)
    cap = cv2.VideoCapture(path)
    count = 0
    m = 50
    images_array = []

    # 5초에 50장 뽑아냄
    while count<m:
        time.sleep(0.1)
        ret, img_ori = cap.read()


        if not ret:
            raise Exception("캡처가 없음")

        img_ori = cv2.resize(img_ori, dsize=(0, 0), fx=0.5, fy=0.5)

        img = img_ori.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = detector(gray)

        for face in faces:
            shapes = predictor(gray, face)
            shapes = face_utils.shape_to_np(shapes)
            x = face.left()
            y = face.top() #could be face.bottom() - not sure
            w = face.right() - face.left()
            h = face.bottom() - face.top()

            eye_img_l, eye_rect_l = crop_eye(gray, eye_points=shapes[36:42])
            eye_img_r, eye_rect_r = crop_eye(gray, eye_points=shapes[42:48])
            ex,ey,ew,eh = eye_rect_l
            eye_img_l = cv2.resize(eye_img_l, dsize=IMG_SIZE)
            eye_img_r = cv2.resize(eye_img_r, dsize=IMG_SIZE)
            eye_img_r = cv2.flip(eye_img_r, flipCode=1)
            cv2.rectangle(img, (ex,ey), (ew,eh), color=(255,255,255), thickness=1)
            images_array.append(eye_img_l)
            
            # print(img[ey:eh,ex:ew,:].shape)
        count+=1
        cv2.imshow('result', img)
        if cv2.waitKey(1) == ord('q'):
            break
    return np.array(images_array)
# images_array => 5초에 50장 저장한 배열

for i in awaken_list:
    print(i)
    array = capture("./nd1/"+i)
    videos.append(array)
    video_labels.append(1)  # 깨어있는 영상 : 

for i in sleeping_list:
    print(i)
    array = capture("./drawsy/"+i)
    videos.append(array)
    video_labels.append(0)





#재사용가능하게 디렉토리에 pickle 모듈로 저장
with open("videos_array","wb") as va:
    pickle.dump(videos,va)
with open("video_labels","wb") as vl:
    pickle.dump(video_labels, vl)


#window close
cv2.destroyAllWindows()