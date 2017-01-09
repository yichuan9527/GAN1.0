import cv2
import os 
import re
path = 'E:\ubuntu_data\picture'
def read_image_list(path):
#reurn he name list of the picture 
    image = os.listdir(path)
    sample = []
    pattern = re.compile(r'(\d+)')
    for item in image:
        if item[:3]=='sam':
            item = os.path.join(path, item)
            sample.append(item)
    image_list = range(len(sample))
    for item in sample:
        num = int(pattern.split(item)[1])
        image_list[num] = item
    return image_list

def write_video(image_list):
    fps = 24
    fourcc = cv2.cv.FOURCC(*'DVIX')
    vedioWriter = cv2.VideoWriter('out.avi',-1, fps, (259, 259))#-1 is to select the video encoder
    for name in image_list:
        frame = cv2.imread(name)
        vedioWriter.write(frame)
    vedioWriter.release()
    
image_list = read_image_list(path)
write_video(image_list)