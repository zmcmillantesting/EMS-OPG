import csv
import datetime
#total mac addresses 53,503
# start: 00:13:C6:13:3F:00 # end: 00:13:C6:14:0F:FF

def Main():
    # val = int("0013C6133F01", base=16)
    # print(hex(val))
    # hex_val = hex(val + 1)
    # print("incremented hex: ", hex_val)
    Mac = int("0013C6133F00", base=16)
    # for i in range(0, 53504):
    #     hex_val = hex(Mac + i)
    #     print(hex_val[2:].upper().zfill(12))

    with open("mac_addresses.csv", "w", newline='') as csvfile:
        mac_writer = csv.writer(csvfile)
        mac_writer.writerow(["Order", "Serial", "MAC Address", "Is Used", "Is Step 10", "Is Step 11", "Operator", "TimeStamp", "Edited", "Explanation"])
        for i in range(0, 53504):
            # hex
            hex_val = hex(Mac + i)
            mac_address = hex_val[2:].upper().zfill(12)
            # format
            mac_address = formatMACAddress(mac_address)
            # if used
            ifUsed = False
            # Order
            order = " "
            # Serial Data
            serial = " "
            #is step 8 or 9
            isStep8 = False
            isStep9 = False

            operator = " "

            timestamp = None
            # Edited?
            edited = False
            edited_by = " "

            explanation = " "

            mac_writer.writerow([order, serial, mac_address, ifUsed, isStep8, isStep9, operator, timestamp, edited, explanation])

def formatMACAddress(mac_address):
    """Format the MAC address to the standard format."""
    return ':'.join(mac_address[i:i+2] for i in range(0, len(mac_address), 2))


if __name__ == "__main__":
    Main()
else:
    print("the main module is not running")


# 8991.1-0001-3126,00:13:C6:13:3F:00,True,True,False
# 8991.1-0001-3126,00:13:C6:13:3F:01,True,False,True
# 8991.1-0002-3126,00:13:C6:13:3F:02,True,True,False
# 8991.1-0002-3126,00:13:C6:13:3F:03,True,False,True
# 8991.1-0003-3126,00:13:C6:13:3F:04,True,True,False
# 8991.1-0003-3126,00:13:C6:13:3F:05,True,False,True
# 8991.1-0004-3126,00:13:C6:13:3F:06,True,True,False
# 8991.1-0004-3126,00:13:C6:13:3F:07,True,False,True
# 8991.1-0005-3126,00:13:C6:13:3F:08,True,True,False
# 8991.1-0005-3126,00:13:C6:13:3F:09,True,False,True
# 8991.1-0006-3126,00:13:C6:13:3F:0A,True,True,False
# 8991.1-0006-3126,00:13:C6:13:3F:0B,True,False,True
# 8991.1-0007-3126,00:13:C6:13:3F:0C,True,True,False
# 8991.1-0007-3126,00:13:C6:13:3F:0D,True,False,True
# 8991.1-0008-3126,00:13:C6:13:3F:0E,True,True,False
# 8991.1-0008-3126,00:13:C6:13:3F:0F,True,False,True
# 8991.1-0009-3126,00:13:C6:13:3F:10,True,True,False
# 8991.1-0009-3126,00:13:C6:13:3F:11,True,False,True
# 8991.1-0010-3126,00:13:C6:13:3F:12,True,True,False
# 8991.1-0010-3126,00:13:C6:13:3F:13,True,False,True
# 8990.1-0001-3325,00:13:C6:13:3F:14,True,True,False
# 8990.1-0001-3325,00:13:C6:13:3F:15,True,False,True
# 8990.1-0002-3325,00:13:C6:13:3F:16,True,True,False
# 8990.1-0002-3325,00:13:C6:13:3F:17,True,False,True
# 8990.1-0003-3325,00:13:C6:13:3F:18,True,True,False
# 8990.1-0003-3325,00:13:C6:13:3F:19,True,False,True
# 8990.1-0004-3325,00:13:C6:13:3F:1A,True,True,False
# 8990.1-0004-3325,00:13:C6:13:3F:1B,True,False,True
# 8990.1-0005-3325,00:13:C6:13:3F:1C,True,True,False
# 8990.1-0005-3325,00:13:C6:13:3F:1D,True,False,True
# 8990.1-0006-3325,00:13:C6:13:3F:1E,True,True,False
# 8990.1-0006-3325,00:13:C6:13:3F:1F,True,False,True
# 8990.1-0007-3325,00:13:C6:13:3F:20,True,True,False
# 8990.1-0007-3325,00:13:C6:13:3F:21,True,False,True
# 8990.1-0008-3325,00:13:C6:13:3F:22,True,True,False
# 8990.1-0008-3325,00:13:C6:13:3F:23,True,False,True
# 8990.1-0009-3325,00:13:C6:13:3F:24,True,True,False
# 8990.1-0009-3325,00:13:C6:13:3F:25,True,False,True
# 8990.1-00010-3325,00:13:C6:13:3F:26,True,True,False
# 8990.1-00010-3325,00:13:C6:13:3F:27,True,False,True
# 8992.1-0001-3325,00:13:C6:13:3F:28,True,True,False
# 8992.1-0001-3325,00:13:C6:13:3F:29,True,False,True
# 8992.1-0002-3325,00:13:C6:13:3F:2A,True,True,False
# 8992.1-0002-3325,00:13:C6:13:3F:2B,True,False,True
# 8992.1-0003-3325,00:13:C6:13:3F:2C,True,True,False
# 8992.1-0003-3325,00:13:C6:13:3F:2D,True,False,True
# 8992.1-0004-3325,00:13:C6:13:3F:2E,True,True,False
# 8992.1-0004-3325,00:13:C6:13:3F:2F,True,False,True
# 8992.1-0005-3325,00:13:C6:13:3F:30,True,True,False
# 8992.1-0005-3325,00:13:C6:13:3F:31,True,False,True
# 8992.1-0006-3325,00:13:C6:13:3F:32,True,True,False
# 8992.1-0006-3325,00:13:C6:13:3F:33,True,False,True
# 8992.1-0007-3325,00:13:C6:13:3F:34,True,True,False
# 8992.1-0007-3325,00:13:C6:13:3F:35,True,False,True
# 8992.1-0008-3325,00:13:C6:13:3F:36,True,True,False
# 8992.1-0008-3325,00:13:C6:13:3F:37,True,False,True
# 8992.1-0009-3325,00:13:C6:13:3F:38,True,True,False
# 8992.1-0009-3325,00:13:C6:13:3F:39,True,False,True