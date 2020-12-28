wget https://raw.githubusercontent.com/magemojo/zlog/master/zlog.py;python3 ./zlog.py

Updated 12-28-2020 Added new options

    -n, --newfile  allows you to examine log file besides the default
    -w, --whois    checks whois by IPs for common traffic sources
    -a, --attacks  checks for common attacks/scans
    
Updated 5-18-2020 Added Top 10 URLs hit & Top 10 User Agents

AHK
::;zlog::
SendRaw, wget https://raw.githubusercontent.com/magemojo/zlog/master/zlog.py;python3 ./zlog.py
Exit
