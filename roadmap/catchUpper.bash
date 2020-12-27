#/!bin/bash
cd /home/pims/roadmap
/home/pims/roadmap/processRoadmap.py logLevel=3 repairYear=${1} mode=repair repairModTime=1

tail -1 /tmp/status309.txt | sed -e 's/KH done/so far done/' | sed -e 's/est done at/estimate totally done at GMT/'; echo ' ' > /misc/yoda/www/plots/user/mike/status309.txt
