snapyelp
========

## Scope

This project intent is the initial bundle

## Stack

python twisted project utilizing qthread and pyqt to coordinate bookings within opentable.com system.

* twisted 14.0.2
* python 2.7
* pyqt 5.3.2
* boto AWS library for python

## Folder Structure

* build - scripts necessary to push demo client to cloudfront
* etc/ami - script for building instance
* etc/init - upstart scripts
* etc/templates - templates for publishing within twisted
* snapyelp - source code

## Design

The back-end service is a websocket accepting json encoded messages format TBD.  Further endpoints - rest may be required.


## Phase

* Worst first, but still non-pollutive to opentable environment.

The goal is to demo to the team a 1-button reservation generator.  

Provided via a series of automated steps via a browser on the back-end.  In opentable system a user booking a table must 1) be logged in 2) select an metro area or "mn" parameter before conducting a "find" and "reserve".  At a minimum the service must be able to perform those tasks as a series.  The end-product being a opentable reservation id.

#### Assumptions

* service is not scrape but rather stateful browser operating as booking agent
* service exposes commands as reduced to a series of page visits and form submissions
* service is a unique email endpoint registered as a booking agent with opentable system
