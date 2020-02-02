import csv
import os
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import random
import math

## Input by user

Mean_Market_penetration = 5
SD_Market_penetration = 0
Minimum_travel_time = 10          # Minimum acceptable travel time
Maximum_travel_time = 200         # Maximum acceptable travel time
Number_of_runs = 50             # The total number of simulation run want to do
filename = "Result_simulation_FreewayWOV_70P_5P"
actual_travel_time = 56.08 #56.34 #55.22
file_name = "fzpfile_freeway_70P.csv" #input file name



Start_point_of_section = 350    # The distance at which the test section has started
Finish_point_of_section = 5630   # The finish line where the test section has finished
Length_of_section = (Finish_point_of_section - Start_point_of_section)




tt=[]

for i in range(Number_of_runs):
    #########set input parameter in the TCAinput.xml file

    #read the file
    tree = ET.parse('TCAinput.xml')
    root = tree.getroot()
    root.tag

    #for child in root:
        #print(child.tag, child.attrib)

    #root[0][1].text

    #change the seed number
    for rank in root.iter('Seed'):
        new_rank = random.randint(342000,343000)
        rank.text = str(new_rank)
        #rank.set('updated', 'yes')

    #change the market penetration
    for rank1 in root.iter('BSMMarketPenetration'):
        new_rank1 = int(Mean_Market_penetration)#int(round(np.random.normal(loc=Mean_Market_penetration, scale=SD_Market_penetration, size=None)))
        #if new_rank1<.5:
         #   new_rank1=0.5
        rank1.text = str(new_rank1)

    for rank2 in root.iter('FileName'):
        new_rank2 = str(file_name)
        rank2.text = str(new_rank2)

    #write the file into TCAinput.xml
    tree.write('TCAinput.xml')


    ############ Call the TCA to run the program
    os.system("python TCA2.py")



    #### Analysis with the output
    data1=pd.read_csv("BSM_Trans.csv")
    #data1.head()

    data1=data1[["PSN","localtime","spd","x","y"]]
    data1 = data1.sort("PSN")
    data1 = data1[(data1.y>Start_point_of_section)&(data1.y<Finish_point_of_section)]

    data2=data1.groupby("PSN")


    def calcu(dd):   
        a=len(dd)
        if a>2:
            dd=dd.sort("localtime")
            test_time=dd["localtime"].max()- dd["localtime"].min()
            test_dis=dd["y"].max()- dd["y"].min()
            if (test_time> Minimum_travel_time) & (test_time<Maximum_travel_time)&(test_dis>(Length_of_section-100))&(test_dis<Length_of_section):
                a1 = random.randint(2,(a-1))
                dd1=dd[0:a1]
                tt1=dd1["localtime"].max()- dd1["localtime"].min()
                y1=dd1["y"].max()- dd1["y"].min()
                dd2=dd[a1:a]
                tt2=dd2["localtime"].max()- dd2["localtime"].min()
                y2=dd2["y"].max()- dd2["y"].min()
                return {'localtime':tt1, 'spd':tt2, 'x':y1, 'y':y2}
            else:
                return {'localtime':0, 'spd':0, 'x':0, 'y':0}
        else:
            return {'localtime':0, 'spd':0, 'x':0, 'y':0}

    nv=data2.aggregate(calcu)  #apply calcu funtion on data2 file

    # average travel time at a perticular run of the TCA
    tt3=((nv.sum()[0]+nv.sum()[1])/(nv.sum()[2]+nv.sum()[3])*Length_of_section)

    print i
    tt.append(tt3)

print np.mean(tt)
print np.std(tt)
print np.min(tt)
print np.max(tt)


#write all the travel time in a file
np.savetxt('%s.csv'%filename,tt,delimiter=",",fmt='%10.5f')


## analysis with the result

travel_time_1=[num for num in tt if num >0]

length_tt = len(travel_time_1)


#Mean Absolute Percent Error (MAPE)
MAPE = sum([(abs((x-actual_travel_time)/actual_travel_time)) for x in travel_time_1])/length_tt*100

#Mean Absolute Deviation (MAD) (also known as the mean absolute error)
MAD = sum([(abs(x-actual_travel_time)) for x in travel_time_1])/length_tt

#Root Mean Squared Error (RMSE)
RMSE = math.sqrt(sum([((x-actual_travel_time)**2) for x in travel_time_1])/length_tt)

#The Standard Deviation of Percentage Error (SDPE)
wt = [((x-actual_travel_time)/actual_travel_time)for x in travel_time_1]
s1 = sum([(x**2)for x in wt])
s2 = (np.mean(wt))**2

SDPE = math.sqrt((s1-(length_tt*s2))/(length_tt-1))*100

print "MAPE:"
print MAPE
print "MAD:"
print MAD
print "RMSE:"
print RMSE
print "SDPE:"
print SDPE
