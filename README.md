wget https://raw.githubusercontent.com/magemojo/zlog/master/zlog.py; python3 ./zlog.py

Updated 7-2-2021 2.3

    -m, --min allows you to examine specified amount of minutes previous to now. Works in combo with options for nginx (not phpfpm --cpu)
    Examples:
    python3 ./zlog.py --min 15
    python3 ./zlog.py --newfile --min 5
    python3 ./zlog.py --whois --min 60
    python3 ./zlog.py --attacks --min 120


Updated 4-22-2021 2.2

    Added paypal carding detection & catalogsearch hits to --attacks

Updated 2-23-2021 CPU usage 2.1

    -c, --cpu  allows you to examine high CPU usage in PHP-FPM logs

Updated 12-28-2020 Added new options 2.0

    -n, --newfile  allows you to examine log file besides the default
    -w, --whois    checks whois by IPs for common traffic sources
    -a, --attacks  checks for common attacks/scans
    
Updated 5-18-2020 Added Top 10 URLs hit & Top 10 User Agents 1.3

AHK
::;zlog::
SendRaw, wget https://raw.githubusercontent.com/magemojo/zlog/master/zlog.py; python3 ./zlog.py
Exit
