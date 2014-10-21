'''
Created on Oct 12, 2014

@author: kevin

Extended QT modules to enable XML-RPC commands

As a rule of thumb these are kept away from browser.py & browser_video.py
  
'''

from PyQt5.QtCore import QUrl, QSize, Qt, QPoint
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtNetwork import QNetworkRequest
#, QNetworkAccessManager
from PyQt5.QtGui import QImage, QPainter

from snapyelp import fixed

import os
import gzip

class SimpleQWebPage(QWebPage):
    disconnect_timeout = 30
    browser_tmp_dir = fixed.tmp_dir
    def __init__(self, *args, **kwargs):
        super(SimpleQWebPage, self).__init__(*args, **kwargs)
        
        #self.networkAccessManager().finished.connect( self.networkFinished )
        
        self.loadStarted.connect(self._page_start)
        self.loadProgress.connect(self._page_progress)
        self.loadFinished.connect(self._page_finished)
        #networkFinished
        
        self.setView(QWebView())
        self.view().resize(QSize(1024, 768))
        self.view().setPage(self)
        self.view().urlChanged.connect(self._page_url_change)        
        self.settings().setAttribute(QWebSettings.AutoLoadImages, True)
        self.settings().setAttribute(QWebSettings.JavascriptEnabled, True)        
        self.settings().setAttribute(QWebSettings.JavaEnabled, False)        
        self.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, False)        
        self.settings().setAttribute(QWebSettings.PluginsEnabled, False)
        self.settings().setAttribute(QWebSettings.NotificationsEnabled, False)                
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.page_finished_deferred = []
        self.loader = None
        self.overrideUpload = None

    def networkFinished(self, reply):
        #print 'newwork finished:', str(reply.url().toString())        
        url = reply.url().toString()
        rc = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        scheme = str(reply.url().scheme())         
        if scheme in['https','http']:
            reply_seq = (url, rc)
            self.loader['replies'].append(reply_seq) 
            #if not self.gather:
            #    return
            #elif 'replies' not in self.gather:
            #    self.gather['replies'] = [reply_seq]  
            #else:
            #    self.gather['replies'].append(reply_seq)
        #else:
        #    print str(reply.url().fragment())
    def _page_progress(self, percent):
        self.loader['percentage'] = percent        
    def _page_start(self):
        self.loader = { 'percentage' : 0, 'replies' : []}
    
    def _page_finished(self, ok):        
        print 'page finished:', str(ok), self.loader['percentage'], (self.view().url().toString() if self.view() else 'No URL'), len(self.page_finished_deferred)
        for d in self.page_finished_deferred:
            if not d.called:
                #print self.percentage, self.view().url().toString()
                d.callback(ok)
                return  
        print 'no fired deferred' 
        
    def _page_url_change(self, url):
        #print '_url_change:', str(url.toString()), self.percentage
        pass
        

    def page_deferred(self, gather):
        #self.networkAccessManager().finished.connect( self.networkFinished )        
        print 'page_deferred', gather['URI']
        #print 'all cookies', self.networkAccessManager().cookieJar().allCookies()
        def cancel_timeout_and_forward(reply, timer):
            if not timer.called:
                #print 'cancel', reply, str(self.view().url().toString()), gather['URI']
                # print 'cancel page timer'
                timer.cancel()            
            return reply
        def delay_response(reply):
            d2 = defer.Deferred()
            d2.addCallback(lambda ign: reply)
            reactor.callLater(2.5, d2.callback, reply)
            return d2
        def timeout(timed_deferred):
            if not timed_deferred.called:
                print 'cancel request', self.view().url().toString()
                timed_deferred.cancel()
        def page_error(err):
            print 'page error', err, gather['URI']
            raise err
        d = defer.Deferred()
        
        timer = reactor.callLater(self.disconnect_timeout, timeout, d)                        
        d.addCallback(cancel_timeout_and_forward, timer)
        d.addCallback(delay_response)
        d.addErrback(page_error)
        
        self.page_finished_deferred.append(d)                
        self.view().load(QUrl(gather['URI']))            
        return d


    def save_html(self, root_file):
        filename = SimpleQWebPage.browser_tmp_dir + root_file + '.html'
        f = open(filename, 'w')
        f.write(str(self.mainFrame().toHtml()))
        f.close()
        return filename;

    def save_html_gzip(self, root_file, delete=True):
        
        filename = self.save_html(root_file)
        gzip_filename = filename + '.gz'        
        f_in = open(filename, 'rb')
        f_out = gzip.open(gzip_filename, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        if delete:
            os.remove(filename);            
        return gzip_filename

    def save_element_html(self, root_file):
        filename = SimpleQWebPage.browser_tmp_dir + root_file + '.html'
        f = open(filename, 'w')
        f.write(str(root_file.toOuterXml()))
        f.close()
        return filename;

    def local_archive(self, root_file):
        def add_png(lf):
            if '.png' in lf:
                return lf
            else:
                return lf + '.png'
        if SimpleQWebPage.browser_tmp_dir in root_file:
            return add_png(root_file)
        else:
            return SimpleQWebPage.browser_tmp_dir + add_png(root_file)

    def save_element_png(self, root_file, e, render_format = QImage.Format_ARGB32):
        #print 'save element:', root_file
        filename = self.local_archive(root_file)
        # print 'save_element_png' , e.geometry().width(), e.geometry().height()
        painter = QPainter()
        image = QImage(QSize(e.geometry().width(), e.geometry().height()), render_format)
        painter.begin(image)
        painter.setRenderHint(QPainter.Antialiasing, True)            
        painter.setRenderHint(QPainter.TextAntialiasing, True)            
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        e.render(painter)        
        if not os.path.exists(filename) and not os.path.exists(os.path.dirname(filename)): 
            os.makedirs(os.path.dirname(filename))
        image.save(filename, "png")
        #print filename
        return filename

    
    def save_png(self, root_file):
        print 'save png:', root_file
        filename = self.local_archive(root_file)
        print 'filename:', filename 
        width = self.viewportSize().width()
        height = self.viewportSize().height()
        if self.mainFrame().scrollBarMaximum(Qt.Vertical) > height:
            height = self.mainFrame().scrollBarMaximum(Qt.Vertical)
        if self.mainFrame().scrollBarMaximum(Qt.Horizontal) > width:
            width = self.mainFrame().scrollBarMaximum(Qt.Horizontal)            
        qs = QSize(width, height)
        self.setViewportSize(qs)
        image = QImage(QSize(width, height), QImage.Format_ARGB32)
        painter = QPainter()
        painter.begin(image)
        painter.setRenderHint(QPainter.Antialiasing, True)            
        painter.setRenderHint(QPainter.TextAntialiasing, True)            
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        self.mainFrame().render(painter)
        painter.end()
        if not os.path.exists(filename) and not os.path.exists(os.path.dirname(filename)): 
            os.makedirs(os.path.dirname(filename))
        image.save(filename, "png")        
        return filename
    
    def extension(self, extension, option, output):        
        print 'extension:', extension, option, output
        if (extension == self.ChooseMultipleFilesExtension):
            if self.overrideUpload is None:
                return super(SimpleQWebPage, self).extension(self, extension, option, output)
            file_upl = self.overrideUpload
            self.overrideUpload = None
            output.fileNames = [file_upl]
            return True
        return False                
        
from twisted.web.xmlrpc import XMLRPC
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtTest import QTest

from twisted.internet import defer, reactor

class BaseWindow(XMLRPC, QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        XMLRPC.__init__(self, allowNone=True)
        self.web_page = SimpleQWebPage()
        self.resize(QSize(1024, 768))
        self.setCentralWidget(self.web_page.view())
    
    def delay(self, ans = True, delay_sec=1):
        if delay_sec != 1:
            print 'delayed:', delay_sec, 'ans:', ans      
        d = defer.Deferred()
        d.addCallback(lambda ign: defer.succeed(ans))
        reactor.callLater(delay_sec, d.callback, ans)
        return d
            
    def xmlrpc_snapshot(self):
        try:
            self.web_page.save_png("snapshot") 
            return True
        except Exception as e:
            print 'snapshot failure:', e
            return False
                
    def xmlrpc_preview(self, html, suffix):
        print 'preview_html'
        try:
            d = defer.Deferred() 
            d.addCallback(lambda ign: self.web_page.save_png( ("preview_html_" + suffix if suffix else "preview_html") ))            
            self.web_page.page_finished_deferred.append(d)
            self.web_page.mainFrame().setHtml(html)            
            return d
        except Exception as e:
            print 'preview html failure:', e
            return False
        
    def xmlrpc_postview(self):
        self.web_page.mainFrame().setHtml('<html></html>')
        self.view().resize(QSize(1024, 768))

    def xmlrpc_toggle(self):
        print 'toggle'
        if self.isVisible():
            return self.hide()
        else:
            return self.show()
                
    def xmlrpc_goto_url(self, url):
        url = fixed.simpleurl(url)
        print 'goto:', url, ' from:', self.web_page.view().url().toString()
        d = self.web_page.page_deferred({'URI':url})
        return d

    def xmlrpc_click(self, x, y, delay_secs=1):
        print 'click:', x, 'x', y        
        QTest.mouseClick(self.web_page.view(), Qt.LeftButton, Qt.NoModifier, QPoint(x, y))
        return self.delay(True,delay_secs)

    '''
    must investigate
    '''
             
    def xmlrpc_doc(self, selector=None, mapping=None):        
        if selector is None:
            print 'doc dump'
            return self.web_page.mainFrame().documentElement().toOuterXml()
        else:
            print 'BETA map'
            response = []
            nl = self.web_page.mainFrame().documentElement().findAll(selector).toList();
            print selector, 'found nodes:', len(nl)
            for i, n in enumerate(nl):
                try:
                    if mapping is None:                                
                        response.append(str(n.toOuterXml()))
                    else:                    
                        clone = { 'id' : i }
                        for key, subselector in mapping.items():                        
                            #print 'map:', key, subselector
                            try:
                                def addnode(node):
                                    ans = unicode(node.toPlainText()).strip()
                                    if len(ans) == 0:
                                        ans = unicode(node.toOuterXml()).strip()                                     
                                    if key not in clone:
                                        clone[key] = ans
                                    elif key in clone and isinstance(clone[key], list):
                                        clone[key].append(ans)
                                    else:
                                        l = [clone[key]]
                                        l.append(ans)
                                        clone[key] = l
                                #print 'subselector', len(n.findAll(subselector))                                                                                                 
                                for subn in n.findAll(subselector):
                                    addnode(subn)
                            except Exception as e:
                                print 'error with key:', key, subselector, e
                        response.append(clone)
                except Exception as e:
                    print 'enumatation exception:', e, i, n.toOuterXml
            #print response
            return response
    
    def xmlrpc_flash_set(self, setting=True):        
        self.web_page.settings().setAttribute(QWebSettings.PluginsEnabled, setting)
        return self.web_page.page_deferred(gather={'URI':'http://www.adobe.com/software/flash/about/'})
    
