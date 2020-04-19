import urllib, os
# This script is used for pinging the client 1 and 3 from 2
os.system("ping -c 5 10.0.0.1 | tail -1| awk '{print $4}' | cut -d '/' -f 2 >> ping_stat_2_1")
os.system("ping -c 5 10.0.0.3 | tail -1| awk '{print $4}' | cut -d '/' -f 2 >> ping_stat_2_3")