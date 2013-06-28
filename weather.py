import urllib2
from xml.dom import minidom
import codecs
import datetime

weatherField = ("cityName", "update", "weather", \
        "temperature", "wind", "cloud", "pressure", "humidity")
dateFormat = "%Y-%m-%dT%H:%M:%S"

def iconFromID(id):
    icon = "default"
    if 200 <= id <= 231:
        icon = "tsra"
    if 232 == id:
        icon = "hi_tsra"

    if 300 <= id <= 321:
        icon = "ra1"

    if 500 <= id <= 504:
        icon = "hi_shwrs"
    if 511 == id:
        icon = "fzra"
    if 520 <= id <= 521:
        icon = "shra"
    if id == 522:
        icon = "hi_shwrs"

    if 600 <= id <= 602:
        icon = "sn"
    if 611 <= id <= 621:
        icon = "rasn"

    if 701 == id:
        icon = "mist"
    if 711 == id:
        icon = "smoke"
    if 721 == id:
        icon = "mist"
    if 731 == id:
        icon = "dust"
    if 741 == id:
        icon = "fg"

    if 800 == id:
        icon = "skc"
    if 801 == id:
        icon = "few"
    if 802 == id:
        icon = "sct"
    if 803 == id:
        icon = "bkn"
    if 804 == id:
        icon = "ovc"

    if 900 == id:
        icon = "nsurtsra"
    if 901 == id:
        icon = "nsurtsra"
    if 902 == id:
        icon = "nsurtsra"
    if 905 == id:
        icon = "wind"
    if 906 == id:
        icon = "ip"

    return icon

class wind:
    def __init__(self, speed, direction):
        self.speed = speed
        self.direction = direction
    def __str__(self):
        return "speed: %s, direction: %s"%(self.speed, self.direction)

class temperature:
    def __init__(self, avg, max, min):
        self.avg = avg
        self.max = max
        self.min = min
    def __str__(self):
        return "avg: %s, max: %s, min: %s"%(self.avg, self.max, self.min)

class weatherObject:
    def __init__(self, cityName, lastUpdate, weather, \
            temperature, wind, cloud, pressure=None, humidity=None):
        self.cityName = cityName
        self.lastUpdate =  datetime.datetime.strptime(lastUpdate, dateFormat)
        self.weather = weather

        self.temperature = temperature
        self.wind = wind
        self.cloud = cloud

        self.pressure = pressure
        self.humidity = humidity

    def __str__(self):
        str = ":%s\n".join(weatherField) + ":%s\n"
        str = str%(self.cityName, self.lastUpdate, self.weather, self.temperature, self.wind, \
                self.cloud, self.pressure, self.humidity)
        return str

class weatherBase:
    def __init__(self, city, country, unit="metric"):
        self.city = city
        self.country = country
        self.dom = None
    def connect(self):
        weather_xml = urllib2.urlopen(self.url).read()
        self.dom = minidom.parseString(weather_xml)
    def parseData(self):
        pass

class weatherCurrent(weatherBase):
    " current weather"
    def __init__(self, city, country, unit="metric"):
        weatherBase.__init__(self, city, country, unit)
        self.url = "http://api.openweathermap.org/data/2.5/weather?q=%s&mode=xml&units=%s"%(city, unit)
    def parseData(self):
        if not self.dom:
            connect(self)

        xml_cityName = self.dom.getElementsByTagName('city')[0].getAttribute('name')
        xml_update = self.dom.getElementsByTagName('lastupdate')[0].getAttribute('value')
        xml_weather = self.dom.getElementsByTagName('weather')[0].getAttribute('value')

        xml_temperature_avg = self.dom.getElementsByTagName('temperature')[0].getAttribute('value')
        xml_temperature_max = self.dom.getElementsByTagName('temperature')[0].getAttribute('max')
        xml_temperature_min = self.dom.getElementsByTagName('temperature')[0].getAttribute('min')
        xml_temperature= temperature(xml_temperature_avg, xml_temperature_max, xml_temperature_min)

        xml_cloud = self.dom.getElementsByTagName('clouds')[0].getAttribute('value')

        xml_wind_speed = self.dom.getElementsByTagName('speed')[0].getAttribute('name')
        xml_wind_direct = self.dom.getElementsByTagName('direction')[0].getAttribute('name')
        xml_wind = wind(xml_wind_speed, xml_wind_direct)

        xml_humidity = self.dom.getElementsByTagName('humidity')[0].getAttribute('value')
        xml_pressure = self.dom.getElementsByTagName('pressure')[0].getAttribute('value')

        weather = weatherObject(xml_cityName, xml_update, xml_weather, xml_temperature, \
                xml_wind, xml_cloud, xml_pressure, xml_humidity)

        return weather

