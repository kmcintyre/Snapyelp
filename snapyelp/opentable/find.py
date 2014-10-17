'''
Created on Oct 12, 2014

@author: kevin

User module mapping login and register functions in opentable 
'''
from snapyelp.opentable import user

from snapyelp import fixed
from snapyelp.qt import browser_video

from twisted.internet import reactor, defer
    
import random

def toggle_by_restuarant(window):
    print 'nextstep'
    window.web_page.mainFrame().documentElement().findFirst('span[id="SearchNav_lblTabText_RestaurantName"]').evaluateJavaScript('this.click()')
    return window        

def select_date(window):
    print window.web_page.mainFrame().documentElement().findFirst('input[id="DatePickerControlDateEdit DatePickerControlDateEdit"]').toPlainText()
    #<input class="DatePickerControlDateEdit DatePickerControlDateEdit" data-container-selector=".FieldContainer" data-date-format="MM/DD/YYYY" value="10/16/2014" id="SearchNav_OTSimpleSearch_OTDateSearch_theOTDate" name="SearchNav$OTSimpleSearch$OTDateSearch$theOTDate">
    
    
def findresult(res, window):
    print 'findresult'
    if res:
        print 'fuck yeah'
        return window
    else:
        defer.fail()

def clickfind(res, window):
    print 'clickfind'
    if res:
        select_date(window)
        
        find_deferred = defer.Deferred()
        find_deferred.addCallback(findresult, window)        
        window.web_page.page_finished_deferred.append(find_deferred)
        window.web_page.mainFrame().documentElement().findFirst('input[id="SearchNav_btnFindTable"]').evaluateJavaScript('this.click()')
        return find_deferred
    else:
        defer.fail()
def pick_city(res,window,city=None):
    if res:
        city_anchors = []
        for c in window.web_page.mainFrame().documentElement().findAll('div[class="hidden"][data-ot-roll-over-link-dropdown] a'): 
            if 'See other' not in c.toPlainText().strip():
                city_anchors.append(c)                
        random_city = random.choice(city_anchors)
        print random_city.attribute('href')
        d = window.xmlrpc_goto_url(random_city.attribute('href'))
        d.addCallback(clickfind, window)
        return d
    else:
        return defer.fail()

def do_find(bw):
    browser_video.app.isReady()
    d = bw.xmlrpc_goto_url('http://opentable.com')
    d.addCallback(pick_city,bw)
    return d
    
if __name__ == '__main__':

    reactor.callWhenRunning(do_find, user.create_window())
    reactor.run()