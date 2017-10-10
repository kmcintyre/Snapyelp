from PyQt5 import QtWebEngineWidgets 
print 'going QT-force load of QtWebEngineWidgets:', QtWebEngineWidgets

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap 
import os
import boto

if os.environ.get('QTDISPLAY'):
    print '    DISPLAY=', os.environ.get('QTDISPLAY')
    os.putenv('DISPLAY', os.environ.get('QTDISPLAY'))
else:
    print 'WTF?'
    os.putenv('DISPLAY', ':0')
from PyQt5 import QtCore
qt_version = QtCore.qVersion()
print 'version:', qt_version 

class App(QApplication):

    def initCapture(self):
        self.capture = True   
        self.opengl = None
        self.video = None
        self.frameCount = 0
        
    def frame(self):
        print  'asdf'
        #self.video, self.opengl
        if self.video and self.opengl:
            print self.opengl
            pixmap = QPixmap(self.opengl.size())
            self.opengl.render(pixmap)
            jpg = self.jpg_location + self.frameCount + '.jpg'
            pixmap.save(jpg)                        
            try:                 
                self.video.write( cv2.imread(jpg) )
                os.remove(jpg)
                self.frameCount += 1                
            except Exception as e:
                print '    OH no!', e
                
'''    
    def toVideo(self, fps=24, location = '/home/ubuntu/Desktop/capture.avi', jpg_location = '/tmp/capture.jpg'):
        fixed.filesubpath(location)
        fixed.filesubpath(jpg_location)
        self.location = location
        self.jpg_location = jpg_location
        print 'VIDEO CAPTURE', self.location, 'at:', fps        
        timer = QTimer()
        timer.timeout.connect(self.frame)
        self.timer = timer
        
        self.video = cv2.VideoWriter(self.location,  cv2.cv.CV_FOURCC('M','J','P','G'), fps, (800,600), True)
        #cv2.cv.CV_FOURCC('M','J','P','G')
        #self.video = cv2.VideoWriter(self.location,  -1, fps, (640,480), True)
        print 'is open:', self.video.isOpened()
        self.timer.start(1000/fps)
        
     
    def toImage(self, location = None):
        png = '/tmp/capture.png'
        if location:            
            png = location         
        print 'toImage:', location
        if not self.opengl:
            print 'no opengl'
            return
        fixed.filesubpath(png)
        print 'IMAGE CAPTURE', png, self.opengl
        pixmap = QPixmap(self.opengl.size())
        self.opengl.render(pixmap)
        pixmap.save(png)
        

    def notify(self, receiver, event):
        #print 'receiver:', receiver, 'event:', event
        if self.capture and isinstance(receiver, QWidget):
        #if self.capture and isinstance(receiver, QOpenGLWidget):
            if self.opengl is None or self.opengl != receiver: 
                #print '    SET OPENGL:', receiver
                self.opengl = receiver                      
        return super(App, self).notify(receiver, event)
'''
app = App([])
app.initCapture()

print 'created app'
from snapyelp.qt import qt5reactor
print 'install qt5reactor'
qt5reactor.install()
from twisted.internet import reactor

def signalDown(int1, int2, int3=None):
    if app.video:
        print 'stop video:', app.video
        app.timer.stop()
        app.video.release()
        print 'is open:', app.video.isOpened()
        #cv2.destroyAllWindows()            
    print 'signal down! calling app quit'
    app.closeAllWindows()
    reactor.stop()        
import signal
signal.signal(signal.SIGINT, signalDown)
