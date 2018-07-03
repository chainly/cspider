# https://splash.readthedocs.io/en/stable/install.html#ubuntu-16-04-manual-way
# from this doc, still in error! just try apt install !
#cd 
#sudo apt-get update  
#sudo apt-get install \
    #apt-transport-https \
    #ca-certificates \
    #curl \
    #software-properties-common -y

#sudo add-apt-repository ppa:git-core/ppa  -y

#sudo apt-get install git python-setuptools  python3-setuptools python-pip python3-pip python-dev -y

#curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#python get-pip.py

#git clone https://github.com/scrapinghub/splash/
#cd splash/dockerfiles/splash

#sudo cp ./qt-installer-noninteractive.qs /tmp/script.qs
## shell self
#apt-add-repository -y "deb http://archive.ubuntu.com/ubuntu xenial multiverse"

#apt-add-repository -y "deb http://archive.ubuntu.com/ubuntu xenial-updates multiverse"
## https://blog.csdn.net/pipisorry/article/details/37730443
#sudo apt-get install -y qt5-qmake 
## https://stackoverflow.com/questions/16607003/qmake-could-not-find-a-qt-installation-of
#apt-get install qt5-default -y

## https://www.e-learn.cn/content/wangluowenzhang/127010
#export QT_SELECT=qt5

#sudo ./provision.sh \
           #prepare_install \
           #install_msfonts \
           #install_extra_fonts \
           #install_deps \
           #install_flash \
           #install_qtwebkit_deps \
           #install_official_qt \
           #install_qtwebkit \
           #install_pyqt5 \
           #install_python_deps

cd 
sudo apt-get update  
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common -y

sudo add-apt-repository ppa:git-core/ppa  -y
sudo apt-get install git python-setuptools  python3-setuptools python-pip python3-pip python-dev -y
# https://stackoverflow.com/questions/2922711/importerror-no-module-named-qtwebkit
# https://askubuntu.com/questions/930998/how-to-install-pyqt5-in-xubuntu-16-04
sudo apt install python3-pyqt5 python3-pyqt5.qtwebkit xvfb openssl libssl-dev -y
pip3 install splash

# https://stackoverflow.com/questions/41408791/python-3-unicodeencodeerror-ascii-codec-cant-encode-characters
# https://help.ubuntu.com/community/Locale
locale charmap |grep -v 'UTF-8' && update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 && sudo locale-gen  # && echo  'logout && login' && exit 1
#root@vpn:~# update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 
#*** update-locale: Error: invalid locale settings:  LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8
# encode all output
nohup python3 -m splash.server --port=8050 2>&1 >> splash.log &

git clone https://github.com/chainly/cspider.git
cd cspider
pip3 install -r  requirement.txt

nohup python3 manage.py runserver 0.0.0.0:80 >> django.log &

# crontab
#cd /root/cspider/fspider && scrapy crawl test2
#scrapy crawl test2