class weatherHourly(weatherBase):
    " weather every 3 hours"
    def __init__(self, city, unit="metric"):
        weatherBase.__init__(self, city, unit)
        self.url = "http://api.openweathermap.org/data/2.5/forecast?q=%s,%s&mode=xml&units=%s"%(city, country, unit)
    def parseData(self):
        pass


class weatherForecast(weatherBase):
    "weather forecast"
    def __init__(self, city, country, unit='metric', cnt=4):
        weatherBase.__init__(self, city, country, unit)
        self.cnt = 7 if cnt > 7 else cnt
        self.url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=%s&mode=xml&units=%s&cnt=%d"%(city, unit, cnt)
    def parseData(self):
        pass
    def getForecast(self, cnt=4):
        tempList = list()
        weatherList = list()
        cnt = self.cnt if cnt > self.cnt else cnt
        xml_forecast = self.dom.getElementsByTagName('time')
        for i in range(cnt):
            min = xml_forecast[i].getElementsByTagName('temperature')[0].getAttribute('min').split('.')[0]
            max = xml_forecast[i].getElementsByTagName('temperature')[0].getAttribute('max').split('.')[0]
            avg = xml_forecast[i].getElementsByTagName('temperature')[0].getAttribute('day').split('.')[0]
            temp = temperature(avg, max, min)
            tempList.append(temp)

            id = xml_forecast[i].getElementsByTagName('symbol')[0].getAttribute('number').split('.')[0]
            name = xml_forecast[i].getElementsByTagName('symbol')[0].getAttribute('name').split('.')[0]
            weatherList.append((int(id), name))
        return tempList, weatherList

def getAndDraw():
    service = weatherForecast("Aachen", "de")
    service.connect()
    tempList, weatherList = service.getForecast()

    day_one = datetime.datetime.today()

    icons = [iconFromID(x[0]) for x in weatherList]
    highs = [x.max for x in tempList]
    lows = [x.min for x in tempList]

    # Open SVG to process
    output = codecs.open('pre.svg', 'r', encoding='utf-8').read()

    # Insert icons and temperatures
    output = output.replace('ICON_ONE',icons[0]).replace('ICON_TWO',icons[1]).replace('ICON_THREE',icons[2]).replace('ICON_FOUR',icons[3])
    output = output.replace('HIGH_ONE',str(highs[0])).replace('HIGH_TWO',str(highs[1])).replace('HIGH_THREE',str(highs[2])).replace('HIGH_FOUR',str(highs[3]))
    output = output.replace('LOW_ONE',str(lows[0])).replace('LOW_TWO',str(lows[1])).replace('LOW_THREE',str(lows[2])).replace('LOW_FOUR',str(lows[3]))
    output = output.replace('Today',day_one.strftime("%a, %b %d") + ', ' + service.city)

    # Insert days of week
    one_day = datetime.timedelta(days=1)
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    output = output.replace('DAY_THREE',days_of_week[(day_one + 2*one_day).weekday()]).replace('DAY_FOUR',days_of_week[(day_one + 3*one_day).weekday()])

    # Write output
    codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)

    return output

    #import cairocffi as cairo
    #import rsvg
    #
    #img =  cairo.ImageSurface(cairo.FORMAT_ARGB32, 600,800)
    #ctx = cairo.Context(img)
    #handler= rsvg.Handle(file="weather-script-output.svg")
    #handler.render_cairo(ctx)
    #img.write_to_png("weather.png")
