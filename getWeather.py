#!/usr/bin/env python
import urllib2
import json
import codecs
import datetime

country = "Germany"
city = "Aachen"
key = "8bb106a0dd83d51f"
urlTmp = "http://api.wunderground.com/api/%s/%s/q/%s/%s.json"

weatherField = ("datetime", "condition", "icon", "avg", "max", "min", "rain")

def iconMap(name):
    result = "skc"

    if name == "chanceflurries":
        result = "sn"
    if name == "chancerain":
        result = "ra1"
    if name == "chancesleet":
        result = "ip"
    if name == "chancesnow":
        result = "sn"
    if name == "chancetstorms":
        result = "tsra"
    if name == "clear":
        result = "skc"
    if name == "cloudy":
        result = "ovc"
    if name == "flurries":
        result = "sn"
    if name == "fog":
        result = "fg"
    if name == "hazy":
        result = "mist"
    if name == "mostlycloudy":
        result = "bkn"
    if name == "mostlysunny":
        result = "sct"
    if name == "partlycloudy":
        result = "sct"
    if name == "partlysunny":
        result = "bkn"
    if name == "sleet":
        result = "ip"
    if name == "rain":
        result = "ra"
    if name == "snow":
        result = "sn"
    if name == "sunny":
        result = "skc"
    if name == "tstorms":
        result = "tsra"
    if name == "cloudy":
        result = "ovc"

    return result

class weather(dict):
    "customized dictionary to store weather related data"

    def __init__(self,*arg,**kw):
        super(weather, self).__init__(*arg, **kw)

    def __setitem__(self, key, value):
        if key in weatherField:
             super(weather,self).__setitem__(key, value)

    def __getitem__(self, key):
        value = None
        if key in weatherField:
             value = super(weather,self).__getitem__(key)
        return value

    def __str__(self):
        string = ''
        for key in weatherField:
            if super(weather,self).has_key(key):
                string += key + ': ' + super(weather,self).__getitem__(key) + '\n'
        return string[:-1]


def iround(i):
    "round to the nearest integer"
    return int(round(i) - .5) + (i > 0)

def f2c(temp):
    result = float((temp -32))*5/9
    return iround(result)

"all function return list of weather"
def forecast(json_string):
    parsed_json = json.loads(json_string)
    weatherList = list()
    for data in parsed_json['forecast']['simpleforecast']['forecastday']:
        weatherDay = weather()
        weatherDay["datetime"] =  data['date']['weekday']
        weatherDay["condition"] =  data['conditions']
        weatherDay["max"] = data['high']['celsius']
        weatherDay["min"] = data['low']['celsius']
        weatherDay["rain"] =  str(data['pop'])
        weatherDay["icon"] =  data['icon']
        weatherList.append(weatherDay)

    return weatherList

def hourly(json_string):
    parsed_json = json.loads(json_string)
    weatherList = list()
    for data in parsed_json['hourly_forecast']:
        weatherDay = weather()
        weatherDay["datetime"] = data['FCTTIME']['hour']
        weatherDay["condition"] = data['condition']
        weatherDay["icon"] = data['icon']
        weatherDay["avg"] = data['temp']["metric"]
        weatherList.append(weatherDay)
    return weatherList

def conditions(json_string):
    parsed_json = json.loads(json_string)
    data = parsed_json['current_observation']
    weatherList = list()
    weatherDay = weather()
    weatherDay["datetime"] = data["observation_time"]
    weatherDay["condition"] = data["weather"]
    weatherDay["icon"] = data["icon"]
    weatherDay["avg"] = str(data["temp_c"])
    weatherList.append(weatherDay)
    return weatherList

function = {"forecast": forecast, "hourly": hourly, "conditions": conditions}

