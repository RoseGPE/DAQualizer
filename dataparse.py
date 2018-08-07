import argparse
# import matplotlib.pyplot as plt
# from matplotlib import gridspec
import csv

def can_to_csv(f_name, csvfile_name):
    timestamp = 0.0

    fieldnames = [
        "time", "start", "stop", "crank", "tps", "rpm", "speed", "fl", "fr", "rl", "rr", "map", "shiftup", "shiftdown", "brake", "clutch", "coolt", "oilt", "batt", "curr",
        "ch1e", "ch2e", "ch3e", "ch4e", "ch5e", "ch6e", "ch7e", "ch8e",
        "ch1a", "ch2a", "ch3a", "ch4a", "ch5a", "ch6a", "ch7a", "ch8a",
        "ch1e_curr", "ch2e_curr", "ch3e_curr", "ch4e_curr", "ch5e_curr", "ch6e_curr", "ch7e_curr", "ch8e_curr",
        "ch1a_curr", "ch2a_curr", "ch3a_curr", "ch4a_curr", "ch5a_curr", "ch6a_curr", "ch7a_curr", "ch8a_curr",
    ]

    start = ([], [])
    crank = ([], [])
    tps = ([], [])
    rpm = ([], [])
    boost = ([], [])
    speed = ([], [])
    shiftup = ([], [])
    shiftdown = ([], [])
    rearws = ([], [])
    clutch = ([], [])
    brake = ([], [])
    batt = ([], [])
    coolt = ([], [])
    curr = ([], [])
    pdmeFlags = ([], [])
    pdmaFlags = ([], [])
    ratio = ([], [])

    che_curr = (([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []))
    cha_curr = (([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []))

    che = (([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []))
    cha = (([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []), ([], []))

    lastws = 0.0
    lastspeed = 0.0
    lastrpm = 0.0
    lastcurrents = [0, 0, 0, 0]
    avgTPS = []
    avgBoost = []
    avgCurr = []
    
    with open(f_name) as f:
        with open(csvfile_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            row = {}
            lasttime = None
            for line in f:
                data = [c for c in line.strip().split('\t')]
                timestamp = int(data[0]) / 1000.0
                row["time"] = timestamp
                data = data[1:]
                data = [int(s, 16) for s in data]
                if(data[0] == 0x500):
                    # if(len(row) > 0):
                    #     if("curr" in row.keys()):
                    #         curr[0].append(timestamp)
                    #         curr[1].append(row["curr"])
                    #     writer.writerow(row)
                    #     row = {}
                    # timestamp = timestamp + 0.01
                    # row["time"] = timestamp
                    row["start"] = int(data[1] & (1 << 6) > 0)
                    row["stop"] = int(data[1] & (1 << 5) > 0)
                    start[0].append(timestamp)
                    start[1].append(row["start"])
                elif(data[0] == 0x504):
                    row["shiftup"] = int(data[1] & (1 << 0) > 0)
                    row["shiftdown"] = int(data[1] & (1 << 1) > 0)
                    shiftup[0].append(timestamp)
                    shiftup[1].append(row["shiftup"])

                    shiftdown[0].append(timestamp)
                    shiftdown[1].append(row["shiftdown"])
                elif(data[0] == 0x508):
                    row["rpm"] = data[1] | (data[2] << 8)
                    if(row["rpm"] >= 0xFFFF):
                        row["rpm"] = 0
                    if(len(rpm[0]) > 0 and row["rpm"] != 0):
                        lasttime = 0.0
                        if(len(ratio[0]) > 0):
                            lastime = ratio[0][-1]
                        if(timestamp > lasttime):
                            ratio[0].append(timestamp)
                            ratio[1].append(lastws/row["rpm"])
                        elif(timestamp == lasttime):
                            ratio[1][-1] = lastws/row["rpm"]
                    row["tps"] = (data[3] | (data[4] << 8))/10.0
                    if(lastspeed > 1.0 and lastrpm > 1000):
                        avgTPS.append(row["tps"])
                    lastrpm = row["rpm"]
                    rpm[0].append(timestamp)
                    rpm[1].append(row["rpm"])
                    tps[0].append(timestamp)
                    tps[1].append(row["tps"])
                elif(data[0] == 0x509):
                    row["map"] = (data[1] | (data[2] << 8)) / 100.0
                    if(lastspeed > 1.0 and lastrpm > 1000):
                        avgBoost.append(row["map"])
                    boost[0].append(timestamp)
                    boost[1].append(row["map"])
                elif(data[0] == 0x50C):
                    row["brake"] = data[1] | (data[2] << 8)
                    brake[0].append(timestamp)
                    brake[1].append(row["brake"])
                elif(data[0] == 0x510):
                    row["clutch"] = data[1] | (data[2] << 8)
                    clutch[0].append(timestamp)
                    clutch[1].append(row["clutch"])

                elif(data[0] == 0x520):
                    row["crank"] = int((data[5] & 0x01) == 0)
                    for i in range(8):
                        che[i][0].append(timestamp)
                        che[i][1].append(int((data[i+1] & 0x01) == 0))
                        row['ch{}e'.format(i+1)] = int((data[i+1] & 0x01) == 0)
                    crank[0].append(timestamp)
                    crank[1].append(row["crank"])
                elif(data[0] == 0x524):
                    for i in range(8):
                        cha[i][0].append(timestamp)
                        cha[i][1].append(int((data[i+1] & 0x01) == 0))
                        row['ch{}a'.format(i+1)] = int((data[i+1] & 0x01) == 0)
                elif(data[0] == 0x512):
                    row["fl"] = data[1] | (data[2] << 8)
                    row["fr"] = data[3] | (data[4] << 8)
                    row["speed"] = ((row["fl"] + row["fr"]) / 2)*(18*0.0029744599)
                    lastspeed = row["speed"]
                    speed[0].append(timestamp)
                    speed[1].append(row["speed"])
                    lastws = (row["fl"] + row["fr"]) / 2
                elif(data[0] == 0x513):
                    row["rl"] = data[1] | (data[2] << 8)
                    row["rr"] = data[3] | (data[4] << 8)
                    lastws = ((row["rl"] + row["rr"]) / 2) * (18*0.0029744599)
                    rearws[0].append(timestamp)
                    rearws[1].append(lastws)
                    if(len(rpm[0]) > 0 and rpm[1][-1] != 0):
                        lasttime = 0.0
                        if(len(ratio[0]) > 0):
                            lasttime = ratio[0][-1]
                        if(lasttime != timestamp):
                            ratio[0].append(timestamp)
                            ratio[1].append(lastws/rpm[1][-1])
                        elif(timestamp > lasttime):
                            ratio[1][-1] = lastws/rpm[1][-1]
                elif(data[0] == 0x534):
                    row["batt"] = (data[1] | (data[2] << 8)) * 5.0*(1.0/4096.0)*(12.4/2.4)
                    batt[0].append(timestamp)
                    batt[1].append(row["batt"])
                elif(data[0] == 0x538):
                    if(len(data) > 7):
                        row["coolt"] = (data[5] | (data[6] << 8))/10.0
                        coolt[0].append(timestamp)
                        coolt[1].append(row["coolt"])
                elif(data[0] in [0x540, 0x544, 0x548, 0x54c]):
                    currents = [0.0, 0.0, 0.0, 0.0]
                    chan = 0
                    for i in range(2):
                        currents[chan] = (data[3*i + 1] | ((data[3*i + 2] & 0x0F) << 8))*10.0*5.0*(1.0/4096.0)
                        if(currents[chan] >= 49):
                            currents[chan] = 0
                        chan = chan + 1
                        currents[chan] = ((data[3*i + 2] >> 4) | (data[3*i + 3] << 4))*10.0*5.0*(1.0/4096.0)
                        if(currents[chan] >= 49):
                            currents[chan] = 0
                        chan = chan + 1
                    if(data[0] == 0x540):
                        for i in range(4):
                            row["ch{}e_curr".format(i+1)] = currents[i]
                            che_curr[i][0].append(timestamp)
                            che_curr[i][1].append(currents[i])
                    elif(data[0] == 0x544):
                        for i in range(4):
                            row["ch{}e_curr".format(i+5)] = currents[i]
                            che_curr[i+4][0].append(timestamp)
                            che_curr[i+4][1].append(currents[i])
                    elif(data[0] == 0x548):
                        for i in range(4):
                            row["ch{}a_curr".format(i+1)] = currents[i]
                            cha_curr[i][0].append(timestamp)
                            cha_curr[i][1].append(currents[i])
                    elif(data[0] == 0x54C):
                        for i in range(4):
                            row["ch{}a_curr".format(i+5)] = currents[i]
                            cha_curr[i+4][0].append(timestamp)
                            cha_curr[i+4][1].append(currents[i])

                    lastcurrents[[0x540, 0x544, 0x548, 0x54c].index(data[0])] = sum(currents)
                    row["curr"] = sum(lastcurrents)
                elif(data[0] == 0x550):
                    pdmeFlags[0].append(timestamp)
                    pdmeFlags[1].append(data[4])
                elif(data[0] == 0x554):
                    pdmaFlags[0].append(timestamp)
                    pdmaFlags[1].append(data[4])
                
                if(len(row) > 0 and (timestamp is not lasttime)):
                    if("curr" in row.keys()):
                        curr[0].append(timestamp)
                        curr[1].append(row["curr"])
                    writer.writerow(row)
                    row = {}
                    lasttime = timestamp

    return start,crank,tps,rpm,boost,speed,shiftup,shiftdown,rearws,clutch,brake,batt,coolt,curr,pdmeFlags,pdmaFlags,ratio, che_curr, cha_curr, che, cha


            # fig = plt.figure(0)
            # fig.text(0.5, 0.04, 'Time(s)', ha='center', va='center')
            # gs = gridspec.GridSpec(7, 1, height_ratios=[3, 1, 1, 3, 3, 2, 2])

            # ax0 = plt.subplot(gs[0])
            # ax0.set_ylabel('batt (V)')
            # ax01 = ax0.twinx()
            # ax01.set_ylabel('curr (A)')
            # line0, = ax0.plot(batt[0], batt[1], color='r', label='batt')
            # line01, = ax01.plot(curr[0], curr[1], color='b', label='curr')
            # ax0.legend((line0, line01), ('batt', 'curr'))

            # ax1 = plt.subplot(gs[1], sharex=ax0)
            # ax1.set_ylabel('shift')
            # line10, = ax1.plot(shiftup[0], shiftup[1], color='r', label="shiftup")
            # line11, = ax1.plot(shiftdown[0], shiftdown[1], color='b', label="shiftdown")
            # line12, = ax1.plot(crank[0], crank[1], color='g', linestyle='--', label="crank")
            # line13, = ax1.plot(start[0], start[1], color='y', label='start')
            # ax1.legend()

            # ax2 = plt.subplot(gs[2], sharex=ax0)
            # ax2.set_ylabel('clutch')
            # ax21 = ax2.twinx()
            # ax21.set_ylabel('brake')
            # line2, = ax2.plot(clutch[0], clutch[1], color='b')
            # line21, = ax21.plot(brake[0], brake[1], color='r')
            # ax2.legend((line2, line21), ('clutch', 'brake'))
            # plt.setp(ax0.get_xticklabels(), visible=False)

            # ax3 = plt.subplot(gs[3], sharex=ax0)
            # ax3.set_ylabel("tps %")
            # line3, = ax3.plot(tps[0], tps[1], color='r')
            # plt.setp(ax0.get_xticklabels(), visible=False)

            # ax4 = plt.subplot(gs[4], sharex=ax0)
            # ax41 = ax4.twinx()
            # ax4.set_ylabel('rpm')
            # ax41.set_ylabel('speed')
            # line4, = ax4.plot(rpm[0], rpm[1], color='g', label='RPM')
            # line41, = ax41.plot(rearws[0], rearws[1], color='b', label="WS")
            # ax4.legend((line4, line41), ('RPM', 'WS'))
            # plt.setp(ax0.get_xticklabels(), visible=False)

            # ax5 = plt.subplot(gs[5], sharex=ax0)
            # ax5.set_ylabel("map")
            # line5, = ax5.plot(boost[0], boost[1], color='y')
            # plt.setp(ax0.get_xticklabels(), visible=False)

            # # ax6 = plt.subplot(gs[6], sharex=ax0)
            # # ax6.set_ylabel('coolt (F)')
            # # line6, = ax6.plot(coolt[0], coolt[1], color='y')
            # # plt.setp(ax0.get_xticklabels(), visible=False)

            # ax7 = plt.subplot(gs[6], sharex=ax0)
            # ax7.set_ylabel('ratio')
            # line7, = ax7.plot(ratio[0], ratio[1], color='r')
            # plt.setp(ax0.get_xticklabels(), visible=False)

            # plt.subplots_adjust(hspace=.0)
            

            # fig1 = plt.figure(1)
            # fig1.text(0.5, 0.04, 'Time(s)', ha='center', va='center')
            # gs = gridspec.GridSpec(8, 2, height_ratios=[1, 1, 1, 1, 1, 1, 1, 1])

            # chane = ("SPK/INJ", "N/A", "FUEL", "RAD", "STRT", "COOL", "BYP", "BST")
            # chana =("ECU", "SHIFT", "O2", "ARB", "INTC", "CLCH", "OIL", "N/A")
            # ax0 = plt.subplot(gs[0])
            # ax0.set_ylabel(chane[0])
            # ax0.set_ylim([-0.1, 1.1])
            # ax01 = ax0.twinx()
            # ax01.set_ylabel('CURR')
            # line, = ax0.plot(che[0][0], che[0][1])
            # line, = ax01.plot(che_curr[0][0], che_curr[0][1], color='r')
            # plt.setp(ax0.get_xticklabels(), visible=False)

            # for i in range(7):
            #     ax = plt.subplot(gs[2*i+2], sharex=ax0)
            #     ax.set_ylabel(chane[i+1])
            #     ax.set_ylim([-0.1, 1.1])
            #     axx = ax.twinx()
            #     axx.set_ylabel('CURR')
            #     line, = ax.plot(che[i+1][0], che[i+1][1])
            #     linee, = axx.plot(che_curr[i+1][0], che_curr[i+1][1], color='r')
            #     plt.setp(ax.get_xticklabels(), visible=False)

            # ax0 = plt.subplot(gs[1])
            # ax0.set_ylabel(chana[0])
            # ax0.set_ylim([-0.1, 1.1])
            # ax01 = ax0.twinx()
            # ax01.set_ylabel('CURR')
            # line, = ax0.plot(cha[0][0], cha[0][1])
            # line, = ax0.plot(cha_curr[0][0], cha_curr[0][1], color='r')

            # for i in range(7):
            #     ax = plt.subplot(gs[2*i+3], sharex=ax0)
            #     ax.set_ylabel(chana[i+1])
            #     ax.set_ylim([-0.1, 1.1])
            #     axx = ax.twinx()
            #     axx.set_ylabel('CURR')
            #     line, = ax.plot(cha[i+1][0], cha[i+1][1])
            #     line, = axx.plot(cha_curr[i+1][0], cha_curr[i+1][1], color='r')
            #     plt.setp(ax.get_xticklabels(), visible=False)

            # plt.setp(ax0.get_xticklabels(), visible=False)
            # plt.subplots_adjust(hspace=0.25)

            # plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fin", help="path to file containing CAN messages")
    parser.add_argument("fout", help="path to destination CSV file")
    args = parser.parse_args()
    out = can_to_csv(args.fin, args.fout)