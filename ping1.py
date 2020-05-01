import urllib, os
# This script is used for pinging the client 2 and 3 from 1
os.system("ping -c 5 10.0.0.2 | tail -1| awk '{print $4}' | cut -d '/' -f 2 >> ping_stat_1_2")
os.system("ping -c 5 10.0.0.3 | tail -1| awk '{print $4}' | cut -d '/' -f 2 >> ping_stat_1_3")