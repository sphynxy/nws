National Weather Service (weather.gov) API
=========

Currently there is no easy way to change the location in this API (but that will be fixed soon)

### Getting Info example
```python
import nws

n = nws.NWS()

# Getting the temperature 1 segment in the future
print(n.get("temperature"), 1)

# Or current temperature
print(n.get("temperature"))
```

Temperature isn't the only thing we can get! The NWS supplies much more info than that.
You can see a full list in the gridpoint json file. Here are a few examples:
- "temperature"
- "dewpoint"
- "relativeHumidity"
- "windSpeed"
- "windChill"
- "probabilityOfPrecipitation"
- "visibility"

You can also get a forecast
```python
print(n.forecast())

>>> This Afternoon|Cloudy. High near 57, with temperatures falling to around 52 in the afternoon. North wind around 15 mph, with gusts as high as 25 mph. New rainfall amounts between a tenth and quarter of an inch possible.
```

Unit conversion soon.
