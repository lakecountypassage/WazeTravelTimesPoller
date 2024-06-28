#!/usr/bin/env
import datetime
import json
import logging
import sys
import urllib.request

# need to use Python3

waze_url = ["https://www.waze.com/rtserver/broadcast/BroadcastRSS?buid={id}&format=JSON"]


class Waze:

    def __init__(self):
        # json that is being read in
        self.json_before = {}
        self.counter = 0
        self.colorCounter = 1
        self.date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # json objects
        self.main_dict = {}
        self.features_list = []
        self.geometry = {}
        self.feature = {}

    def download(self, feed_url):
        try:
            r = urllib.request.urlopen(feed_url, timeout=5).read().decode('utf-8')

            if r.status_code == 200:
                self.json_before = r.json()
            else:
                raise Exception('Waze website it currently unreachable')

        except Exception as e:
            logging.exception(e)
            sys.exit()

    def create_coords(self):
        # parse out only routes
        routes = self.json_before['routes']

        for route in routes:
            if route["type"] == "DYNAMIC":
                pass

            self.counter += 1
            # self.geometry = []

            lines = route['line']
            coords = []

            for line in lines:
                coordinates = [line['x'], line['y']]
                coords.append(coordinates)

            self.geometry = coords
            self.create_features()

    def create_features(self):
        self.feature = {"geometry": {"paths": [self.geometry], "spatialReference": {"wkid": 4326}},
                        "attributes": {"ColorCode": self.colorCounter, "Updated": str(self.date_time)}}
        self.features_list.append(self.feature)
        self.colorCounter = self.colorCounter + 1
        if self.colorCounter > 20:
            self.colorCounter = 1

    def build_main(self):
        # self.main_dict["type"] = "FeatureCollection"
        self.main_dict["routeCount"] = int(self.counter)
        self.main_dict["date"] = str(self.date_time)
        self.main_dict["geometryType"] = "esriGeometryPolyline"
        self.main_dict["spatialReference"] = {"wkid": 4326}
        self.main_dict["fields"] = [{"name": "OBJECTID", "type": "esriFieldTypeOID"},
                                    {"name": "ColorCode", "type": "esriFieldTypeSmallInteger"},
                                    {"name": "Updated", "type": "esriFieldTypeString"}]
        self.main_dict["features"] = self.features_list

    def dump_json(self):
        with open('generated_map.json', 'w') as f:
            f.write(json.dumps(self.main_dict, indent=1))


if __name__ == "__main__":

    # logging.debug("------------------ Start ------------------")
    # logging.debug(waze_url)

    w = Waze()
    for url in waze_url:
        w.download(url)
        w.create_coords()
    w.build_main()
    w.dump_json()

    # logging.debug("------------------ End --------------------")
