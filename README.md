# DAQualizer

Hey this is a bit of a hot mess! Here's what this does.

1. dataparse.py: translates CAN messages (in a tab-separated value format) to CSV channels
2. combine.py: merges the CSV CAN channels with ECU CAN channels (prior to this, you need to 'synchronize' the ECU and CAN channels)
3. merged_plot.py: plots the data
