import datetime
import json
import re
import requests


def _int(s):
    r = ''
    for c in str(s):
        if c.isdigit():
            r += c
    return r or 0


def _clean(s):
    s = str(s).strip()
    if s.endswith(';'):
        s = s[:-1]
    return s


def get_bj_weather():
    url = 'http://www.weather.com.cn/weather/101010100.shtml'
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html_text = resp.text
    weather_data = _clean(re.findall("hour3data=([\s\S]*?)</script>", html_text)[0])
    aqi_data = _clean(re.findall("observe24h_data = ([\s\S]*?)</script>", html_text)[0])

    aqi = None
    for ele in json.loads(aqi_data)['od']['od2'][::-1]:
        aqi = ele.get('od28')
        if aqi:
            break

    weather_info_list = ['Beijing']
    now = datetime.datetime.now() + datetime.timedelta(hours=8)
    current_hour = now.hour
    point = [
        [7, 8, 9],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18],
        [19, 20, 21],
        [22, 23, 24, 0],
        [1, 2, 3],
        [4, 5, 6]
    ]

    for p, ele in zip(point, json.loads(weather_data)['1d']):
        if current_hour in p:
            _, _, a, b, _, c, _ = ele.strip().split(',')
            weather_info_list.append(now.strftime("%Y%m%d%H%M%S"))
            weather_info_list.append(_int(b))     # temperature
            weather_info_list.append(None)        # Humidity
            weather_info_list.append(_int(c))     # WindPower
            weather_info_list.append(_int(aqi))   # AQI
            weather_info_list.append(a)           # GeneralWeather
            weather_info_list.append(None)        # Rainfall
            break

    return weather_info_list


if __name__ == '__main__':
    from utils import write_to_csv
    write_to_csv(get_bj_weather(), 'weather')
