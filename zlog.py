#!/usr/bin/python
# 1.1
# Questions? Problems? Need more? ask Jackie

import os
import sys
import subprocess

# ASK 4 STUFFZ
print "1. STRATUS"
print "2. MHM"
wtype = raw_input("1 or 2? > ")
if wtype == '1':
   if os.path.exists("/log/access.log"):
      thepath = "/log/access.log"
      saveplace = "/srv/"
   else:
      print "Are you sure this is Stratus?"
      print "Can not find log at /log/access.log";
      sys.exit()
elif wtype == '2':
   print " "
   print "1. NGINX"
   print "2. APACHE"
   w80 = raw_input("1 or 2? > ")
   saveplace = "/home/log/"
   if w80 == '1':
      if os.path.exists("/home/log/nginx/access.log"):
         thepath = "/home/log/nginx/access.log"
         saveplace = "/srv/"
      else:
         print "Are you sure this is Nginx?"
         print "Can not find log at /home/log/nginx/access.log";
         sys.exit()
   elif w80 == '2':
      if os.path.exists("/home/log/httpd/access.log"):
         thepath = "/home/log/httpd/access.log"
      elif os.path.exists("/home/log/apache/access.log"):
         thepath = "/home/log/apache/access.log"
      else:
         print "Are you sure this is Apache?"
         print "Can not find apache log at /home/log/httpd/access.log or /home/log/apache/access.log";
         sys.exit()
   else:
      print "Unknown Option Selected!";
      sys.exit()
else:
   print "Unknown Option Selected!"
   sys.exit()

# GET TIME START OF LOG FILE
if wtype == '1':
   vhead = os.popen("head -n1 " + thepath  + " | awk -F ' ' '{print $3}'").read()
   vhead = vhead.replace('[', '').replace("\n", '')
else:
   vhead = os.popen("head -n1 " + thepath  + " | awk -F ',' '{print $1}'").read()
   vhead = vhead.replace('T', ' ').replace('"', '').replace("'", '').replace("{@timestamp:", '').replace("\n", '')

vhead = os.popen("head -n1 " + thepath  + " | awk -F ' ' '{print $3}'").read()
vhead = vhead.replace('T', ' ').replace('"', '').replace("'", '').replace("{@timestamp:", '').replace("\n", '')
print " "
print "Since " + vhead  + " GMT"
print " "
print "HITS / IP / AGENT"

# GET TOP 15 IPs
cmdget = "grep -E -o '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' " + thepath + " | sort -n | uniq -c | sort -n | tail -15 > " + saveplace  + "zIPs.log"
os.system(cmdget)

cmdip = "grep -E -o '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' " + saveplace  + "zIPs.log > " + saveplace + "zTemp.log"
os.system(cmdip)

# GET AGENT OF EACH IP
with open(saveplace + "zTemp.log") as f:
   for line in f:
       line = line.replace("\n", '')

       if wtype == '1':
          vagent = os.popen("grep -m1 " + line  + " " + thepath + " | awk -F ' ' '{print $11 $12 $13 $14 $15 $16 $17 $18 $19 $20}'").read()
       else:
          vagent = os.popen("grep -m1 " + line  + " " + thepath + " | awk -F ',' '{print $15}'").read()

       vagent = vagent.replace('"', '').replace("'", '').replace(";", '').replace("\n", '').replace("}", '').replace("webserver_http_user_agent:", '')
       vcount = os.popen("grep -m1 " + line  + " " + saveplace + "zIPs.log | awk -F ' ' '{print $1,$2}'").read()
       vcount=vcount.replace("\n", '')
       print vcount + " -" + vagent


       if 'str' in line:
          break

print " "
vapi = os.popen("grep api " + thepath + " | wc -l").read()

print "api mentions = " + vapi

vdownloader = os.popen("grep downloader " + thepath + " | wc -l").read()
print "downloader mentions = " + vdownloader

vsoap = os.popen("grep soap " + thepath + " | wc -l").read()
print "soap mentions = " + vsoap
