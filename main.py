#! /usr/bin/python2

import time
import sys
import os
import threading
import mysql.connector
import datetime


EMULATE_HX711=False

if not EMULATE_HX711:
    print "From HX711"
    import RPi.GPIO as GPIO
    from hx711 import HX711
    # from hx711 import HX7112
else:
    from emulated_hx711 import HX711

mydb = mysql.connector.connect(
  host="192.168.1.8",
  user="user",
  passwd="testrun",
  database="wim2"
)
x = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #print date without microsecond
mycursor = mydb.cursor()

def cleanAndExit():
    print "Cleaning..."

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print "Bye!"
    sys.exit()

hx = HX711(5, 6) #GPIONumbering
# h2x = HX7112(20,21)
# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")
# h2x.set_reading_format("MSB", "MSB")
# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(92) #calibration unit
# h2x.set_reference_unit(92)
hx.reset()
# h2x.reset()
#hx.tare()
# h2x.tare()
print "Tare done! Add weight now..."

# to use both channels, you'll need to tare them both
hx.tare_A()
hx.tare_B()

while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        # weight = hx.get_weight(5)
        # print weight

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this

        y = int(50000)  # Asumsi berat minimum truck
        jarak = int(20)  # Dalam Meter

        val_A = hx.get_weight_A(5)
        val_B = hx.get_weight_B(5)
        print "A: %s  B: %s" % (val_A, val_B)

        pass
        if val_A >= y:
            timeSensor1 = time.time()
            print timeSensor1
        if val_B >= y:
            timeSensor2 = time.time()
            print timeSensor2
        while val_A >= y and val_B >= y:
            waktu = timeSensor2 - timeSensor1 #Dalam Detik
            print "Waktu : %s" % float(round(waktu, 3))
            kecepatan = int(jarak) / float(round(waktu, 3))
            print "Sensor 1 = %s Sensor 2 = %s Kecepatan = %s" % (val_A, val_B, kecepatan)
            sql = "INSERT INTO weight (Date,BeratWim1,BeratWim2,Kecepatan) VALUES (%s,%s,%s,%s)"
            val = (x,val_A,val_B,kecepatan)
            mycursor.execute(sql,val)
            mydb.Commit()
            #print (mycursor.rowcount, "Data Send to database")
            pass


        # val_A = hx.get_weight_A(5)
        # val_B = hx.get_weight_B(5)
        # print "A: %s  B: %s" % ( val_A, val_B )
        # if val_A and val_B >= y:
        #     sql = "INSERT INTO weight (Date,BeratWim1,BeratWim2) VALUES (%s,%s,%s)"
        #     val =(x,val_A,val_B)
        #     mycursor.execute(sql,val)
        #     mydb.commit()
        
       
        

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)
        print (mycursor.rowcount, "Data Send to database")
        print ""
        print ""
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
print(mycursor.rowcount, "record inserted.")
# def sendDataToServer():

#     threading.Timer(600,sendDataToServer).start()
#     print('Sending data to server ')
#     print val
 