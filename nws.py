import json
import urllib.request
from datetime import datetime
from dateutil.tz import tzutc, tzlocal
import xml.etree.ElementTree as eT


def round_time():
    # Rounds UTC time to nearest hour, returns string in ISO-8601 format.
    d = datetime.utcnow()

    if d.minute > 30:
        return "{year}-{month:02}-{day:02}T{hour:02}:00:00+00:00".format(year=d.year, month=d.month,
                                                                         day=d.day, hour=d.hour + 1)
    else:
        return "{year}-{month:02}-{day:02}T{hour:02}:00:00+00:00".format(year=d.year, month=d.month,
                                                                         day=d.day, hour=d.hour)


def convert_time(iso_time, simple=True):
    # Converts UTC-0 time to local time, in ISO-8601 format.
    year = iso_time.split("-")[0]
    mm = iso_time.split("-")[1]
    dd = iso_time.split("-")[2].split("T")[0]
    h = iso_time.split("T")[1].split(":")[0]
    m = iso_time.split("T")[1].split(":")[1]

    if simple:
        return str(datetime(int(year), int(mm), int(dd),
                            int(h), int(m), 0, 0, tzinfo=tzutc()).astimezone(tzlocal()))
    else:
        return datetime(int(year), int(mm), int(dd), int(h), int(m), 0, 0, tzinfo=tzutc()).astimezone(tzlocal())


class NWS:
    """
    National Weather Service (weather.gov) API
    
    DO NOT access these servers with programs/scripts that are:

        too repetitive a login over time ( know frequency data changes ), 
        opening up multiple sessions to access the same data products  
        using the FTP "ls" (list command) during each returning session  
        as they will significantly reduce server response for everyone and severely impact 
        the access by all users. DO NOT DO THIS!  -- weather.gov
    
    :param coordinates: Coordinates of desired location data.
    :param _v: Prints information if true.
    """

    def __init__(self, coordinates, _v=False):

        self.coordinates = coordinates

        if _v:
            print("Connecting to website...")

        self.grid_coord = "https://api.weather.gov/points/{lat},{long}".format(
            lat=coordinates[0],
            long=coordinates[1])

        self.__data = self.load(self.grid_coord)

        self.grid_point = self.__data["properties"]["forecastGridData"]

        self.__data = self.load(self.grid_point)

        if _v:
            print("Acquired grid point.")

        self.uom = self.__data["properties"]["temperature"]["uom"]

    def forecast(self, sec=0, additional_info=False):
        """
        Forecast

        :param sec: How many sections in to the future
        :param additional_info: Includes additional info in forecast. Useless right now.

        :returns: Forecast string, written by NWS.
        """

        with urllib.request.urlopen(self.grid_point + "/forecast") as url:
            __forecast_data = json.loads(url.read().decode())

        forecast = str(__forecast_data["properties"]["periods"][sec]["name"] + "|"
                       + __forecast_data["properties"]["periods"][sec]["detailedForecast"])

        if not additional_info:
            return forecast

        if additional_info:
            return forecast + " Elevation: " + str(__forecast_data["properties"]["elevation"]["value"])
            # Add more stuff... Kind of useless in current state.

    def update(self):
        self.__init__(self.coordinates)

    def get(self, uri, future=0, include_local_time=False, convert=True, _v=False):
        """
        Get data from NWS

        :param uri: String, data to get, out of list https://pastebin.com/5vNdB4F4
        :param future: Int, how far in to the future to get data
        :param include_local_time: Whether or not to convert UTC time to Local Time.
        :param convert: Whether or not to convert Metric units to Imperial.
        :param _v: Prints information if true.

        :returns: Data, time occasionally
        """

        time = round_time()

        loop, index = 0, 0

        valid_times = []

        for value in self.__data["properties"][uri]["values"]:
            if time in value["validTime"]:
                if _v:
                    print("Exact time found for:", uri)

                if future == 0:
                    values = list(value.values())
                    if include_local_time:

                        values[0] = convert_time(values[0])

                        if convert:
                            values[1] = self.m_to_im(values[1], uom="c")
                            return values

                        else:
                            return values

                    else:
                        if convert:
                            return self.m_to_im(values[1], uom="c")

                        else:
                            return values[1]

            loop += 1

            if loop == len(value["validTime"]) - 1:
                for closest in self.__data["properties"][uri]["values"]:

                    if time.split("T")[0] in closest["validTime"].split("T")[0]:
                        valid_times.append([closest["validTime"].split("T")[1].split(":")[0],
                                           closest["value"], index])  # Add validTime hour to list

                    index += 1
                hour = int(time.split("T")[1].split(":")[0])

                try:
                    if include_local_time:
                        return (self.__data["properties"][uri]["values"][min(valid_times,
                                key=lambda x: abs(int(x[0]) - hour))[2] + future]
                                )

                    else:
                        return self.__data["properties"][uri]["values"][min(valid_times,
                                                                            key=lambda x: abs(int(x[0]) - hour))[2]
                                                                        + future]["value"]

                except ValueError:
                    print("Null value encountered.")
                    break

    @staticmethod
    def m_to_im(a, uom="c"):
        if uom == "c":
            return (9.0 / 5.0 * a) + 32

        if uom == "m/s":
            return 2.237 * a

    @staticmethod
    def load(url):
        with urllib.request.urlopen(url) as url:
            return json.loads(url.read().decode())


class Hydro:
    """
    NWS Hydrography data

    :param location: ID of station
    """

    def __init__(self, location):

        self.data = self.__xml(
            "https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage={station}&output=xml".format(station=location)
        )

    def level(self, historical=0, local_time=True):
        """
        River data

        :param historical: Int, How far back to look.
        :param local_time: Whether or not to convert UTC to Local Time.
        """

        if local_time:
            return {"Time": convert_time(self.data[5][historical][0].text),
                    "Stage": self.data[5][historical][1].text,
                    "Flow": self.data[5][historical][2].text}

        else:
            return {"Time": self.data[5][historical][0].text,
                    "Stage": self.data[5][historical][1].text,
                    "Flow": self.data[5][historical][2].text}

    def __xml(self, url):
        return eT.fromstring(self.load(url))

    @staticmethod
    def load(url):
        with urllib.request.urlopen(url) as url:
            return url.read()
