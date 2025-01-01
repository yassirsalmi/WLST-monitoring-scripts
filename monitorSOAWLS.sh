#!/bin/bash

##############################################
# Weblogic Server Monitoring Script
##############################################

# Oracle Middleware environment variables
export MW_HOME=/home/yassir/Oracle/Middleware/Oracle_Home
export DOMAIN_HOME=$MW_HOME/user_projects/domains/test_domain

# security manager options
export JAVA_OPTIONS="-Djava.security.manager -Djava.security.policy=$MW_HOME/wlserver/server/lib/weblogic.policy ${JAVA_OPTIONS}"

$MW_HOME/oracle_common/common/bin/wlst.sh /home/yassir/oracle/scripts/wlst/monitor_all_servers.py


#----------------------------------------
# Variables
#----------------------------------------
ENV=PROD12C
ORACLE_HOME=~/Oracle/Middleware/Oracle_Home
SCRIPT_PATH=/home/yassir/oracle/scripts/wlst
SERVERS=webLogic
PORT=7001
EMAILS="yssr1949@gmail.com"  

#----------------------------------------
# Set environment
#----------------------------------------
source ${ORACLE_HOME}/wlserver/server/bin/setWLSEnv.sh 2>&1 > /dev/null

#----------------------------------------
# Loop through server list
#----------------------------------------
for serv in ${SERVERS}
do
    #----------------------------------------
    # Run WLST script
    #----------------------------------------
    echo "********************************************************"
    echo " Running Server status report for :${serv}  ${PORT}"
    echo "********************************************************"
    ${ORACLE_HOME}/oracle_common/common/bin/wlst.sh ${SCRIPT_PATH}/monitor_all_servers.py "${serv}" "${PORT}"
    

    echo ' ********** END OF REPORT ********** ' >> ${SCRIPT_PATH}/monitorstatus.html

    #----------------------------------------
    # Set email subject
    #----------------------------------------
    grep "yellow" ${SCRIPT_PATH}/monitorstatus.html >> /dev/null
    if [ $? == 0 ]; then
        ALERT_CODE="[WARNING]"
    fi

    grep "red" ${SCRIPT_PATH}/monitorstatus.html >> /dev/null
    if [ $? == 0 ]; then
        ALERT_CODE="[CRITICAL]"
    fi

    grep "green" ${SCRIPT_PATH}/monitorstatus.html >> /dev/null
    if [ $? == 0 ]; then
        ALERT_CODE="[GREEN]"
    fi

    ENVIRONMENT=`echo $ENV | tr '[:lower:]' '[:upper:]'`
    
    #----------------------------------------
    # Send email
    #----------------------------------------
    CONTENT=${SCRIPT_PATH}/monitorstatus.html
    SUBJECT="${ALERT_CODE} - SOA ${ENVIRONMENT} ENVIRONMENT STATUS REPORT "
    ( echo "Subject: $SUBJECT"
    echo "MIME-Version: 1.0"
    echo "Content-Type: text/html"
    echo "Content-Disposition: inline"
    cat $CONTENT )| /usr/sbin/sendmail $EMAILS

done

rm ${SCRIPT_PATH}/monitorstatus.html
