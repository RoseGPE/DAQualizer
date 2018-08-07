import plotly.offline as py
from plotly import tools
import plotly.graph_objs as go
import plotly.figure_factory as FF

import numpy as np
import pandas as pd

df_merged = pd.read_csv('merged.csv')
# df_car = pd.read_csv('test.csv')
# df_ecu = pd.read_csv('5-27-airport_024.csv')

def filterValue(frame, data, offset):
    return list(zip(*[(x + offset,y) for x, y in zip(frame['Time (sec)'], frame[data])
        if not np.isnan(y)
        ]))

def filterTransformValue(frame, data, beg, end, offset):
    return list(zip(*[(x+offset,y) for x, y in zip(frame['Time (sec)'], frame[data])
        if x + offset> beg and x + offset < end
        and x+offset > 0]))

rpm_car = filterValue(df_merged, 'rpm', 0)
speed_car = filterValue(df_merged, 'speed', 0)

# rpm_ecu = filterTransformValue(df_ecu, 'RPM', 0, 100, 0)
# tps_ecu = filterTransformValue(df_ecu, 'TPS (%)', 0, 100, 0)

rpm_ecu = filterValue(df_merged, 'RPM', 0)
tps_ecu = filterValue(df_merged, 'TPS (%)', 0)

fig = tools.make_subplots(rows=3, cols=1, shared_xaxes=True)

fig.append_trace(
    go.Scatter(
        x=rpm_car[0],
        y=rpm_car[1],
        name='rpm-car'
    ), 1, 1
)
fig.append_trace(
    go.Scatter(
        x=rpm_ecu[0],
        y=rpm_ecu[1],
        name='rpm-ecu'
    ), 1, 1
)
fig.append_trace(
    go.Scatter(
        x=speed_car[0],
        y=speed_car[1],
        name='speed'
    ), 1, 1
)

fig.append_trace(
    go.Scatter(
        x=tps_ecu[0],
        y=tps_ecu[1],
        name='tps-ecu'
    ), 2, 1
)

fig.append_trace(
    go.Scatter(
        x=speed_car[0],
        y=speed_car[1],
        name='speed'
    ), 3, 1
)

print(fig['layout'])

fig['layout']['yaxis1'].update(title='RPM')
fig['layout']['yaxis2'].update(title='TPS')
fig['layout']['yaxis3'].update(title='Speed')
fig['data'][2].update(yaxis='y4')
fig['layout']['yaxis4'] =dict(
    autorange=True,
    overlaying= 'y1',
    side='right',
    title='Speed (MPH)'
)


py.plot(fig, filename='ecutest')
