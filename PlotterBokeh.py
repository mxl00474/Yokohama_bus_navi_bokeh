from bokeh.plotting import gmap
from bokeh.models import ColumnDataSource, GMapOptions, Circle, ImageURL
from bokeh.models.tools import PanTool, WheelZoomTool, ResetTool, HoverTool
from bokeh.io import curdoc
from bokeh.layouts import column

import pandas as pd
from pandas.tseries.offsets import BusinessMonthEnd
from BusInfo import BusInfo

class PlotterBokeh():
    session_list = {}

    @staticmethod
    def update():
        doc = curdoc()
        plotter = PlotterBokeh.session_list[doc.session_context]
        plotter.update_buslocation()

    def __init__(self, lat, lng, apiKey, doc=None):

        if doc is None:
            self.doc = curdoc()
        else:
            self.doc = doc

        tools = [PanTool(), WheelZoomTool(), ResetTool()]
        map_options = GMapOptions(lat=lat, lng=lng, map_type="roadmap", zoom=15)
        self.apiKey = apiKey
        self.fig = gmap(self.apiKey, map_options, title="Yokohama Bus Map", tools=tools, height=300)

    def init_buslocation(self, bus_list):

        self.source = ColumnDataSource(bus_list)

        g2 = ImageURL(url="img_url", x="lng", y="lat", anchor='center', angle='azimuth', angle_units='deg') 
        g2_r = self.fig.add_glyph(source_or_glyph=self.source, glyph=g2)

        #g1 = Circle(x="lng", y="lat", size=15, fill_color="color", fill_alpha=0.8)
        g1 = Circle(x="lng", y="lat", size=15, fill_color="color", fill_alpha=0.0, line_alpha=0.0)
        g1_r = self.fig.add_glyph(source_or_glyph=self.source, glyph=g1)

        g1_hover = HoverTool(renderers=[g1_r],
                             tooltips=[('路線', '@route_name'), 
                                       ('前のバス停', '@pole_name_x'), 
                                       ('次のバス停', '@pole_name_y'),
                                       ('混雑度', '@occupancy'),
                                       ]) 
        self.fig.add_tools(g1_hover)
        self.fig.text(x="lng", y="lat", text="route_num", source=self.source)

        #self.fig.triangle(x="azimuth_x", y="azimuth_y", size=7, fill_color="color", fill_alpha=0.8,
        #                  angle="azimuth", source=self.source)

    def update_buslocation(self):

        bus_list = BusInfo.update()        
        self.source.data = bus_list

    def loop(self):
        PlotterBokeh.session_list.setdefault(self.doc.session_context, self)
        self.doc.add_root(column(self.fig, sizing_mode='scale_both'))
        self.doc.add_periodic_callback(PlotterBokeh.update, 10000)
