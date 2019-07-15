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

hx = HX711(20, 21) #GPIONumbering
hx2 = HX711(23,24)
# Pada beberapa versi python,numpy dan hx711 sendiri selalu byte yang tidak selalu sama
# Jika Anda mengalami nilai-nilai super acak, ubah nilai-nilai ini ke MSB atau LSB hingga mendapatkan nilai yang lebih stabil.
# Menurut pada Datasheet Hx711, Parameter kedua merupakan MSB JANGAN DI UBAH.
hx.set_reading_format("MSB", "MSB")
hx2.set_reading_format("MSB", "MSB")
# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# Dalam hal ini, 92 adalah 1 gram karena, dengan 1 sebagai unit referensi saya mendapat angka mendekati 0 tanpa bobot
# dan saya mendapat angka sekitar 184000 ketika saya menambahkan 2kg. Jadi :
# Jika 2000 gram adalah 184000 maka 1000 gram adalah 184000/2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(200) #calibration unit
hx2.set_reference_unit(225)
hx.reset()
hx2.reset()
hx.tare()
hx2.tare()
print "Tare done! Add weight now..."

while True:
    try:
        y = int(1000)  # Asumsi berat minimum truck dalam KG
        jarak = int(20)  # Dalam Meter

        Sensor1 = hx.get_weight(5)
        Sensor2 = hx2.get_weight(5)
        print "A: %s Gram, B: %s Gram" % (Sensor1, Sensor2)


        if Sensor1 >= y:
            timeSensor1 = time.time()
            print timeSensor1
        if Sensor2 >= y:
            timeSensor2 = time.time()
            print timeSensor2
        while Sensor1 >= y and Sensor2 >= y:
            waktu = timeSensor2 - timeSensor1 #Dalam Detik
            print "Waktu : %s" % float(round(waktu, 2))
            kecepatan = int(jarak) / float(round(waktu, 2))
            print "Kecepatan : %s" % (kecepatan)
            print "Sensor 1 = %s Sensor 2 = %s Kecepatan = %s" % (Sensor1, Sensor2, kecepatan)
            sql = "INSERT INTO weight (Date,BeratWim1,BeratWim2,Kecepatan) VALUES (%s,%s,%s,%s)"
            val = (x,Sensor1,Sensor2,kecepatan)
            mycursor.execute(sql,val)
            mydb.Commit()
            #print (mycursor.rowcount, "Data Send to database")

        
       
        

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)
        print (mycursor.rowcount, "Data Send to database")
        print ""
        print ""
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
#print(mycursor.rowcount, "record inserted.")

 