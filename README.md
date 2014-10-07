snapyelp
========

## Scope

This project intent is the initial bundle for instagator.com

## Stack

python twisted project utilizing qthread and pyqt to coordinate bookings within opentable.com system.

* twisted 14.0.2
* python 2.7
* pyqt 5.3.2

## Design

The back-end service is a websocket accepting json encoded messages format TBD.  Further endpoints i.e. restful will be required.

## Phase

* Worst first, but still non-pollutive to opentable environment.

The goal is to demo to the team a 1-button reservation generator, with cancel by hand.

#### Assumptions

* service is not scrape but rather stateful browser operating as booking agent
* service exposes commands as reduced to a series of page visits and form submissions
* service is a unique email endpoint registered as a booking agent with opentable system

#### Folder Structure

* etc # upstart configs, and install scripts
* html # static-content for thin client demo client
* snapyelp # source

