import os
import time


runNum = 100
cValues = [ 1,  10, 100 , 1000 ]
iValues = [ 1, 5, 10, 0 ]
QValues = [ 1,50, 100 , 500, 1000, 10000]


#for test
#cValues = [ 1, 2 ]
#iValues = [ 1, 2 ]
#QValues = [ 1,50, 100 , 500, 1000, 10000]


for cv in cValues :
    for iv in  iValues :
        for qv in  QValues :
            commond = './dnsperf -d dnsRequest -s 192.168.1.30 -c ' + str(cv) + ' -i ' + str(iv ) + ' -Q ' +str(qv)
            print ( commond )
            for  _ in range(runNum):             
                val = os.system(commond)
                #print(val)
                time.sleep(10)