def w2svg(feature):

    url = urllib2.urlopen(urlTmp%(key, feature, country, city))
    json_string = url.read()
    weatherList = function[feature](json_string)
    #for weatherDay in weatherList:
        #print weatherDay
    url.close

    day_one = datetime.datetime.today()

    icons = [iconMap(x["icon"]) for x in weatherList]
    highs = [x["max"] for x in weatherList]
    lows = [x["min"] for x in weatherList]
    rains = [x["rain"] for x in weatherList]
    conds = [x["condition"] for x in weatherList]

    # Open SVG to process
    output = codecs.open('pre2.svg', 'r', encoding='utf-8').read()

    # Insert icons and temperatures
    output = output.replace('ICON_ONE',icons[0]).replace('ICON_TWO',icons[1]).replace('ICON_THREE',icons[2]).replace('ICON_FOUR',icons[3])
    output = output.replace('HIGH_ONE',str(highs[0])).replace('HIGH_TWO',str(highs[1])).replace('HIGH_THREE',str(highs[2])).replace('HIGH_FOUR',str(highs[3]))
    output = output.replace('LOW_ONE',str(lows[0])).replace('LOW_TWO',str(lows[1])).replace('LOW_THREE',str(lows[2])).replace('LOW_FOUR',str(lows[3]))
    output = output.replace('RAIN_ONE',rains[0])
    output = output.replace('RAIN_TWO',rains[1])
    output = output.replace('RAIN_THREE',rains[2])
    output = output.replace('RAIN_FOUR',rains[3])

    output = output.replace('COND_ONE',conds[0])
    output = output.replace('COND_TWO',conds[1])
    output = output.replace('COND_THREE',conds[2])
    output = output.replace('COND_FOUR',conds[3])
    output = output.replace('Today',day_one.strftime("%a, %b %d") + ', ' + city)

    # Insert days of week
    one_day = datetime.timedelta(days=1)
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    output = output.replace('Tomorrow',days_of_week[(day_one + 1*one_day).weekday()])
    output = output.replace('DAY_THREE',days_of_week[(day_one + 2*one_day).weekday()]).replace('DAY_FOUR',days_of_week[(day_one + 3*one_day).weekday()])

    url = urllib2.urlopen(urlTmp%(key, "hourly" , country, city))
    json_string = url.read()
    hourlyList = function["hourly"](json_string)
    url.close

    hourly_icons = [iconMap(x["icon"]) for x in hourlyList[0:10]]
    hourly_datetime = [x["datetime"] for x in hourlyList[0:10]]
    hourly_avg = [int(x["avg"]) for x in hourlyList[0:10]]
    avg_max = int(max(hourly_avg))
    avg_min = int(min(hourly_avg))
    avg_range = avg_max - avg_min

    hourly_yaix = [str(460 - int(float(x - avg_min)/avg_range*30)) for x in hourly_avg]

    output = output.replace('HOURLY_MAX',str(avg_max))
    output = output.replace('HOURLY_MIN',str(avg_min))

    output = output.replace('HOURLY_0',hourly_datetime[0])
    output = output.replace('HOURLY_1',hourly_datetime[1])
    output = output.replace('HOURLY_2',hourly_datetime[2])
    output = output.replace('HOURLY_3',hourly_datetime[3])
    output = output.replace('HOURLY_4',hourly_datetime[4])
    output = output.replace('HOURLY_5',hourly_datetime[5])
    output = output.replace('HOURLY_6',hourly_datetime[6])
    output = output.replace('HOURLY_7',hourly_datetime[7])
    output = output.replace('HOURLY_8',hourly_datetime[8])
    output = output.replace('HOURLY_9',hourly_datetime[9])

    output = output.replace('HOURLY_ICON_0',hourly_icons[0])
    output = output.replace('HOURLY_ICON_1',hourly_icons[1])
    output = output.replace('HOURLY_ICON_2',hourly_icons[2])
    output = output.replace('HOURLY_ICON_3',hourly_icons[3])
    output = output.replace('HOURLY_ICON_4',hourly_icons[4])
    output = output.replace('HOURLY_ICON_5',hourly_icons[5])
    output = output.replace('HOURLY_ICON_6',hourly_icons[6])
    output = output.replace('HOURLY_ICON_7',hourly_icons[7])
    output = output.replace('HOURLY_ICON_8',hourly_icons[8])
    output = output.replace('HOURLY_ICON_9',hourly_icons[9])

    output = output.replace('HOURLY_YAIX_0',hourly_yaix[0])
    output = output.replace('HOURLY_YAIX_1',hourly_yaix[1])
    output = output.replace('HOURLY_YAIX_2',hourly_yaix[2])
    output = output.replace('HOURLY_YAIX_3',hourly_yaix[3])
    output = output.replace('HOURLY_YAIX_4',hourly_yaix[4])
    output = output.replace('HOURLY_YAIX_5',hourly_yaix[5])
    output = output.replace('HOURLY_YAIX_6',hourly_yaix[6])
    output = output.replace('HOURLY_YAIX_7',hourly_yaix[7])
    output = output.replace('HOURLY_YAIX_8',hourly_yaix[8])
    output = output.replace('HOURLY_YAIX_9',hourly_yaix[9])

    return output


if __name__ == "__main__":
    output = w2svg("forecast")
    codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)

    #import cairo
    #import rsvg

    #img =  cairo.ImageSurface(cairo.FORMAT_ARGB32, 600,800)
    #ctx = cairo.Context(img)
    #handler= rsvg.Handle(file="weather-script-output.svg")
    #handler.render_cairo(ctx)
    #img.write_to_png("weather.png")
