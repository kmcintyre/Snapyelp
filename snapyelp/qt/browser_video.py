'''
Created on Oct 12, 2014

@author: kevin

Extended QT modules to enable Video Caputure of Safari  
'''


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QEvent, QSize, QUrl
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWebKitWidgets import QWebView
import cv2
import os

os.environ['LIBOVERLAY_SCROLLBAR'] = '0'
os.putenv('DISPLAY', ':0')

#from pyscewpt import fixed

target_video = 'video.avi'
video_bucket = None
google_role = None
folder = None
import sys
url = 'www.youtube.com'
if len(sys.argv) > 1:
    url = sys.argv[1]
if len(sys.argv) > 2:
    print 'set video:',sys.argv[2]
    target_video = sys.argv[2]
else:
    print 'create video:', target_video
    
if len(sys.argv) > 3:
    from snapyelp.aws import bucket_util
    video_bucket = bucket_util.bucket_conv(sys.argv[3])
    folder = '/upload/'
    if len(sys.argv) > 4:
        folder = '/' + sys.argv[4] + '/'        
    if len(sys.argv) > 5:
        google_role = sys.argv[5]
        
    
if '.avi'not in target_video:
    target_video += '.avi'
print 'VIDEO:', target_video, url, folder, google_role 

class VideoBrowser(QApplication):    
    painter = QPainter()    
    events = []
    ready = False
    video = None
    def isReady(self):
        print 'READY!'
        VideoBrowser.ready = True
        VideoBrowser.video = cv2.VideoWriter(target_video, cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), 24, (1024, 768), True)        
    def done(self):
        if VideoBrowser.video and VideoBrowser.video.isOpened():
            cv2.destroyAllWindows()
            VideoBrowser.video.release()         
    def notify(self, receiver, event):
        if VideoBrowser.ready and isinstance(receiver, QWebView) and not VideoBrowser.painter.isActive():
            try:                
                image = QImage(QSize(1024, 768), QImage.Format_RGB32)                
                VideoBrowser.painter.begin(image)
                VideoBrowser.painter.setRenderHint(QPainter.Antialiasing, True)            
                VideoBrowser.painter.setRenderHint(QPainter.TextAntialiasing, True)            
                VideoBrowser.painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                VideoBrowser.painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
                receiver.page().mainFrame().render(VideoBrowser.painter)
                #print 'write'            
                image.save("temp.jpg", "jpg")                                    
                VideoBrowser.video.write(cv2.imread('temp.jpg'))
                VideoBrowser.painter.end()
            except Exception as e:
                print e
                    
        elif not event.type() in VideoBrowser.events:
            #print 'new type', receiver, event.type(), QEvent.User            
            VideoBrowser.events.append(event.type())
        else:
            pass      
        return super(VideoBrowser, self).notify(receiver, event)

app = VideoBrowser([])
from snapyelp.qt import qt5reactor
qt5reactor.install()

def end(ign = None, ign2 = None):
    print 'the end'
    if video_bucket:
        print 'upload to bucket:', folder + target_video
        bucket_util.save_s3(video_bucket, folder + target_video, None, target_video)
    reactor.stop()
        
if __name__ == '__main__':
    from twisted.internet import reactor
    from snapyelp.qt.base import BaseWindow
    import signal
    signal.signal(signal.SIGINT, end)
    
    sw = BaseWindow()
    sw.xmlrpc_toggle()
    app.isReady()
    d = w.web_page.page_deferred({'URI':fixed.simpleurl(url)})
    reactor.run()