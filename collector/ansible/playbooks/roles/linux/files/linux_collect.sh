#!/bin/bash

data_file=/tmp/collect_result.tmp
rm -rf /tmp/collect_result.tmp

##disk
df -hP -B 1G | awk 'NR>1{print $4,100-$5,$NF}' | while read -r line ; do
     available_value=$(echo "${line}"| awk '{print $1}')
     available_percent=$(echo "${line}"| awk '{print $2}')
     file_partition=$(echo "${line}"|awk '{print $3}')
     echo "${file_partition}_size_free:${available_value}" >> ${data_file}
     echo "${file_partition}_percent:${available_percent}" >> ${data_file}
done

## mem
mem_total=$(free -g|sed -n '2p' | awk '{printf $2}')
echo "mem_total:${mem_total}" >> ${data_file}

## CPU
load15=$(uptime | awk '{printf $NF}'|sed 's/,//g')
echo "cpu_load15:${load15}" >> ${data_file}


