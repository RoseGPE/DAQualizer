import dataparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate
from scipy import signal

out = dataparse.can_to_csv('first-run.tsv', 'tmp.csv')
start,crank,tps,rpm,boost,speed,shiftup,shiftdown,rearws,clutch,brake,batt,coolt,curr,pdmeFlags,pdmaFlags,ratio, che_curr, cha_curr, che, cha = out
# NOTE: SPEED IS IN MPH

x = integrate.cumtrapz(speed[1], speed[0], initial=0)
tx = speed[0]

fig, axes = plt.subplots(nrows=3, ncols=1)

axes[0].plot(np.interp(speed[0],tx,x), speed[1])
axes[0].plot(np.interp(rearws[0],tx,x), rearws[1])
axes[0].set_ylabel('Velocity (MPH)')

axes[1].plot(np.interp(tps[0],tx,x), tps[1], color='g')
brkax = axes[1].twinx()
brkax.plot(np.interp(brake[0],tx,x), brake[1], color='r')

axes[1].tick_params('y', colors='g')
axes[1].set_ylim(0,100)
axes[1].set_ylabel('TPS %')
brkax.tick_params('y', colors='r')
brkax.set_ylim(0,5000)
brkax.set_ylabel('Brake Pressure')

# axes[2].plot(ratio[0], ratio[1])
crange = (0,5000) #(min(clutch[1]), max(clutch[1]))

clutchax = axes[2].twinx()

gear_cutoffs = np.array([1.0/2.168,1.0/1.741,1.0/1.4195,1.0/1.1635]) / 2.81 * (18*0.0029744599) / (30.0/13.0)
print(gear_cutoffs)

ratio_filtered = np.array(ratio[1])
ratio_filtered[ratio_filtered > max(gear_cutoffs)*1.25] = 0.0
ratio_filtered = signal.savgol_filter(ratio_filtered, 31, 1)

# print(ratio[1])
gears = []
for r in ratio_filtered:
	for i, gc in enumerate(gear_cutoffs):
		if r < gc:
			gears.append(i+1)
			break
	else:
		gears.append(len(gear_cutoffs)+1)

for i, s in enumerate(shiftup[1]):
	if s > 0:
		xp = np.interp(shiftup[0][i],tx,x)
		axes[2].plot([xp,xp], [0, len(gear_cutoffs)+1], color='g')

for i, s in enumerate(shiftdown[1]):
	if s > 0:
		xp = np.interp(shiftdown[0][i],tx,x)
		axes[2].plot([xp,xp], [0, len(gear_cutoffs)+1], color='r')


# axes[2].plot(np.interp(ratio[0],tx,x),   ratio[1])
# axes[2].plot(np.interp(ratio[0],tx,x),   ratio_filtered)
axes[2].plot(np.interp(ratio[0],tx,x),   gears)
clutchax.plot(np.interp(clutch[0],tx,x), clutch[1])
clutchax.set_ylim(crange)

axes[2].tick_params('y', colors='g')
axes[2].set_ylabel('Gear')
clutchax.tick_params('y', colors='r')
clutchax.set_ylim(crange)
clutchax.set_ylabel('Clutch Engagement')

plt.show()