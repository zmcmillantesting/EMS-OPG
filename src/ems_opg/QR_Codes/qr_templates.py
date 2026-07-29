# steps
# 1 root
# 2 default
STEP3 = "ls /dev/sd[a-e]"
STEP4 = "timeout 2s loopback /dev/port0[2-4] -q"
STEP5 = "timeout 2s loopback /dev/port0[5-8] -q"
STEP6 = "ifconfig eth1 up && sleep 5 && ethtool eth1"

STEP7="emd -i sysfc" #run twice

STEP8 = "setfset -u ethaddr={mac1}"
STEP9 = "setfset -u eth1addr={mac2}"

# combine steps 3, 4, 5, 6, 8
COMBINED = (
    STEP3
    + " && "
    + STEP4
    + " && "
    + STEP5
    + " && "
    + STEP6
)
