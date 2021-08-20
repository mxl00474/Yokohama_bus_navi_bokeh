from urllib import request, parse
import pandas as pd
import json
import os

from bokeh.core.validation.decorators import error

class BusInfo:

    url = 'https://api-tokyochallenge.odpt.org/api/v4/odpt:Bus'
    url_busstop = 'https://api-tokyochallenge.odpt.org/api/v4/odpt:BusstopPole.json'
    url_routes = 'https://api-tokyochallenge.odpt.org/api/v4/odpt:BusroutePattern.json'
    
    params = {
            'odpt:operator': 'odpt.Operator:YokohamaMunicipal',
        }

    bus_stops = None
    bus_routes = None

    @staticmethod
    def init():
        
        apiKey = os.getenv('BUS_TOKEN')
        BusInfo.params['acl:consumerKey'] = apiKey

        BusInfo.getBusStops()
        BusInfo.getBusRoutes()

    @staticmethod
    def getBusRoutes():
        
        #BusInfo.bus_routes = pd.DataFrame()
        #return

        busroute_list=[]
        req = request.Request('{}?{}'.format(BusInfo.url_routes, parse.urlencode(BusInfo.params)))
        with request.urlopen(req) as res:
            json_load = json.load(res)    
            for v in json_load:
                try:
                    busstop = { 'route_id': v['owl:sameAs'],
                                'route_name': v['dc:title'],
                                }
                    busroute_list.append(busstop)
                except Exception:
                    pass
        BusInfo.bus_routes = pd.DataFrame(busroute_list).set_index('route_id')

    @staticmethod
    def getBusStops():

        #BusInfo.bus_stops = pd.DataFrame()
        #return

        busstop_list=[]
        req = request.Request('{}?{}'.format(BusInfo.url_busstop, parse.urlencode(BusInfo.params)))
        with request.urlopen(req) as res:
            json_load = json.load(res)    
            for v in json_load:
                try:
                    busstop = { 'busstop_id': v['owl:sameAs'],
                                'pole_name': v['dc:title'],
                                }
                    busstop_list.append(busstop)
                except Exception:
                    pass
        BusInfo.bus_stops = pd.DataFrame(busstop_list).set_index('busstop_id')

    @staticmethod
    def update():
        bus_list=[]
        req = request.Request('{}?{}'.format(BusInfo.url, parse.urlencode(BusInfo.params)))
        with request.urlopen(req) as res:
            json_load = json.load(res)    
            for v in json_load:
                try:

                    if v['odpt:occupancyStatus'] == 'odpt.OccupancyStatus:Empty':
                        occupancy = '空いている'
                        color='blue'
                    elif v['odpt:occupancyStatus'] == 'odpt.OccupancyStatus:ManySeatsAvailable':
                        occupancy = '空き座席多数'
                        color='blue'
                    elif v['odpt:occupancyStatus'] == 'odpt.OccupancyStatus:FewSeatsAvailable':
                        occupancy = '座席わすか'
                        color='yellow'
                    elif v['odpt:occupancyStatus'] == 'odpt.OccupancyStatus:StandingRoomOnly':
                        occupancy = '混雑'
                        color='red'
                    else:
                        color='gray'

                    bus = { 'bus_id': v['odpt:busNumber'],
                            'lat': v['geo:lat'],
                            'lng': v['geo:long'],
                            'route_num': v['odpt:busroute'][-3:],
                            'route_id': v['odpt:busroutePattern'],
                            'prevStop': v['odpt:fromBusstopPole'],
                            'nextStop': v['odpt:toBusstopPole'],
                            'occupancy' : occupancy,
                            'color' : color,
                            'azimuth' : 360-v['odpt:azimuth'],
                            'img_url' : 'https://mxl00474.github.io/test_static/arrow_' + color + '.png'
                            }
                    bus_list.append(bus)
                except Exception:
                    pass
        df = pd.DataFrame(bus_list).set_index('bus_id')
        df = pd.merge(df, BusInfo.bus_stops, left_on='prevStop', right_index=True, how='left')
        df = pd.merge(df, BusInfo.bus_stops, left_on='nextStop', right_index=True, how='left')
        df = pd.merge(df, BusInfo.bus_routes, left_on='route_id', right_index=True, how='left')
        return df

if __name__ == '__main__':

    BusInfo.init()

    print('=== Get stop info ===')
    BusInfo.getBusStops()
    print(BusInfo.bus_stops)

    print('=== Get route info ===')
    BusInfo.getBusRoutes()
    #print(BusInfo.bus_routes)
    print(len(BusInfo.bus_routes))

    print('=== Get bus info ===')
    bus_list = BusInfo.update()
    print(bus_list)
    print(bus_list.columns)

