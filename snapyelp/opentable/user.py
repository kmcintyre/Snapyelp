'''
Created on Oct 12, 2014

@author: kevin

User module mapping login and register functions in opentable 
'''


from snapyelp.qt import browser
print browser.version 

from snapyelp.qt.base import BaseWindow
from snapyelp.aws import dynamo
from snapyelp import fixed

opentable = dynamo.OpenTable()

domain = 'snapyelp.com'
lastname = 'Snapyelp'

from twisted.internet import reactor, defer

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
    

from boto.dynamodb2.exceptions import ItemNotFound

def login_done(res, window):
    if res:
        defer.succeed(window)
    else:
        return defer.fail("populate_login_and_enter")

def register_done(res, city, cityname, cityemail, citypassword, window):
    if res:
        print 'register_done:', res, city, cityname, cityemail
        opentable.furnish({'city': city, 'cityname': cityname, 'cityemail':cityemail, 'citypassword' : citypassword})        
        return defer.succeed("registered")
    else:
        return defer.fail("populate_account")

def populate_account(res, window):
    if res:
        for cf in window.web_page.mainFrame().childFrames():
            fn = cf.documentElement().findFirst('input[id="ucName_txtFirstName"]')
            if fn.hasAttributes():            
                for i, opt in enumerate(cf.documentElement().findAll('select[id="cboCity"] option').toList()[1:]):
                    city = fixed.simplify_to_id(opt.toInnerXml()).encode('ascii',errors='replace')
                    select_value = opt.attribute('value')
                    try:
                        print 'check city:', city
                        item = opentable.get_item(city=city)
                        print 'item:', item
                        if 'city_id' not in item:
                            print 'need to add city_id', select_value
                        else:
                            print item                            
                    except ItemNotFound as e:
                        print 'register city:'
                        
                        fn.evaluateJavaScript('this.focus()')                        
                        cityname = city.split('_')[0]                        
                        cityemail = cityname + '@' + domain
                        citypassword = 'snapper1!'
                                                
                        QTest.keyClicks(window.web_page.view(), cityname.title() , Qt.NoModifier, 20)
                        cf.documentElement().findFirst('input[id="ucName_txtLastName"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(window.web_page.view(), lastname, Qt.NoModifier, 20)
                        cf.documentElement().findFirst('input[id="txtEmail"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(window.web_page.view(), cityemail, Qt.NoModifier, 20)            
                        cf.documentElement().findFirst('input[id="txtPassword"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(window.web_page.view(), citypassword, Qt.NoModifier, 20)            
                        cf.documentElement().findFirst('input[id="txtReEnterPassword"]').evaluateJavaScript('this.focus()')
                        QTest.keyClicks(window.web_page.view(), citypassword , Qt.NoModifier, 20)                                            
                        opt.evaluateJavaScript('this.parentNode.selectedIndex = ' + str(i+1) + ';')
                        cf.documentElement().findFirst('input[id="chkIsAdmin"]').evaluateJavaScript('this.click()')

                        cf.documentElement().findFirst('a[id="btnRegister"] span').evaluateJavaScript('this.click()')                        
                        post_click = defer.Deferred()
                        window.web_page.page_finished_deferred.append(post_click)
                        post_click.addCallback(register_done, city, cityname, cityemail, citypassword, window)                        
                        return post_click 
                    except Exception as e:
                        print 'populate account exception:', e
    else:
        return defer.fail("click_create_account")
            

def click_create_account(res, window):
    if res:
        post_click = defer.Deferred()
        window.web_page.page_finished_deferred.append(post_click)    
        for cf in window.web_page.mainFrame().childFrames():
            anchor = cf.documentElement().findFirst('a[id="lnkNotMemberReg"]') 
            if anchor.hasAttributes():
                post_click.addCallback(populate_account, window)
                anchor.evaluateJavaScript('this.click()')
        return post_click
    else:
        return defer.fail('click_sign_in')


def populate_login_and_enter(res, window):
    print 'populate_login'
    if res:
        for cf in window.web_page.mainFrame().childFrames():
            input_email = cf.documentElement().findFirst('input[id="txtUserEmail"]')
            if input_email.hasAttributes():
                input_email.evaluateJavaScript('this.focus()')
                QTest.keyClicks(window.web_page.view(), 'kevin70@yahoo.com', Qt.NoModifier, 20)
                cf.documentElement().findFirst('input[id="txtUserPassword"]').evaluateJavaScript('this.focus()')
                QTest.keyClicks(window.web_page.view(), 'tererdfcvO1', Qt.NoModifier, 20)
                cf.documentElement().findFirst('span[id="lblMember"]').evaluateJavaScript('this.focus()')
                post_click = defer.Deferred()
                post_click.addCallback(login_done, window)
                window.web_page.page_finished_deferred.append(post_click)                
                QTest.keyClick(window.web_page.view(), Qt.Key_Enter, Qt.NoModifier, 250)
                return post_click
    else:
        defer.fail("click_sign_in")
    
def click_sign_in(ans, callback, window):
    print 'click sign in', callback, window
    anchor = window.web_page.mainFrame().documentElement().findFirst('a[id="global_nav_sign_in"]')
    post_click = defer.Deferred()
    post_click.addCallback(callback, window)
    window.web_page.page_finished_deferred.append(post_click)
    anchor.evaluateJavaScript('this.click()')
    return post_click


def create_window():
    bw = BaseWindow()
    bw.show()
    return bw

def do_login(city, bw):    
    d = bw.xmlrpc_goto_url('http://opentable.com')
    d.addCallback(click_sign_in, populate_login_and_enter)
    return d

def do_registration(bw):
    d = bw.xmlrpc_goto_url('http://opentable.com')
    d.addCallback(click_sign_in, click_create_account, bw)
    d.addCallback(lambda ign: create_window())
    d.addCallback(do_registration)
    return d
    
if __name__ == '__main__':

    reactor.callWhenRunning(do_registration, create_window())
    reactor.run()