# nws
wip nws api for getting weather data for an automated garden

example: this gets the hourly temperature for the next 12 hours (right now it is just "sections" because api.weather.gov doesnt always have the data for the exact hour, so it will approximate to the nearest hour)

```
import nws

weather = nws.NWS()

def hourly_temperature(hours):

    period = []
    temperature = []

    for hour in range(hours):

        period.append(hour)
        try:
            temperature.append(weather.get("temperature", future=hour, include_future=True))
        except TypeError:
            print('uh')

    return [period, temperature]

h = hourly_temperature(12)
```
