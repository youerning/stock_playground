#!/bin/bash

# 记录用到的命令

# start elk env
# echo "vm.max_map_count=655360" >> tail /etc/sysctl.conf
# ulimit -n 65535
docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -v /home/elasticsearch/:/var/lib/elasticsearch -itd  sebp/elk
