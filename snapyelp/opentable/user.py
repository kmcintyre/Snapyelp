from snapyelp.qt import browser
print browser.version 

from snapyelp.qt.base import BaseWindow
from snapyelp.aws import dynamo
from snapyelp import fixed

bw = BaseWindow()
bw.show()

domain = 'snapyelp.com'

from twisted.internet import reactor, defer

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
    

def login_done(res):
    if res:
        print 'login_done:', res
    else:
        return defer.fail("populate_login_and_enter")

def populate_account(res):
    if res:
        for cf in bw.web_page.mainFrame().childFrames():
            fn = cf.documentElement().findFirst('input[id="ucName_txtFirstName"]')
            if fn.hasAttributes():            
                for opt in cf.documentElement().findAll('select[id="cboCity"] option').toList()[1:]:
                    city = fixed.simplify_to_id(opt.toInnerXml())
                    select_value = opt.attribute('value')
                    try:
                        item = dynamo.OpenTable().get_item(city=city)
                        if 'city_id' not in item:
                            print 'need to add city_id', select_value
                        else:
                            print item
                            
                    except Exception as e:
                        print 'city not found:', e.__class__.__name__
                        fn.evaluateJavaScript('this.focus()')
                        QTest.keyClicks(bw.web_page.view(), 'Kevin', Qt.NoModifier, 20)
                        cf.documentElement().findFirst('input[id="ucName_txtLastName"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(bw.web_page.view(), 'McIntyre', Qt.NoModifier, 20)
                        cf.documentElement().findFirst('input[id="txtEmail"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(bw.web_page.view(), 'test@snapyelp.com', Qt.NoModifier, 20)            
                        cf.documentElement().findFirst('input[id="txtPassword"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(bw.web_page.view(), 'tererdfcv1', Qt.NoModifier, 20)            
                        cf.documentElement().findFirst('input[id="txtReEnterPassword"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(bw.web_page.view(), 'tererdfcv1', Qt.NoModifier, 20)
                        cf.documentElement().findFirst('input[id="chkIsAdmin"]').evaluateJavaScript('this.click()')
                        return
    else:
        return defer.fail("click_create_account")
            

def click_create_account(res, callback = populate_account):
    if res:
        post_click = defer.Deferred()
        bw.web_page.page_finished_deferred.append(post_click)    
        for cf in bw.web_page.mainFrame().childFrames():
            anchor = cf.documentElement().findFirst('a[id="lnkNotMemberReg"]') 
            if anchor.hasAttributes():
                post_click.addCallback(callback)
                anchor.evaluateJavaScript('this.click()')
        return post_click
    else:
        return defer.fail('click_sign_in')


def populate_login_and_enter(res):
    print 'populate_login'
    if res:
        for cf in bw.web_page.mainFrame().childFrames():
            input_email = cf.documentElement().findFirst('input[id="txtUserEmail"]')
            if input_email.hasAttributes():
                input_email.evaluateJavaScript('this.focus()')
                QTest.keyClicks(bw.web_page.view(), 'kevin70@yahoo.com', Qt.NoModifier, 20)
                cf.documentElement().findFirst('input[id="txtUserPassword"]').evaluateJavaScript('this.focus()')
                QTest.keyClicks(bw.web_page.view(), 'tererdfcvO1', Qt.NoModifier, 20)
                cf.documentElement().findFirst('span[id="lblMember"]').evaluateJavaScript('this.focus()')
                post_click = defer.Deferred()
                post_click.addCallback(login_done)
                bw.web_page.page_finished_deferred.append(post_click)                
                QTest.keyClick(bw.web_page.view(), Qt.Key_Enter, Qt.NoModifier, 250)
                return post_click
    else:
        defer.fail("click_sign_in")
    
def click_sign_in(ans, callback):
    print 'click sign in'
    anchor = bw.web_page.mainFrame().documentElement().findFirst('a[id="global_nav_sign_in"]')
    post_click = defer.Deferred()
    post_click.addCallback(callback)
    bw.web_page.page_finished_deferred.append(post_click)
    anchor.evaluateJavaScript('this.click()')
    return post_click


def do_login():    
    d = bw.xmlrpc_goto_url('http://opentable.com')
    d.addCallback(click_sign_in, populate_login_and_enter)
    return d

def do_registration():    
    d = bw.xmlrpc_goto_url('http://opentable.com')
    d.addCallback(click_sign_in, click_create_account)
    return d
    
if __name__ == '__main__':
    reactor.callWhenRunning(do_login)
    reactor.run()