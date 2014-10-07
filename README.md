snapyelp
========

### Scope

This project intent is the initial bunble for instagator.com

### Stack

python twisted project utilizing qthread and pyqt to coordinate bookings within opentable.com system.

* twisted 14.0.2
* python 2.7
* pyqt 5.3.2

### Design

The back-end service is a websocket accepting json encoded messages format TBD.  Further endpoints i.e. restful will be required.

### Assumptions

* service is not scrape but rather stateful browser operating as booking agent
* booking agent exposes commands that can be reduced to a series of page visits and form submissions
* booking agent is a unique email endpoint
* booking agent 

### Phase

* Worst first.
* Random button reservation, with delayed cancellation.

### Folders

* etc/ami/ami.sh #install procedure for build-out from latest/greatest ubuntu
* etc/init/ # upstart configs
* html # static-content for thin client demo client
* snapyelp # source

### AMI provisioning 
