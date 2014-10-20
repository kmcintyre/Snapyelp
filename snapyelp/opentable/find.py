'''
Created on Oct 12, 2014

@author: kevin

User module mapping login and register functions in opentable 
'''
from snapyelp.opentable import user

from twisted.internet import reactor, defer
    
import datetime
import random

def cancel_result(res, window):
    print 'cancel_result:', res
    if res:
        print 'auto cancel done:', window
        reactor.stop()
    else:
        defer.fail()
    

def cancel_reservation(res, window):
    print 'cancel_reservation result', res
    if res:
        print 'auto cancel'
        do_cancel = defer.Deferred()
        do_cancel.addCallback(cancel_result, window)
        window.web_page.page_finished_deferred.append(do_cancel)
        window.web_page.mainFrame().documentElement().findFirst('a[id="cancelAction"]').evaluateJavaScript('this.click()')        
    else:
        defer.fail()

def reservation_result(res, window):
    print 'reservation_result result', res
    if res:
        cancel_anchor = window.web_page.mainFrame().documentElement().findFirst('a[id="linkCancelReservation"]')        
        print cancel_anchor.attribute('href')
        click_cancel = defer.Deferred()
        click_cancel.addCallback(cancel_reservation, window)
        window.web_page.page_finished_deferred.append(click_cancel)
        cancel_anchor.evaluateJavaScript('this.click()')
    else:
        defer.fail()
        
def populate_reservation(res, window):
    print 'populate_reservation result', res
    if res:
        window.web_page.mainFrame().documentElement().findFirst('input[id="radFirstTimeDiningYes"]').evaluateJavaScript('this.click()')
        window.web_page.mainFrame().documentElement().findFirst('input[id="PhoneEntry1_txtPhone1"]').evaluateJavaScript('this.value="718 249 5058"')
        
        click_reservation = defer.Deferred()
        click_reservation.addCallback(reservation_result, window)
        window.web_page.page_finished_deferred.append(click_reservation)
        window.web_page.mainFrame().documentElement().findFirst('input[id="btnContinueReservation"]').evaluateJavaScript('this.click()')                
        
    else:
        defer.fail()

def populate_signin(res, window):
    print 'populate_signin result', res
    if res:
        active_user = user.opentable_db.get_active()
        print 'active_user:', active_user
        email = window.web_page.mainFrame().documentElement().findFirst('input[id="txtUserEmail"]')
        email.evaluateJavaScript('this.value="' + active_user['cityemail'] + '"')
        password = window.web_page.mainFrame().documentElement().findFirst('input[id="txtUserPassword"]')
        password.evaluateJavaScript('this.value="' + active_user['citypassword'] + '"')
        anchor = window.web_page.mainFrame().documentElement().findFirst('span[id="lblMember"]').parent()

        signin_click = defer.Deferred()
        signin_click.addCallback(populate_reservation, window)
        window.web_page.page_finished_deferred.append(signin_click)
        anchor.evaluateJavaScript('this.click()')
                
    else:
        defer.fail()

def signin(res, window):
    print 'signin result', res
    if res:
        click_signin = defer.Deferred()
        click_signin.addCallback(populate_signin, window)        
        window.web_page.page_finished_deferred.append(click_signin)        
        anchor = window.web_page.mainFrame().documentElement().findFirst('a[id="linkSignIn"]')
        print 'anchor:', anchor, anchor.isNull()
        anchor.evaluateJavaScript('this.click()')
        #return window
    else:
        defer.fail()

def find_result(res, window):
    print 'find_result result', res
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
                d.addCallback(signin, window)
        #return window
    else:
        defer.fail()


def interim(res, window):
    print 'interim result', res
    if res:
        find_deferred = defer.Deferred()
        find_deferred.addCallback(find_result, window)        
        window.web_page.page_finished_deferred.append(find_deferred)
        return find_deferred
    else:
        defer.fail()

def toggle_by_restuarant(window):
    print 'nextstep'
    window.web_page.mainFrame().documentElement().findFirst('span[id="SearchNav_lblTabText_RestaurantName"]').evaluateJavaScript('this.click()')
    return window        

def select_date(window, dt = None):
    print 'select date'
    se = window.web_page.mainFrame().documentElement().findFirst('input[name="SearchNav$OTSimpleSearch$OTDateSearch$theOTDate"]')
    if dt is None:
        dt = datetime.datetime.strptime(se.attribute('value'), "%m/%d/%Y")  + datetime.timedelta(days=7)
    se.evaluateJavaScript('this.value="' + datetime.datetime.strftime(dt, "%m/%d/%Y") + '"') 
    #<input class="DatePickerControlDateEdit DatePickerControlDateEdit" data-container-selector=".FieldContainer" data-date-format="MM/DD/YYYY" value="10/16/2014" id="SearchNav_OTSimpleSearch_OTDateSearch_theOTDate" name="SearchNav$OTSimpleSearch$OTDateSearch$theOTDate">

def select_time(window, st = None):
    print 'select date'
    te = window.web_page.mainFrame().documentElement().findFirst('select[name="SearchNav$OTSimpleSearch$OTDateSearch$cboHourList"]')
    if st is None:
        st = '8:00 PM'
    for opt in te.findAll('option').toList():
        if st == opt.attribute('value'):
            opt.evaluateJavaScript('this.selected=true')

def clickfind(res, window):
    print 'clickfind'
    if res:
        select_date(window)
        select_time(window)     
        interim_deferred = defer.Deferred()
        interim_deferred.addCallback(interim, window)        
        window.web_page.page_finished_deferred.append(interim_deferred)
        window.web_page.mainFrame().documentElement().findFirst('input[id="SearchNav_btnFindTable"]').evaluateJavaScript('this.click()')
        return interim_deferred
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
    d = bw.xmlrpc_goto_url('http://opentable.com')
    d.addCallback(pick_city,bw)
    return d
    
if __name__ == '__main__':

    reactor.callWhenRunning(do_find, user.create_window())
    reactor.run()