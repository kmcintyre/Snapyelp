print 'Using QT'
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QKeyEvent, QMouseEvent
import os
os.environ['LIBOVERLAY_SCROLLBAR'] = '0'
os.putenv('DISPLAY', ':0')
version = '5.3.1'
class Browser(QApplication):
    pass
    '''
    def notify(self, receiver, event):
    #    print 'hello:', event
        if isinstance(event, QKeyEvent):
            pass
            # print event.key(), event.type()
        if isinstance(event, QMouseEvent):
            #print event.pos().x(), event.pos().y(), '    ', event.__class__.__name__
            pass 
        #print 'receiver:', receiver
        return super(Browser, self).notify(receiver, event)
    '''
app = Browser([])
def get_app():
    return app
from snapyelp.qt import qt5reactor
qt5reactor.install()
if __name__ == '__main__':
    from twisted.internet import reactor
    from snapyelp.base import BaseWindow
    sw = BaseWindow()
    sw.xmlrpc_toggle()
    import sys
    if len(sys.argv) > 1:
        print sys.argv[1]
        sw.xmlrpc_goto_url(sys.argv[1])
    port = 8001    
    from twisted.web import server
    reactor.listenTCP(port, server.Site(sw))        
    reactor.run()