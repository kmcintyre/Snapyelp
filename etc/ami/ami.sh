echo "[Credentials]" > .boto
echo "aws_access_key_id = <key> " >> .boto
echo "aws_secret_access_key = <pass>" >> .boto

sudo apt-get update

sudo apt-get -y install alsa-base ant gcc git glances imagemagick libfreetype6-dev libgles2-mesa-dev libjpeg-dev libmagickwand-dev libnss3 libgl1-mesa-dev libssl-dev libx11-dev libx11-xcb-dev libxcb-glx0-dev libxcb1-dev libxext-dev libxfixes-dev libxi-dev libxrender-dev libxslt1-dev monit nginx python-dev python-lxml python-opencv python-pip python-setuptools unzip xvfb 

sudo pip install --upgrade pip
sudo pip install --upgrade autobahn boto cssselect lxml Pillow pyopenssl requests service_identity simplejson Twisted Wand psutil

curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
sudo apt-get install -y nodejs 

sudo npm install -g bower
sudo npm install -g polymer-cli

git clone https://github.com/kmcintyre/Snapyelp -b demo

cd Snapyelp
git config credential.helper 'store'

sudo cp etc/systemd/xvfb.service /etc/systemd/system
sudo cp etc/systemd/swap.service /etc/systemd/system
sudo cp etc/systemd/identify.service /etc/systemd/system
	
cd /etc/systemd/system/

sudo systemctl enable xvfb
sudo systemctl enable swap
sudo systemctl enable identify

sudo systemctl start xvfb
sudo systemctl start swap

cd

wget http://download.qt.io/official_releases/qt/5.11/5.11.0/qt-opensource-linux-x64-5.11.0.run

chmod +x qt-opensource-linux-x64-5.11.0.run
export DISPLAY=:2
./qt-opensource-linux-x64-5.11.0.run --script ~/Snapyelp/etc/ami/qt.install.js

wget https://www.riverbankcomputing.com/static/Downloads/sip/sip-4.19.4.dev1710092233.tar.gz
gzip -df sip-4.19.4.dev1710092233.tar.gz
tar -xvf sip-4.19.4.dev1710092233.tar
rm *.tar
cd sip-4.19.4.dev1710092233
python configure.py
make
sudo make install
cd ..

wget https://www.riverbankcomputing.com/static/Downloads/PyQt5/PyQt5_gpl-5.9.1.dev1710071532.tar.gz
gzip -df PyQt5_gpl-5.9.1.dev1710071532.tar.gz
tar -xvf PyQt5_gpl-5.9.1.dev1710071532.tar
rm PyQt5_gpl-5.9.1.dev1710071532.tar 
cd PyQt5_gpl-5.9.1.dev1710071532
python configure.py --qmake=/home/ubuntu/Qt/5.7/gcc_64/bin/qmake 
make
sudo make install
cd ..