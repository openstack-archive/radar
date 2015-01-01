Radar Third Party CI Dashboard for OpenStack
=====================

* Radar API Installation
  * apt-get install libpq-dev libmysqlclient-dev
  * apt-get install mysql-server
  * apt-get install rabbitmq-server
  * pip install --upgrade -r requirements.txt
  * python setup.py build
  * python setup.py install

* Nodejs setup
  * curl -sL https://deb.nodesource.com/setup | sudo bash -
  * apt-get install -y nodejs
  * npm install -g grunt-cli
  * npm install -g bower
  * npm install
  * bower install
  * grunt
  
* Database
  * CREATE user 'radar'@'localhost' IDENTIFIED BY 'radar'; 
  * GRANT ALL PRIVILEGES ON radar.* to 'radar'@'localhost'; 
  * FLUSH PRIVILEGES;
  * radar-db-manage upgrade head
  
* To run the:
  * API
    * radar-api
  
  * Update Daemon
    * radar-update-daemon
