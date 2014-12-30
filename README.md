Radar Third Party CI Dashboard for OpenStack
=====================

* Application Installation
  * apt-get install libpq-dev libmysqlclient-dev
  * apt-get install mysql-server
  * apt-get install rabbitmq-server
  * pip install --upgrade -r requirements.txt
  * python setup.py build
  * python setup.py install
  
* Database
  * CREATE user 'radar'@'localhost' IDENTIFIED BY 'radar'; 
  * GRANT ALL PRIVILEGES ON radar.* to 'radar'@'localhost'; 
  * FLUSH PRIVILEGES;
  * radar-db-manage upgrade head
  
* API
  * radar-api
  
* Update Daemon
  * radar-update-daemon