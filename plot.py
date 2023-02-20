import matplotlib.pyplot as plt
import numpy as np

x = [16,64,128,256,384,512,768,1024,1280,1536,2048,2560,3072,3584,3968]
y1 = [
    0.03170967102050781,
    0.3237724304199219,
    1.3420581817626953,
    4.3354034423828125,
    9.938955307006836,
    18.713712692260742,
    41.92185401916504,
    74.39589500427246,
    118.67213249206543,
    171.5564727783203,
    307.25812911987305,
    484.9972724914551,
    706.2840461730957,
    958.2674503326416,
    1191.0982131958008
]

y2 = [
    0.07915496826171875,
    0.8285045623779297,
    2.9633045196533203,
    10.118722915649414,
    20.600557327270508,
    37.529945373535156,
    83.86611938476562,
    148.32162857055664,
    224.84564781188965,
    336.6811275482178,
    601.140022277832,
    911.1447334289551,
    1289.7076606750488,
    1777.8403759002686,
    2258.2690715789795,
]

z1 = [
    12208,
    12572,
    12620,
    13056,
    13904,
    13776,
    13228,
    15104,
    16648,
    17616,
    22124,
    23680,
    26580,
    26052,
    28700,
]

z2 = [
    12840,
    12780,
    12868,
    13236,
    13252,
    13292,
    13284,
    13316,
    13152,
    13268,
    13416,
    13496,
    13336,
    13876,
    13844,
]

# CPU
plt.plot(x,y1,"s-",color = 'r',label = "time (basic solution)")
plt.plot(x,y2,"o-",color = 'g',label = "time (efficient solution)")
plt.title('CPU time vs problem size',fontsize= 30,fontweight='bold') 
my_x_ticks = np.array(x)
plt.xticks(my_x_ticks)
plt.xlabel("problem size (m+n)")
plt.ylabel("CPU time (milliseconds)")
plt.legend(loc = "best")

# MEMORY
# plt.plot(x,z1,"s-",color = 'r',label = "memory (basic solution)")
# plt.plot(x,z2,"o-",color = 'g',label = "memory (efficient solution)")
# plt.title('Memory usage vs problem size',fontsize= 30,fontweight='bold') 
# my_x_ticks = np.array(x)
# plt.xticks(my_x_ticks)
# plt.xlabel("problem size (m+n)")
# plt.ylabel("memory (KB)")
# plt.legend(loc = "best")

plt.show()
