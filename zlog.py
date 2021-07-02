#!/usr/bin/python
# 2.3 // 2021-7-1
# Questions? Problems? Need more? ask Jackie

import os
import sys
import datetime
import subprocess
import argparse
global user_agent_str

######## GLOBAL VARS #######
saveplace = "/srv/"
logfile = "/log/access.log" # Default
linecount = 0
NC='\033[0m' # No Color
YELLOW='\033[0;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
HPINK ='\033[1;45m'

if sys.version_info[0] < 3:
   raise Exception(RED + "Zlog now uses Python 3: python3 ./zlog.py" + NC)
   sys.exit()

######### EXTRA ARGUMENT MAGIC AKA LETS DO OTHER THINGS ##########
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--newfile', action='store_true',
   help="allows you to examine log file besides the default: python3 zlog.py --newfile")
parser.add_argument('-w', '--whois', action='store_true',
   help="checks whois by IPs for common traffic sources: python3 zlog.py --whois")
parser.add_argument('-a', '--attacks', action='store_true',
   help="checks for common attacks/scans: python3 zlog.py --attacks")
parser.add_argument('-c', '--cpu', action='store_true',
   help="checks for high CPU usage in logs: python3 zlog.py --cpu")
parser.add_argument('-m', '--min', action='store', dest='min', type=int,
   help="check logs for past x minutes: python3 zlog.py --attacks --min 5")
args = parser.parse_args()


######## GLOBAL FUNCTIONS ######

# Check logfile exists and if it's large
def checklog(logfile,saveplace):
   if os.path.exists(logfile):
      log_size = os.path.getsize(logfile)
   else:
      print("Can not find log at: " + logfile)
      sys.exit()

   filter_tmp_log = False
   if log_size >= 250000000:
      filter_tmp_log = True
      print("\nThe log is huge ({}M), filtering...".format(log_size / 1000000))
      now = datetime.datetime.now()
      today_str = "{}/{}/{}:".format(now.strftime("%d"), now.strftime("%b"), now.strftime("%Y"))
      os.popen("cat {} | grep {} > {}zLog-filtered-tmp.log".format(logfile, today_str, saveplace))
      logfile = "{}zLog-filtered-tmp.log".format(saveplace)

# Get Log start time
def getlogstart(file):
   vhead = os.popen("head -n1 " + file  + " | awk -F ' ' '{print $3}'").read().replace("  ", " ")
   vhead = vhead.replace("[", "").replace("\n", "")

   vtail = os.popen("tail -n1 " + file  + " | awk -F ' ' '{print $3}'").read().replace("  ", " ")
   vtail = vtail.replace("[", "").replace("\n", "")

   print(HPINK + "Data range: {} -> {} (now).".format(vhead, vtail) + NC)

# Get Top <num> IPs
def gettopips(file,amount,saveplace):
   if amount==100:
      cmdget = "awk {'print $1'}  " + file + " | sort | uniq -c | sort -n  > " + saveplace  + "zLog.ips.log"
   else:
      cmdget = "awk {'print $1'}  " + file + " | sort | uniq -c | sort -n | tail -n" + str(amount) +" > " + saveplace  + "zLog.ips.log"
   os.system(cmdget)
   cmdip = "awk {'print $2'} " + saveplace  + "zLog.ips.log > " + saveplace + "zLog.tmp.log"
   os.system(cmdip)

# Get Agent of thing
def getagent(thing,logfile):
   global user_agent_str
   user_agent_str = os.popen("grep -m1 " + thing + " " + logfile + " | awk '{$1=$2=$3=$4=$5=$6=$7=$8=$9=$10=\"\"; print $0}'").read()
   user_agent_str = user_agent_str.replace('"', '').replace(" ", '').replace(";", '').replace("\n", '').replace("\t", '')
   return user_agent_str

######### --newfile -n IF DIFF FILE CHOSEN ###########
if args.newfile:
   logfile = input("Enter logfile path (Ex. " + YELLOW + "/log/access.log.1" + NC + "): ")
   if str(logfile) == "":
      logfile = "/log/access.log"

   #past this point uses same code as default zlog

