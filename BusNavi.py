import os
from PlotterBokeh import PlotterBokeh
from BusInfo import BusInfo
from bokeh.plotting import curdoc
from bokeh.layouts import column

BusInfo.init()

# Set the initial location as Yokohama station
lat=35.46591430126525
lng=139.62125644093177

apiKey = os.getenv('GMAP_TOKEN')

plotter = PlotterBokeh(lat, lng, apiKey)
bus_list = BusInfo.update()
plotter.init_buslocation(bus_list)
plotter.loop()
