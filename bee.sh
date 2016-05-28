#################
# bee.sh    
# Starts and stops the bee services as follows:
# webstart      Starts the web service server
# webstop       Stops the web service server
# webcheck      Checks the web service server is running. Returns 0 if yes, 1 if no.
# statstart     Starts the statistics service      
# statstop      Stops the statistics service
# statcheck     Checks the statistics service is running. Returns 0 if yes, 1 if no.

# set the install directory location
BEE_PATH=`pwd`

# Set to your version of python
PYTHON=python3

# Set to your port number for this instance of the bee system
# i.e. different port numbers between different instances allows
# you to have multiple instances on the same server.
port=443

# start the webservice server
webstart() {
    echo "Starting Bee webservice server: "     
    echo "BEE path: "
    echo "$BEE_PATH"  
    echo "Port: $port"
    sudo $PYTHON  $BEE_PATH\/backend/beeWebServices.py $BEE_PATH $port &
    echo $! > $BEE_PATH/beeWebServices.lock 
    echo $!
}

# Stop the webservice server
webstop() {
    echo "Stopping Bee webservice server: " 	
    sudo kill `cat $BEE_PATH/beeWebServices.lock`
    echo  $BEE_PATH/beeWebServices.lock
    rm -f $BEE_PATH/beeWebServices.lock
}

# Check the web service
webcheck() {
    echo "Port: $port"
    if [ -f "$BEE_PATH/beeWebServices.lock" ]
    then 
        echo AAA
	if ps -p `cat $BEE_PATH/beeWebServices.lock` > /dev/null
        then
            echo "running"
            return 0  # running
        else
            echo "not running"
            return 1  # Not running
        fi
    else
	echo BBB
        echo "not running"
        return 1
    fi
}

# start the statistics server
statstart() {
    echo "Starting Bee stat server: "    
    echo "BEE path: " 
    echo "$BEE_PATH"
    $PYTHON $BEE_PATH\/backend/beeStat.py $BEE_PATH &
    echo $! > $BEE_PATH/beeStat.lock 
}

# Stop the statistics server
statstop() {
    echo "Stopping Bee statistics server: " 	
    touch $BEE_PATH/beeStatStop
}

# Check the statistics service
statcheck() {
    if [ -f "$BEE_PATH/beeStat.lock" ]
    then 
        if ps -p `cat $BEE_PATH/beeStat.lock` > /dev/null
        then     
            if [ -f "$BEE_PATH/beeStatStop" ]
            then
                echo "pending stop"
                return 0
            else
                echo "running"
                return 0  # running
            fi
        else
            echo "not running"
            return 1  # Not running
        fi
    else
        echo "not running"
        return 1
    fi
}

### main logic ###
case "$1" in
  webstart)
        if webcheck
        then
            gg= "true"  # dummy command
        else
            webstart
        fi
        ;;
  webstop)
        if webcheck
        then
            webstop
        fi
        ;;
  webcheck)
        webcheck
        ;;
  statstart)
	if statcheck
	then
	    gg="true"  # dummy command
	else
	    statstart
	fi
        ;;
  statstop)
	if statcheck
	then
	    statstop
        fi
        ;;
  statcheck)
	statcheck
        ;;
  *)
        echo $"Usage: $0 {webstart|webstop|webcheck|statstart|statstop|statcheck}"
        exit 1
	;;
esac