######## --whois -w IF WHOIS OPTION CHOSEN #########
if args.whois:
   wholist = []  #declare list for whois strings
   whototals = {}  #declare dict for whois totals
   touch = "touch " + saveplace + "zLog.whois.log"
   logfile = input("Enter logfile path (Ex. " + YELLOW + "/log/access.log" + NC + "): ")
   if str(logfile) == "":
      logfile = "/log/access.log"

   # check if minutes are chosen
   if args.min:
      if args.min >= 1:
         getmins = "awk -v d1=\"$(date --date=\"-" + str(args.min) + " min\" \"+%d/%b/%Y:%T\")\" -v d2=\"$(date \"+%d/%b/%Y:%T\")\" '{gsub(/^[\[\t]+/, \"\", $3);}; $3 > d1 && $3 < d2 || $3 ~ d2' " + logfile + " > " + saveplace + "zLog.min.tmp"
         os.system(getmins)
         logfile = saveplace + "zLog.min.tmp"

   # CHECK LOGFILE
   checklog(logfile,saveplace)

   # GET TIME START OF LOG FILE
   getlogstart(logfile)

   # GET IP COUNTS
   print("\n" + YELLOW + str("Grabbing IPs...") + "\033[1;m")
   gettopips(logfile,100,saveplace)

   # WHO ARE THESE JOKERS?
   #print "{} - {} - {}".format("Count", "Address", "Whois")
   with open(saveplace + "zLog.tmp.log") as f:
       contents = f.readlines()
       for line in reversed(contents):
          line = line.replace("\n", "")
          linecount = linecount + 1

          # grab count
          tmp_str = os.popen("grep -m1 " + line + " " + saveplace + "zLog.ips.log | awk -F ' ' '{print $1,$2}'").read().replace("\n", "")
          count_str = tmp_str.split(" ")[0]

          whois = os.popen("whois " + line + " | grep -E -i 'OrgName|StateProv|Country' | sort -u").read().replace(" ",'').replace("\n", "")
          whois = whois.replace("Country", " ").replace("OrgName", " ").replace("StateProv", " ").replace("'", "").replace(",", "")
          savewho = "echo " + count_str + ", " + line + ", '" + whois + "' >> " + saveplace + "zLog.whois.log"
          os.system(savewho)

          # save just whois to list
          wholist.append(whois)

          # adjust output according to line number
          if linecount == 50:
             break
   #print "--------------------------------------------------------------------"

   print(" ")
   print(YELLOW + "WHOIS - HITS / LOCATION / " + NC)

   # Total # of hits in file
   # cat /srv/zLog.whois.log | awk {'print $1'} | awk '{ SUM += $1} END { print SUM }'

   # Number of hits from US
   # cat /srv/zLog.whois.log | grep :US | awk {'print $1'} | awk '{ SUM += $1} END { print SUM }'

   # Check total hits for each whois
   for w in wholist:
      docount = os.popen("grep '" + str(w) + "' " + saveplace + "zLog.whois.log | awk '{ SUM += $1} END { print SUM }'").read().replace("\n", "")
      #print("docount = " + docount + " " + w)  #debug
      # Add each whois to a dictionary with total if its not already recorded
      if w not in whototals:
         whototals[w] = docount
         #print("added above to dict")  #debug

   #print dictionary sorted by values instead of key
   sort_who = sorted(whototals.items(), key=lambda x: int(x[1]), reverse=True)
   for i in sort_who:
      print("{} |{}".format(i[1], i[0]))


