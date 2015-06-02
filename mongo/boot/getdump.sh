rm -Rf dump*
scp rabshakeh@leah.active8.nl:./dump.tar.gz .
gzip -d dump.tar.gz
tar -xvf dump.tar
gzip dump.tar
