import cv2
vidcap = cv2.VideoCapture('highway.mp4')
success,image = vidcap.read()
fps = vidcap.get(cv2.CAP_PROP_FPS)
totalframes = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
frame2skip = 5  # num of frames to skip when extracting
outputframe = int(totalframes / frame2skip)
print('Video FPS rate is {}'.format(fps))
print('You will get {} frames in total'.format(outputframe))
while success:
    frameId = int(round(vidcap.get(1)))
    success, image = vidcap.read()
    if frameId % frame2skip == 0:
        cv2.imwrite('itungitung frame_%d.jpg' % frameId, image)
        print('Export frame {}: '.format(frameId), success)
vidcap.release()
print ('Extraction completed!')