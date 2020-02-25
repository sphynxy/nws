# nws
Python 3 weather.gov library.  
nws.py has no requirements

### example
```python
import nws

n = nws.NWS(coordinates=(32.83, -97.36))
print(n.get("temperature", include_local_time=True))
