snapyelp
========

Latest greatest - demonstration of AWS CICD with a tunable funnel performance test  

## Stack

* [boto](https://github.com/boto/boto)
* [pyqt](https://riverbankcomputing.com/software/pyqt/intro)
* [Twisted](https://twistedmatrix.com/trac/)
* [Polymer](https://www.polymer-project.org/)

See [AMI script](repo/blob/master/etc/ami.sh) for additional libraries 

## Folder Structure

* etc/ami - script for building instance
* etc/systemd - upstart scripts
* etc/bin - utility scripts
* snapyelp - python source code
* src - html code

## Roles

* [website](http://snapyelp.com) - published assets via [Cloudfront](https://aws.amazon.com/cloudfront/)
* [service](http://service.snapyelp.com) - choreographs tests 
* agent - test running 

## Install

* ./etc/ami/ami.sh (create AMI for distribution)