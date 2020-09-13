from math import floor

from libraries.slpp import dcsslpp as lua
from datetime import datetime

WRITEACCESS_ERROR = 'This file is write-protected!'
class WriteProtectionError(Exception):
    pass

NOTSUPPORTED_ERROR = 'This feature is not supported!'
class NotSupportedError(Exception):
    pass

class STMFile(object):
    STMfilename = ''
    readonly = True
    missionData = None
    missionLua = None
    theatre = None

    def __init__(self, filename, readonly=True):
        self.STMfilename = filename
        self.readonly = readonly

    def commit(self):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        stmfilehandle = open(self.STMfilename, "wb")
        stmfilehandle.write('staticTemplate ='.encode('UTF-8'))
        stmfilehandle.write("\n".encode('UTF-8'))
        stmfilehandle.write(lua.encode(self.missionData['staticTemplate']).encode('UTF-8'))
        stmfilehandle.close()

    def getMissionLUA(self):
        if not self.missionLua:
            stmfilehandle = open(self.STMfilename, 'rb')
            self.missionLua = stmfilehandle.read()
            stmfilehandle.close()
        return self.missionLua

    def getMission(self):
        if not self.missionData:
            self.missionData = lua.decode('{' + self.getMissionLUA().decode('UTF-8') + '}')
        return self.missionData['staticTemplate']

    def setMission(self, missiondata):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        self.missionData['staticTemplate'] = missiondata

    def getTheatre(self):
        if self.theatre:
            return self.theatre
        self.theatre = self.getMission()['threatre']
        return self.theatre

    def getTheatreLatLon(self):
        if self.getTheatre() == 'Caucasus':
            return {"lat": 42.355691, "lon": 43.323853}
        elif self.getTheatre() == 'PersianGulf':
            return {"lat": 26.304151 , "lon": 56.378506}
        elif self.getTheatre() == 'Nevada':
            return {"lat": 36.145615, "lon": -115.187618}
        elif self.getTheatre() == 'Normandy':
            return {"lat": 49.183336, "lon": -0.365908}
        else:
            return None

    def getDateTime(self):
        day = self.getMission()['date']['Day']
        month = self.getMission()['date']['Month']
        year = self.getMission()['date']['Year']
        starttime = self.getMission()['start_time']
        second = floor(starttime % 60)
        starttime /= 60
        minute = floor(starttime % 60)
        hour = floor(starttime / 60)
        datestr = f'{day:02}' + '.' + f'{month:02}' + '.' + f'{year:04}' + ' ' + f'{hour:02}' + ':' + f'{minute:02}'\
                  + ':' + f'{second:02}'
        return datetime.strptime(datestr, '%d.%m.%Y %H:%M:%S')

    def setDateTime(self, dt):
        if self.readonly:
            raise WriteProtectionError(WRITEACCESS_ERROR)
        missiondata = self.getMission()
        missiondata['date']['Day'] = dt.day
        missiondata['date']['Month'] = dt.month
        missiondata['date']['Year'] = dt.year
        missiondata['start_time'] = (((dt.hour*60) + dt.minute)*60) + dt.second
        self.setMission(missiondata)

    def setDateTimeNow(self):
        self.setDateTime(datetime.now())

    def getWeather(self):
        raise NotSupportedError(NOTSUPPORTED_ERROR)

    def setWeather(self, weatherdata):
        raise NotSupportedError(NOTSUPPORTED_ERROR)
