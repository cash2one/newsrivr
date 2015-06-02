mkdir -p ./dbs/config1
mkdir -p ./dbs/config2
mkdir -p ./dbs/config3

mongod --fork --dbpath /Users/rabshakeh/workspace/river/cluster/dbs/config1/ --port 20001 --logpath /Users/rabshakeh/Desktop/mds1.log
mongod --fork --dbpath /Users/rabshakeh/workspace/river/cluster/dbs/config2/ --port 20002 --logpath /Users/rabshakeh/Desktop/mds2.log
mongod --fork --dbpath /Users/rabshakeh/workspace/river/cluster/dbs/config3/ --port 20003 --logpath /Users/rabshakeh/Desktop/mds3.log