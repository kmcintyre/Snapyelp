'''
Created on Oct 12, 2014

@author: kevin

User module mapping login and register functions in opentable 
'''
from snapyelp.opentable import user


from twisted.internet import reactor, defer
    
import datetime
import random

#def cancel_result(res, window):
#    print 'cancel_result:', res, window
#    return (rn,ri,dn)
    #return window
    
    #if res:
    #    print 'auto cancel done:', window
    #    reactor.stop()
    #else:
    #    defer.fail()
    

def cancel_reservation(res, window):
    print 'cancel_reservation', res, window
    if res:
        #window.web_page.mainFrame().documentElement().findFirst('a[id="cancelAction"]').evaluateJavaScript('this.click()')                
        rn = window.web_page.mainFrame().documentElement().findFirst('li[id="restaurantName"]').toInnerXml()
        print 'restuarant name:', rn
        ri = window.web_page.mainFrame().documentElement().findFirst('li[id="reservationInfo"] span').toInnerXml()
        print 'restuarant info:', ri
        dn = window.web_page.mainFrame().documentElement().findFirst('li[id="dinerName"]').toPlainText().split(":")[1]
        print 'dinner name:', dn
        return (rn,ri,dn)
    else:
        print 'cancel_reservation fail'
        reactor.stop()        


def reservation_result(res, window):
    print 'reservation_result', res
    if res:
        cancel_anchor = window.web_page.mainFrame().documentElement().findFirst('a[id="linkCancelReservation"]')        
        print 'CANCELING!:', cancel_anchor.attribute('href')
        click_cancel = defer.Deferred()
        click_cancel.addCallback(cancel_reservation, window)
        window.web_page.page_finished_deferred.append(click_cancel)
        cancel_anchor.evaluateJavaScript('this.click()')
        return click_cancel
    else:
        print 'reservation_result fail'
        reactor.stop()        

        
def populate_reservation(res, window):
    print 'populate_reservation result', res
    if res:
        window.web_page.mainFrame().documentElement().findFirst('input[id="radFirstTimeDiningYes"]').evaluateJavaScript('this.click()')
        window.web_page.mainFrame().documentElement().findFirst('input[id="PhoneEntry1_txtPhone1"]').evaluateJavaScript('this.value="212 754-9494"')
        
        click_reservation = defer.Deferred()
        click_reservation.addCallback(reservation_result, window)
        window.web_page.page_finished_deferred.append(click_reservation)
        window.web_page.mainFrame().documentElement().findFirst('input[id="btnContinueReservation"]').evaluateJavaScript('this.click()')                
        return click_reservation 
    else:
        print 'populate_reservation fail'
        reactor.stop()        

def find_result(res, window):
    print 'find_result:', res, window
    if res:
        found_available = False
        reservation_table = window.web_page.mainFrame().documentElement().findFirst('table[id="search_results_table"]')
        for tr in reservation_table.findAll('tr').toList()[1:]:
            rn = tr.findFirst('td[class="cell first-cell"] div[class="rest-content"] a').toPlainText()
            rb = tr.findFirst('td[class="cell last-cell availability-col"] div[class="timeslots cf"] li[class="timeslot exact"] a')
            if not rb.isNull() and not found_available:
                print 'tr:', rn, rb.attribute('href')
                found_available = True
                d = window.xmlrpc_goto_url('http://www.opentable.com' + rb.attribute('href'))
                d.addCallback(populate_reservation, window)
                return d
        #return window
    else:
        print 'find_result fail'
        reactor.stop()        


def interim_result(res, window):
    print 'interim_result', res
    if res:
        find_deferred = defer.Deferred()
        find_deferred.addCallback(find_result, window)        
        window.web_page.page_finished_deferred.append(find_deferred)
        return find_deferred
    else:
        print 'interim_result fail'
        reactor.stop()

def toggle_by_restuarant(window):
    print 'toggle_by_restuarant'
    window.web_page.mainFrame().documentElement().findFirst('span[id="SearchNav_lblTabText_RestaurantName"]').evaluateJavaScript('this.click()')
    return window        

#[id="SearchNav$OTSimpleSearch$OTDateSearch$theOTDate"]
#
def select_date(window, dt = None):
    print 'select_date', window
    for inp in window.web_page.mainFrame().documentElement().findAll('input'):
        print 'se:', inp.toOuterXml()
    
    #se = window.web_page.mainFrame().documentElement().find('input[id="SearchNav$OTSimpleSearch$OTDateSearch$theOTDate"]')
    #print 'se:', se.toOuterXml()
    #if dt is None:        
    #    dt = datetime.datetime.strptime(se.attribute('value'), "%m/%d/%Y")  + datetime.timedelta(days=7)
    #se.evaluateJavaScript('this.value="' + datetime.datetime.strftime(dt, "%m/%d/%Y") + '"') 
    #<input class="DatePickerControlDateEdit DatePickerControlDateEdit" data-container-selector=".FieldContainer" data-date-format="MM/DD/YYYY" value="10/16/2014" id="SearchNav_OTSimpleSearch_OTDateSearch_theOTDate" name="SearchNav$OTSimpleSearch$OTDateSearch$theOTDate">

def select_time(window, st = None):
    print 'select_time', window
    te = window.web_page.mainFrame().documentElement().findFirst('select[name="SearchNav$OTSimpleSearch$OTDateSearch$cboHourList"]')
    if st is None:
        st = '8:00 PM'
    for opt in te.findAll('option').toList():
        if st == opt.attribute('value'):
            opt.evaluateJavaScript('this.selected=true')

def click_find(res, window):
    print 'click_find', window
    if res:
        select_date(window)
        select_time(window)     
        interim_deferred = defer.Deferred()
        interim_deferred.addCallback(interim_result, window)        
        window.web_page.page_finished_deferred.append(interim_deferred)
        window.web_page.mainFrame().documentElement().findFirst('input[id="SearchNav_btnFindTable"]').evaluateJavaScript('this.click()')
        return interim_deferred
    else:
        print 'click_find fail'
        reactor.stop()

def pick_city(res,window,city=None):
    if res:
        city_anchors = []
        for c in window.web_page.mainFrame().documentElement().findAll('div[class="hidden"][data-ot-roll-over-link-dropdown] a'): 
            if 'See other' not in c.toPlainText().strip():
                city_anchors.append(c)                
        random_city = random.choice(city_anchors)
        print 'random city:', random_city.attribute('href')
        #pick_deferred = defer.Deferred()
        #window.web_page.page_finished_deferred.append(pick_deferred)
        #pick_deferred.addCallback()    
        #random_city.evaluateJavaScript('this.click()')                
        #return pick_deferred
        d = window.xmlrpc_goto_url('http://www.google.com')
        d.addCallback(lambda ign: window.xmlrpc_goto_url( random_city.attribute('href') ) )
        d.addCallback(click_find, window)
        return d
    else:
        print 'pick_city fail'
        reactor.stop()

def do_find(bw):
    if bw.web_page.view().url().toString() != 'http://www.opentable.com/start/home':
        d = bw.xmlrpc_goto_url('http://www.opentable.com/start/home')
        d.addCallback(pick_city,bw)
        return d
    else:
        print 'already there'
        return pick_city(True,bw) 
    
if __name__ == '__main__':

    reactor.callWhenRunning(do_find, user.create_window())
    reactor.run()
