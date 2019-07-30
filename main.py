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
    
else:
    from emulated_hx711 import HX711

mydb = mysql.connector.connect(
  host="192.168.1.8",
  user="user",
  passwd="testrun",
  database="wim2"
)
date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #print date without microsecond
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

# list_truk = []
#
# class Truk:
#     def __init__(self, x, waktu1, sensor1, sensor2):
#         self.waktu1 = waktu1
#         # self.waktu2 = None
#         self.x = x
#         self.sensor1 = sensor1
#         self.sensor2 = sensor2
#
#     def set_waktu2(self, waktu):
#         self.waktu2 = waktu
#
#     def getTruk(self):
#         waktu = self.waktu2 - self.waktu1  # Dalam Detik
#         print "Waktu : %s" % float(round(waktu, 2))
#         kecepatan = int(jarak) * float(round(waktu, 2))
#         print "Kecepatan : %s" % (kecepatan)
#         print "Sensor 1 = %s Sensor 2 = %s Kecepatan = %s" % (self.sensor1, self.sensor2, kecepatan)
#         return (date, self.sensor1, self.sensor2, kecepatan)

while True:
    try:

        y = int(1000)  # Asumsi berat minimum truck dalam KG
        jarak = int(5)  # Dalam Meter
        jenis1 = "Truck"
        jenis2 = "Bukan Truck"

        Sensor1 = hx.get_weight(5)
        Sensor2 = hx2.get_weight(5)
        print "A: %s Gram, B: %s Gram" % (Sensor1, Sensor2)


        if Sensor1 >= y:
            # time.sleep(1)
            timeSensor1 = time.time()
            # list_truk.append(Truk(date,timeSensor1,Sensor1,Sensor2))
            print timeSensor1
        if Sensor2 >= y:
            # time.sleep(1)
            timeSensor2 = time.time()
            # list_truk[0].set_waktu2(timeSensor2)
            print timeSensor2
        if Sensor1 >= y and Sensor2 >= y:
            waktu = timeSensor2 - timeSensor1 #Dalam Detik
            print "Waktu : %s" % float(round(waktu, 2))
            kecepatan = int(jarak) / float(round(waktu, 2))
            print "Kecepatan : %s" % (kecepatan)
            print "Jenis : %s" % (jenis1)
            print "Sensor 1 = %s Sensor 2 = %s Kecepatan = %s Jenis Kendaraan : %s" % (Sensor1, Sensor2, kecepatan, jenis1)
            sql = "INSERT INTO weight (Date,BeratWim1,BeratWim2,Kecepatan,Keterangan) VALUES (%s,%s,%s,%s,%s)"
            val = (date,Sensor1,Sensor2,kecepatan,jenis2)
            # val = list_truk[0].getTruk()
            # list_truk.pop(0)
            mycursor.execute(sql,val)
            mydb.Commit()
        elif Sensor1 < y and Sensor2 < y:
            waktu = timeSensor2 - timeSensor1  # Dalam Detik
            print "Waktu : %s" % float(round(waktu, 2))
            kecepatan = int(jarak) / float(round(waktu, 2))
            print "Kecepatan : %s" % (kecepatan)
            print "Jenis : %s" % (jenis2)
            print "Sensor 1 = %s Sensor 2 = %s Kecepatan = %s Jenis Kendaraan : %s" % (
            Sensor1, Sensor2, kecepatan, jenis2)
            sql = "INSERT INTO weight (Date,BeratWim1,BeratWim2,Kecepatan,Keterangan) VALUES (%s,%s,%s,%s,%s)"
            val = (date, Sensor1, Sensor2, kecepatan, jenis2)
            # val = list_truk[0].getTruk()
            # list_truk.pop(0)
            mycursor.execute(sql, val)
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

 