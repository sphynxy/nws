import json
import urllib.request
from datetime import datetime
from dateutil.tz import tzutc, tzlocal

# very very wip

class NWS:
    __doc__ = '''National Weather Service (weather.gov) API'''

    grid_point = "https://api.weather.gov/gridpoints/FWD/71,102"

    temperature = 0
    dew_point = 0
    humidity = 0
    wind_chill = 0
    wind_speed = 0
    wind_direction = 0

    def __init__(self):

        print("Connecting to website...")

        with urllib.request.urlopen(self.grid_point) as url:
            self.__data = json.loads(url.read().decode())

        self.uom = self.__data["properties"]["temperature"]["uom"]

        NWS.temperature = self.get("temperature")
        NWS.dew_point = self.get("dewpoint")
        NWS.humidity = self.get("relativeHumidity")
        NWS.wind_chill = self.get("windChill")
        NWS.wind_speed = self.get("windSpeed")
        NWS.wind_direction = self.get("windDirection")

    def forecast(self, sec=0, additional_info=False):

        print("Connecting to website...")

        with urllib.request.urlopen(self.grid_point + "/forecast") as url:
            __forecast_data = json.loads(url.read().decode())

        forecast = str(__forecast_data["properties"]["periods"][sec]["name"] + "|"
                       + __forecast_data["properties"]["periods"][sec]["detailedForecast"])

        if not additional_info:
            return forecast

        if additional_info:
            return forecast + " Elevation: " + str(__forecast_data["properties"]["elevation"]["value"])
            # Add more stuff...

    def update(self):
        self.__init__()

    def get(self, uri, future=0, include_future=False):

        # Gets data from the grid points JSON file

        time = self.__round_time()

        loop = 0
        index = 0

        valid_times = []

        for value in self.__data["properties"][uri]["values"]:

            if time in value["validTime"]:

                print("Exact time found for:", uri)

                if future == 0:
                    return value["value"]

            loop += 1

            if loop == len(value["validTime"]) - 1:

                for closest in self.__data["properties"][uri]["values"]:

                    if time.split("T")[0] in closest["validTime"].split("T")[0]:
                        valid_times.append([closest["validTime"].split("T")[1].split(":")[0],
                                           closest["value"], index])  # Add validTime hour to list

                    index += 1

                hour = int(time.split("T")[1].split(":")[0])

                try:

                    if future == 0:

                        if include_future:

                            return self.__data["properties"][uri]["values"][min(valid_times,
                                                                                key=lambda x: abs(int(x[0]) - hour))[2]
                                                                            + future]

                        else:

                            return self.__data["properties"][uri]["values"][min(valid_times,
                                                                                key=lambda x: abs(int(x[0]) - hour))[2]
                                                                            + future]["value"]

                    if future > 0:

                        if include_future:

                            return self.__data["properties"][uri]["values"][min(valid_times,
                                                                                key=lambda x: abs(int(x[0]) - hour))[2]
                                                                            + future]

                        else:

                            return self.__data["properties"][uri]["values"][min(valid_times,
                                                                                key=lambda x: abs(int(x[0]) - hour))[2]
                                                                            + future]["value"]

                except ValueError:
                    print("Null value encountered.")
                    break

    @staticmethod
    def __round_time():

        # Rounds UTC time to nearest hour, returns string in ISO-8601 format.

        d = datetime.utcnow()

        if d.minute > 30:

            return "{year}-{month:02}-{day:02}T{hour:02}:00:00+00:00".format(year=d.year, month=d.month,
                                                                             day=d.day, hour=d.hour + 1)
        else:
            return "{year}-{month:02}-{day:02}T{hour:02}:00:00+00:00".format(year=d.year, month=d.month,
                                                                             day=d.day, hour=d.hour)

    @staticmethod
    def convert_time(iso_time, simple=True):
        # example time 2020-02-10T03:00:00+00:00/PT3H
        year = iso_time.split("-")[0]
        mm = iso_time.split("-")[1]
        dd = iso_time.split("-")[2].split("T")[0]
        h = iso_time.split("T")[1].split(":")[0]
        m = iso_time.split("T")[1].split(":")[1]

        if simple:
            return str(datetime(int(year), int(mm), int(dd),
                                int(h), int(m), 0, 0, tzinfo=tzutc()).astimezone(tzlocal())).split('-')[1:-1][1][:-3]
        else:
            return datetime(int(year), int(mm), int(dd), int(h), int(m), 0, 0, tzinfo=tzutc()).astimezone(tzlocal())

    @staticmethod
    def c_to_f(t):

        if t is not None:
            return (9.0 / 5.0 * t) + 32
