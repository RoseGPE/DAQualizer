import plotly.offline as py
from plotly import tools
import plotly.graph_objs as go
import plotly.figure_factory as FF

import numpy as np
import pandas as pd

df_car = pd.read_csv('test.csv')
df_ecu = pd.read_csv('test_022.csv')

def filterValue(frame, data, offset):
    return list(zip(*[(x + offset,y) for x, y in zip(frame['time'], frame[data])
        if not np.isnan(y) and x > 1000.0
        ]))

def filterTransformValue(frame, data, beg, end, offset):
    return list(zip(*[(x+offset,y) for x, y in zip(frame['Time (sec)'], frame[data])
        if x > beg and x < end
        and x > 0]))

rpm_car = filterValue(df_car, 'rpm', 0)
tps_car = filterValue(df_car, 'tps', 0)
speed_car = filterValue(df_car, 'speed', 0)

rpm_ecu = filterTransformValue(df_ecu, 'RPM', 0, 200, 1039.47)
tps_ecu = filterTransformValue(df_ecu, 'TPS (%)', 0, 200, 1039.47)

rpmTrace = go.Scatter(
    x=rpm_car[0],
    y=rpm_car[1],
    name='rpm-car'
)

tpsTrace = go.Scatter(
    x=tps_car[0],
    y=tps_car[1],
    name='tps-car'
)

fig = tools.make_subplots(rows=3, cols=1, shared_xaxes=True)
fig.append_trace(rpmTrace, 1, 1)
fig.append_trace(
    go.Scatter(
        x=rpm_ecu[0],
        y=rpm_ecu[1],
        name='rpm-ecu'
    ), 1, 1
)
fig.append_trace(tpsTrace, 2, 1)
fig.append_trace(
    go.Scatter(
        x=tps_ecu[0],
        y=tps_ecu[1],
        name='tps-car'
    ), 2, 1
)

fig.append_trace(
    go.Scatter(
        x=speed_car[0],
        y=speed_car[1],
        name='speed'
    ), 3, 1
)

fig['layout']['yaxis1'].update(title='RPM')
fig['layout']['yaxis2'].update(title='TPS')
fig['layout']['yaxis3'].update(title='Speed')

# data = [rpmTrace, speedTrace]
# layout = go.Layout(
#     title='RPM and Speed',
#     yaxis=dict(
#         title='RPM'
#     ),
#     yaxis2=dict(
#         title='Speed',
#         titlefont=dict(
#             color='rgb(148, 103, 189)'
#         ),
#         tickfont=dict(
#             color='rgb(148, 103, 189)'
#         ),
#         overlaying='y',
#         side='right'
#     )
# )
# fig = go.Figure(data=data, layout=layout)


py.plot(fig, filename='ecutest')
