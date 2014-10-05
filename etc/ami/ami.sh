# echo "[Credentials]" > .boto
# echo "aws_access_key_id = <key> " >> .boto
# echo "aws_secret_access_key = <pass>" >> .boto

sudo apt-get update
sudo apt-get -y install git python-setuptools python-lxml python-opencv libav-tools xvfb vnc4server openbox gcc g++ make python-dev qt5-default

sudo easy_install pip
sudo pip install service_identity
sudo pip install boto --upgrade
sudo pip install beautifulsoup4
sudo pip install pyvirtualdisplay
sudo easy_install autobahn


wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.3/sip-4.16.3.tar.gz
gzip -df sip-4.16.3.tar.gz
tar -xvf sip-4.16.3.tar

wget http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.3.2/PyQt-gpl-5.3.2.tar.gz
gzip -df PyQt-gpl-5.3.2.tar.gz
tar -xvf PyQt-gpl-5.3.2.tar

wget http://download.qt-project.org/official_releases/qt/5.3/5.3.2/qt-opensource-linux-x64-5.3.2.run
chmod +x qt-opensource-linux-x64-5.3.2.run

if [[ `twistd --version` =~ .*14.0.2* ]]
then
    echo 'Twisted installed'
else
    echo 'Install Twisted'
    sudo apt-get -y install gcc python-dev
	wget https://pypi.python.org/packages/source/T/Twisted/Twisted-14.0.2.tar.bz2
	bunzip2 Twisted-14.0.2.tar.bz2
	tar -xvf Twisted-14.0.2.tar
	
	cd Twisted-14.0.2
	sudo python setup.py install
	cd ..
	sudo rm -f Twisted-14.0.2.tar    
	sudo rm -rf Twisted-14.0.2 	
fi

git clone https://github.com/kmcintyre/snapyelp

#
# Next part is to get PyQt5.3.2 installed
#

vnc4server
#setup password
vnc4server -kill :1
screen
sudo cp snapyelp/etc/xvfb.conf /etc/init/
sudo start xvfb


#new screen
vi .vnc/xstartup
# comment out "x-window-manager &" 
# add new line:openbox-session &
export DISPLAY=:0
openbox-session &

# new screen
vnc4server # should start on 5901

# connect with RDC

export DISPLAY=:1
./qt-opensource-linux-x64-5.3.2.run


### You can kill vnc openbox

cd sip-4.16.3
python configure.py
make
sudo make install
cd ..

cd PyQt-gpl-5.3.2
python configure.py --qmake=/home/ubuntu/Qt5.3.2/5.3/gcc_64/bin/qmake
sudo ln -s /usr/include/python2.7 /usr/local/include/python2.7
make
sudo make install

python configure.py --qmake=/home/ubuntu/Qt5.3.2/5.3/gcc_64/bin/qmake -e QtWebKit
make
sudo make install
python configure.py --qmake=/home/ubuntu/Qt5.3.2/5.3/gcc_64/bin/qmake -e QtWebKitWidgets
make
sudo make install

sudo apt-get install gstreamer0.10