######### --attacks -a IF ATTACK CHECK IS CHOSEN ##########
if args.attacks:
   logfile = input("Enter logfile path (Ex. " + YELLOW + "/log/access.log" + NC + "): ")
   if str(logfile) == "":
      logfile = "/log/access.log"

   print(" ")
   print(YELLOW + "PATH / HITS" + NC)

   # check if minutes are chosen
   if args.min:
      if args.min >= 1:
         getmins = "awk -v d1=\"$(date --date=\"-" + str(args.min) + " min\" \"+%d/%b/%Y:%T\")\" -v d2=\"$(date \"+%d/%b/%Y:%T\")\" '{gsub(/^[\[\t]+/, \"\", $3);}; $3 > d1 && $3 < d2 || $3 ~ d2' " + logfile + " > " + saveplace + "zLog.min.tmp"
         os.system(getmins)
         logfile = saveplace + "zLog.min.tmp"
         #print(getmins)  #debug

   # payment-informtation API hits declined (carding attack)
   carding = os.popen("grep payment-information " + logfile + " | grep ' 400 ' | grep POST | wc -l").read().replace("\n", "")
   print("1. payment-information declines (M2 carding attacks): " + YELLOW + carding + NC)

   account = os.popen("grep ' /customer/account/create' " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("2. customer/account/create POSTS: " + YELLOW + account + NC)

   newsletter = os.popen("grep newsletter " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("3. newsletter POSTS: " + YELLOW + newsletter + NC)

   sqlinj = os.popen("grep -E 'SELECT|UNION|1=1|SLEEP' " + logfile + " | wc -l").read().replace("\n", "")
   print("4. possible SQL injections: " + YELLOW + sqlinj + NC)

   wp = os.popen("grep -E 'wp-admin|wp-login|xmlrpc.php' " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("5. possible wp brute force: " + YELLOW + wp + NC)

   dirt = os.popen("grep '\.\./' " + logfile + " | wc -l").read().replace("\n", "")
   print("6. directory traversal attempts: " + YELLOW + dirt + NC)

   wishlist = os.popen("grep wishlist " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("7. wishlist POSTS: " + YELLOW + wishlist + NC)

   scan = os.popen("grep -Ei '\.zip|\.gz|\.tar' " + logfile + " | wc -l").read().replace("\n", "")
   print("8. random scans: " + YELLOW + scan + NC)

   m1 = os.popen("grep -E 'downloader|magmi' " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("9. M1 downloader/magmi POSTS: " + YELLOW + m1 + NC)

   account2 = os.popen("grep ' /customer/account/login' " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("10. customer/account/login POSTS: " + YELLOW + account2 + NC)

   search = os.popen("grep ' /catalogsearch/result' " + logfile + " | wc -l").read().replace("\n", "")
   print("11. catalogsearch/result HITS: " + YELLOW + search + NC)

   pp = os.popen("grep /paypal/transparent/requestSecureToken " + logfile + " | grep POST | wc -l").read().replace("\n", "")
   print("12. paypal/transparent/requestSecureToken POSTS: " + YELLOW + pp + NC)

   print(" ")
   pick = input("Examine one of the above? If so, input #: ")
   #print("pick = " + pick + " carding = " + carding)  #debug

   # If examime an attack, is chosen, lets get the details
   if int(pick) == 1:
      if str(carding) == "0":
         sys.exit(RED + "Results were 0 for carding. Nothing to examine." + NC)
      else:
         examine = "grep payment-information " + logfile + " | grep ' 400 ' | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 2:
      if str(account) == "0":
         sys.exit(RED + "Results were 0 for account/create. Nothing to examine." + NC)
      else:
         examine = "grep ' /customer/account/create' " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 3:
      if str(newsletter) == "0":
         sys.exit(RED + "Results were 0 for newsletter posts. Nothing to examine." + NC)
      else:
         examine = "grep newsletter " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 4:
      if str(sqlinj) == "0":
         sys.exit(RED + "Results were 0 for sql injections. Nothing to examine." + NC)
      else:
         examine = "grep -E 'SELECT|UNION|1=1|SLEEP' " + logfile + " > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 5:
      if str(wp) == "0":
         sys.exit(RED + "Results were 0 for wp attacks. Nothing to examine." + NC)
      else:
         examine = "grep -E 'wp-admin|wp-login|xmlrpc.php' " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 6:
      if str(dirt) == "0":
         sys.exit(RED + "Results were 0 for traversal attempts. Nothing to examine." + NC)
      else:
         examine = "grep '\.\./' " + logfile + " > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 7:
      if str(wishlist) == "0":
         sys.exit(RED + "Results were 0 for wishlist posts. Nothing to examine." + NC)
      else:
         examine = "grep wishlist " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 8:
      if str(scan) == "0":
        sys.exit(RED + "Results were 0 for scans. Nothing to examine." + NC)
      else:
         examine = "grep -Ei '\.zip|\.gz|\.tar' " + logfile + " > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 9:
      if str(m1) == "0":
        sys.exit(RED + "Results were 0 for download/magmi. Nothing to examine." + NC)
      else:
         examine = "grep -E 'downloader|magmi' " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 10:
      if str(account2) == "0":
         sys.exit(RED + "Results were 0 for account/login. Nothing to examine." + NC)
      else:
         examine = "grep ' /customer/account/login' " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 11:
      if str(search) == "0":
         sys.exit(RED + "Results were 0 for search. Nothing to examine." + NC)
      else:
         examine = "grep ' /catalogsearch/result' " + logfile + " > " + saveplace + "zLog.tmp.attacks"
   elif int(pick) == 12:
      if str(pp) == "0":
         sys.exit(RED + "Results were 0 for paypal posts. Nothing to examine." + NC)
      else:
         examine = "grep /paypal/transparent/requestSecureToken " + logfile + " | grep POST > " + saveplace + "zLog.tmp.attacks"

   # if user chooses no option or hits enter go backto prompt
   else:
      sys.exit("Nothing chosen. Later!")

   # print 100 chosen attack examples
   print("\n" + HPINK + str("100 example logs") + "\033[1;m")
   os.system(examine)
   stop = 0
   with open(saveplace + "zLog.tmp.attacks") as a:
      for line in a:
         line = line.replace("\n", "")
         print(line)
         stop = stop + 1
         if stop == 100:
            break

   # get IPs
   print("\n" + HPINK + str("Top 25 IPs associated") + "\033[1;m")
   gettopips(saveplace + "zLog.tmp.attacks",25,saveplace)

   # GET AGENT OF EACH IP
   print("{} - {} - {}".format("Count", "Address", "User Agent"))
   #max_count_len = 0
   with open(saveplace + "zLog.tmp.log") as f:
      contents = f.readlines()
      for line in reversed(contents):
         line = line.replace("\n", "")

         # grab count
         tmp_str = os.popen("grep -m1 " + line + " " + saveplace + "zLog.ips.log | awk -F ' ' '{print $1,$2}'").read().replace("\n", "")
         count_str = tmp_str.split(" ")[0]

         getagent(line,logfile)
         print("{} - {} - {}".format(count_str, line, user_agent_str))


########### --cpu -c IF CPU OPTION IS CHOSEN ##########
if args.cpu:
   logfile = input("Enter logfile path (Ex. " + YELLOW + "/log/php-fpm/php.access.log" + NC + "): ")
   if str(logfile) == "":
      logfile = "/log/php-fpm/php.access.log"

   # GET HIGH CPU
   getcpu = "grep -av php-fpm-status " + logfile + " | awk -F'\"' '{print $36,$32,$4,$8,$24}' | sort -n > " + saveplace + "zLog.cpu.log"
   os.system(getcpu)
   #print(getcpu)  #debug

   # GET TOP 20 IPSs
   print(" ")
   print(RED + "Top 20 IPs for high CPU" + NC)
   byip = "awk {'print $4'} " + saveplace + "zLog.cpu.log | sort | uniq -c | sort -n | tail -n20 > " + saveplace + "zLog.cpu.ex.log"
   os.system(byip)

   # PRINT THE IPs
   print(YELLOW + " HITS / IP " + NC)
   byipshow = os.popen("cat " + saveplace + "zLog.cpu.ex.log").read()
   print(byipshow)

   #GET EXAMPLE LOGS OF ABOVE IPs
   byipex = os.popen("awk '{print $2}' " + saveplace + "zLog.cpu.ex.log | tail -n1").read().replace("\n", "")
   byipexget = os.popen("grep \"" + byipex + "\" " + saveplace + "zLog.cpu.log | tail -n20").read()
   print(RED + "Examples of IPs:" + NC)
   print(YELLOW + "CPU% / request_time / timestamp / IP / path" + NC)
   print(byipexget)

   # GET TOP 20 PATHS
   print(RED + "Top 20 paths for high CPU" + NC)
   bypath = "awk {'print $5'} " + saveplace + "zLog.cpu.log | sort | uniq -c | sort -n | tail -n20 > " + saveplace + "zLog.cpu.path.log"
   os.system(bypath)

   # PRINT THE PATHS
   print(YELLOW + "HITS / PATH" + NC)
   bypathshow = os.popen("cat " + saveplace + "zLog.cpu.path.log").read()
   print(bypathshow)

   #GET EXAMPLE LOGS OF ABOVE PATHS
   bypathex = os.popen("awk '{print $2}' " + saveplace + "zLog.cpu.path.log | tail -n1").read().replace("\n", "")
   bypathexget = os.popen("grep \"" + bypathex + "\" " + saveplace + "zLog.cpu.log | tail -n20").read()
   print(RED + "Examples of PATHS:" + NC)
   print(YELLOW + "CPU% / request_time / timestamp / IP / path" + NC)
   print(bypathexget)

  # check if minutes are chosen
   if args.min:
      if args.min >= 1:
         #getmins = "awk -v d1=\"$(date --date=\"-" + str(args.min) + " min\" \"+%d/%b/%Y:%T\")\" -v d2=\"$(date \"+%d/%b/%Y:%T\")\" '{gsub(/^[\[\t]+/, \"\", $3);}; $3 > d1 && $3 < d2 || $
         #os.system(getmins)
         #logfile = saveplace + "zLog.min.tmp"
         print(RED + "--min -m does not work with --cpu yet. Here is the whole enchilada" + NC)

####### IF NO ARGUMENTS USED, DO SAME OLD REGULAR LOG STATS #######
#if not len(sys.argv) > 1 or args.newfile:
if (not len(sys.argv) > 1) or (args.newfile) or (args.min and not args.attacks and not args.whois and not args.cpu):
   # check if minutes are chosen
   if args.min:
      if args.min >= 1:
         getmins = "awk -v d1=\"$(date --date=\"-" + str(args.min) + " min\" \"+%d/%b/%Y:%T\")\" -v d2=\"$(date \"+%d/%b/%Y:%T\")\" '{gsub(/^[\[\t]+/, \"\", $3);}; $3 > d1 && $3 < d2 || $3 ~ d2' " + logfile + " > " + saveplace + "zLog.min.tmp"
         os.system(getmins)
         logfile = saveplace + "zLog.min.tmp"

   #CHECK LOGFILE
   checklog(logfile,saveplace)

   # GET TIME START OF LOG FILE
   getlogstart(logfile)

   # GET TOP 25 IPs
   print("\n" + HPINK + str("Top 25 IPs") + "\033[1;m")
   gettopips(logfile,25,saveplace)

   # GET AGENT OF EACH IP
   print("{} - {} - {}".format("Count", "Address", "User Agent"))
   #max_count_len = 0
   with open(saveplace + "zLog.tmp.log") as f:
      contents = f.readlines()
      for line in reversed(contents):
         line = line.replace("\n", "")

         # grab count
         tmp_str = os.popen("grep -m1 " + line + " " + saveplace + "zLog.ips.log | awk -F ' ' '{print $1,$2}'").read().replace("\n", "")
         count_str = tmp_str.split(" ")[0]

         getagent(line,logfile)
         print("{} - {} - {}".format(count_str, line, user_agent_str))

   vapi = os.popen("grep api " + logfile + " | wc -l").read().replace("\n", "")
   vdownloader = os.popen("grep downloader " + logfile + " | wc -l").read().replace("\n", "")
   vsoap = os.popen("grep soap " + logfile + " | wc -l").read().replace("\n", "")
   print("\nAPI mentions: {} - SOAP mentions: {} - Downloader mentions: {}\n".format(vapi, vsoap, vdownloader))

   # GET TOP USER AGENTS QUICK CHECK - IGNORES DIFFERENCES BETWEEN STANDARD MOZILLA AGENT
   vagents = os.popen("awk -F\'\"\' \'/GET/ {print $6}\' " + logfile + " | cut -d\' \' -f1 | sort | uniq -c | sort -rn | head -n10").read()
   print(HPINK + str("Top 10 User Agents") + "\033[1;m")
   print(vagents)

   #GET TOP HIT URLs
   vURLs = os.popen("awk {'print $6'} " + logfile + " | sort | uniq -c | sort -n | tail -n20").read()
   print("\n" + HPINK + str("Top 20 Hit URLs") + NC)
   print(vURLs)

# Clean up our mess
os.system("rm {}zLog*".format(saveplace))
os.system("rm ./zlog.py")