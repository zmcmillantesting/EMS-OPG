# Templates for reusability

USERNAME="root"
PASSWORD="default"
STEP_ONE="ls /dev/sd[a-e]"
STEP_TWO="timeout 2s loopback /dev/port0[2-4] -q"
STEP_THREE="timeout 2s loopback /dev/port0[5-8] -q"
STEP_FOUR="ifconfig eth1 up&&sleep 5&&ethtool eth1"
STEP_FIVE="/etc/scripts/swtool diag" # we skip this one as it is not for the boards we currently test
STEP_SIX="echo 1 | tee /sys/class/leds/acm7000:green:sig_*brightness"
STEP_SEVEN="emd -i sysfs" #run twice
#mac 1
#mac2
STEP_EIGHT="setfset | grep eth0 && setfset | grep eth1"
STEPS_COMBINED=