./checkall.sh
scp *.py *.rb *.sh leah.active8.nl:./Newsrivr/daemons &
scp *.py *.rb *.sh hannah.active8.nl:./Newsrivr/daemons 
ssh root@hannah.active8.nl reboot
scp *.py *.rb *.sh rachel.active8.nl:./Newsrivr/daemons 
ssh root@rachel.active8.nl reboot
scp *.py *.rb *.sh 173.255.251.211:./Newsrivr/daemons 
ssh root@amzi.active8.nl reboot
