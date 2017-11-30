#!/usr/bin/env python
#
#Andy Pitcher <andy.pitcher@concordia.ca>
#This program trains and collects the system calls run by a given app by generating random usage
#
##############################################################################################
from match_sig import check_sig
import subprocess
import pexpect
import sys,os
from random import randint

#Env setup
attempt=randint(0,100)
temp_strace_dir="/system/xbin/strace_dir/"+str(attempt)+"/"
app=sys.argv[1]
rand_iterations="50"

#Cleaning strace dir
os.system("adb shell 'rm -rf /system/xbin/strace_dir/*'")

#Create training directory on Android device
os.system("adb shell mkdir "+temp_strace_dir)  

#Retrieve zygote PID to attach the future app pid
cmd_get_zygote_pid="adb shell ps | grep zygote | awk '{print $2}'"
zygote_PID=subprocess.check_output([cmd_get_zygote_pid], shell=True)

#Get all attached Zigote's child process and App PID to pull the its strace output
cmd_get_all_pid="adb shell pgrep -P"+zygote_PID
cmd_get_app_pid="adb shell ps | grep "+app+" | awk '{print $2}'"

#Start zygote's PID strace subprocess in bg which collects and copy its children process in temp_strace_dir 
#cmd_get_all_strace="adb shell strace -e"+trace_filter+" -ff -o"+temp_strace_dir+"trace -p"+str(zygote_PID)
cmd_get_all_strace="adb shell strace -ff -o"+temp_strace_dir+"trace -p"+str(zygote_PID)
proc_strace=subprocess.Popen([cmd_get_all_strace], shell=True)

#Print all attached Zygote's child process before lauching the app
zygote_child_PID=subprocess.check_output([cmd_get_all_pid], shell=True)
print "Number of child process\n"+zygote_child_PID

#input("Press any key to start the next? Default["+app+"]")

#Start the app and launch random unit tests: rand_iterations, throttle can be removed or increased to reduce the delay between events
os.system("adb shell monkey --throttle 50 -p "+app+" -c android.intent.category.LAUNCHER "+rand_iterations)
app_PID=subprocess.check_output([cmd_get_app_pid], shell=True)

#Stop the app
os.system("adb shell am force-stop "+app)
#Stop the Zigote strace
proc_strace.kill()

#Pull the trace.app_PID file to the computer and remove temp_strace_dir
#os.system("adb pull "+temp_strace_dir+"trace."+app_PID)
os.system("adb pull "+temp_strace_dir+" reports/")

status,details=check_sig(attempt)
print status
print details
#print "Results are available in reports/"+str(attempt) 
#print "To check reverse_tcp success or attempt, run the following command in the reports/"+str(attempt)+"\n\nif grep -ri Meterpreter ; then echo attack;elif grep -ri 172.16.16.5; then echo Attempt;else echo Legit;fi"

os.system("adb shell rm -rf "+temp_strace_dir)
