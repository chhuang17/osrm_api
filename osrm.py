import requests
import json
import numpy as np
import haversine as hs
import warnings


__version__ = '1.0.1'


tableURL = 'http://router.project-osrm.org/table/v1/driving/'
routeURL = 'http://router.project-osrm.org/route/v1/driving/'


def distance(orign, destn, unit='m', steps='false', timeout=5):
    """ Get the distance between `orign` and `destn` """
    newURL = routeURL + f'{orign[0]},{orign[1]};{destn[0]},{destn[1]}' + f'?steps={steps}'
    try:
        r = requests.get(newURL, timeout=timeout)
    except requests.exceptions.Timeout:
        warnings.warn('Exceed the maximum timeout to request, so use the haversine distance instead.')
        if (unit == 'm'):
            return hs.haversine((orign[1],orign[0]),(destn[1],destn[0]), unit=hs.Unit.METERS)
        elif (unit == 'km'):
            return hs.haversine((orign[1],orign[0]),(destn[1],destn[0]), unit=hs.Unit.KILOMETERS)
        else:
            raise ValueError(f"unit '{unit}' not understood.")
    
    routeInfo = json.loads(r.content)
    if (routeInfo['code'] == 'Ok'):
        if (steps == 'false'):
            if (unit == 'm'):
                return routeInfo['routes'][0]['legs'][0]['distance']
            elif (unit == 'km'):
                return routeInfo['routes'][0]['legs'][0]['distance'] / 1000
            else:
                raise ValueError(f"unit '{unit}' not understood.")
        elif (steps == 'true'):
            if (unit == 'm'):
                return routeInfo['routes'][0]['legs'][0]['distance'], routeInfo['routes'][0]['legs'][0]['summary']
            elif (unit == 'km'):
                return routeInfo['routes'][0]['legs'][0]['distance'] / 1000, routeInfo['routes'][0]['legs'][0]['summary']
            else:
                raise ValueError(f"unit '{unit}' not understood.")
    else:
        warnings.warn('Fail to get data from the OSRM API, so use the haversine distance instead.')
        if (unit == 'm'):
            return hs.haversine((orign[1],orign[0]),(destn[1],destn[0]), unit=hs.Unit.METERS)
        elif (unit == 'km'):
            return hs.haversine((orign[1],orign[0]),(destn[1],destn[0]), unit=hs.Unit.KILOMETERS)
        else:
            raise ValueError(f"unit '{unit}' not understood.")

def travTime(orign, destn, unit='second', steps='false', timeout=5, speed=30):
    """ Get the travel time between `orign` and `destn` """
    newURL = routeURL + f'{orign[0]},{orign[1]};{destn[0]},{destn[1]}' + f'?steps={steps}'
    try:
        r = requests.get(newURL, timeout=timeout)
    except requests.exceptions.Timeout:
        warnings.warn('Exceed the maximum timeout to request, so use the haversine distance instead.')
        hsDist = hs.haversine((orign[1],orign[0]),(destn[1],destn[0]), unit=hs.Unit.METERS)
        if (unit == 'second'):
            speed /= 3.6
            return hsDist/speed
        elif (unit == 'minute'):
            speed /= 3.6
            return (hsDist/speed)/60
        elif (unit == 'hour'):
            return (hsDist/1000)/speed
        else:
            raise ValueError(f"unit '{unit}' not understood.")
    
    routeInfo = json.loads(r.content)
    if (routeInfo['code'] == 'Ok'):
        if (steps == 'false'):
            if (unit =='second'):
                return routeInfo['routes'][0]['legs'][0]['duration']
            elif (unit == 'minute'):
                return routeInfo['routes'][0]['legs'][0]['duration'] / 60
            elif (unit == 'hour'):
                return routeInfo['routes'][0]['legs'][0]['duration'] / 60 / 60
            else:
                raise ValueError(f"unit '{unit}' not understood.")
        elif (steps == 'true'):
            if (unit =='second'):
                return routeInfo['routes'][0]['legs'][0]['duration'], routeInfo['routes'][0]['legs'][0]['summary']
            elif (unit == 'minute'):
                return routeInfo['routes'][0]['legs'][0]['duration'] / 60, routeInfo['routes'][0]['legs'][0]['summary']
            elif (unit == 'hour'):
                return routeInfo['routes'][0]['legs'][0]['duration'] / 60 / 60, routeInfo['routes'][0]['legs'][0]['summary']
            else:
                raise ValueError(f"unit '{unit}' not understood.")
    else:
        warnings.warn('Fail to get data from the OSRM API, so use the haversine distance instead.')
        hsDist = hs.haversine((orign[1],orign[0]),(destn[1],destn[0]), unit=hs.Unit.METERS)
        if (unit == 'second'):
            speed /= 3.6
            return hsDist/speed
        elif (unit == 'minute'):
            speed /= 3.6
            return (hsDist/speed)/60
        elif (unit == 'hour'):
            return (hsDist/1000)/speed
        else:
            raise ValueError(f"unit '{unit}' not understood.")

def odMatrix(nodeList, get='distance', sources=None, distUnit='m', timeUnit='second', timeout=5, speed=30, decimals=1):
    """ Get the O-D Matrix from all nodes in `nodeList` """
    # nodeList: [(), (), ... , ()]
    get = get.replace(' ', '')
    nodes = ''
    for i, node in enumerate(nodeList):
        if (i < len(nodeList)-1):
            nodes += str(node[0]) + ',' + str(node[1]) + ';'
        else:
            nodes += str(node[0]) + ',' + str(node[1])
    
    # sources = 0 will return 1xN matrix
    if sources == 0:
        nodes += '?sources=0'
        # 依據 get 參數決定回傳的值
        if (get == 'duration'):
            nodes += f'&annotations={get}'
            newURL = tableURL + nodes            
            try:
                r = requests.get(newURL, timeout=timeout)
            except requests.exceptions.Timeout:
                warnings.warn('Exceed the maximum timeout to request, so use the haversine distance here.')
                timeMatx = []
                row = []
                for y in nodeList:
                    hsDist = hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.METERS)
                    if (timeUnit == 'second'):
                        row.append(hsDist/(speed/3.6))
                    elif (timeUnit == 'minute'):
                        row.append((hsDist/(speed/3.6))/60)
                    elif (timeUnit == 'hour'):
                        row.append((hsDist/(speed/3.6))/60/60)
                    else:
                        raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                timeMatx.append(row)
                return np.round(np.array(timeMatx), decimals)
            
            tableInfo = json.loads(r.content)
            if (tableInfo['code'] == 'Ok'):
                if (timeUnit == 'second'):
                    return np.array(tableInfo['durations'])
                elif (timeUnit == 'minute'):
                    return np.round(np.array(tableInfo['durations'])/60, decimals)
                elif (timeUnit == 'hour'):
                    return np.round(np.array(tableInfo['durations'])/60/60, decimals)
                else:
                    raise ValueError(f"timeUnit '{timeUnit}' not understood.")
            else:
                warnings.warn('Fail to get data from the OSRM API, so use the haversine distance here.')
                timeMatx = []
                row = []
                for y in nodeList:
                    hsDist = hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.METERS)
                    if (timeUnit == 'second'):
                        row.append(hsDist/(speed/3.6))
                    elif (timeUnit == 'minute'):
                        row.append((hsDist/(speed/3.6))/60)
                    elif (timeUnit == 'hour'):
                        row.append((hsDist/(speed/3.6))/60/60)
                    else:
                        raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                timeMatx.append(row)
                return np.round(np.array(timeMatx), decimals)
        
        elif (get == 'distance'):
            nodes += f'&annotations={get}'
            newURL = tableURL + nodes
            try:
                r = requests.get(newURL, timeout=timeout)
            except requests.exceptions.Timeout:
                warnings.warn('Exceed the maximum timeout to request, so use the haversine distance here.')
                distMatx = []
                row = []
                for y in nodeList:
                    if (distUnit == 'm'):
                        row.append(hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.METERS))
                    elif (distUnit == 'km'):
                        row.append(hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.KILOMETERS))
                    else:
                        raise ValueError(f"distUnit '{distUnit}' not understood.")
                distMatx.append(row)
                return np.round(np.array(distMatx), decimals)
            
            tableInfo = json.loads(r.content)
            if (tableInfo['code'] == 'Ok'):
                if (distUnit == 'm'):
                    return np.array(tableInfo['distances'])
                elif (distUnit == 'km'):
                    return np.round(np.array(tableInfo['distances'])/1000, decimals)
                else:
                    raise ValueError(f"distUnit '{distUnit}' not understood")
            else:
                warnings.warn('Fail to get data from the OSRM API, so use the haversine distance here.')
                distMatx = []
                row = []
                for y in nodeList:
                    if (distUnit == 'm'):
                        row.append(hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.METERS))
                    elif (distUnit == 'km'):
                        row.append(hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.KILOMETERS))
                    else:
                        raise ValueError(f"distUnit '{distUnit}' not understood.")
                distMatx.append(row)
                return np.round(np.array(distMatx), decimals)
        
        elif (get == 'duration;distance') or (get == 'distance;duration'):
            nodes += f'&annotations={get}'
            newURL = tableURL + nodes
            try:
                r = requests.get(newURL, timeout=timeout)
            except requests.exceptions.Timeout:
                warnings.warn('Exceed the maximum timeout to request, so use the haversine distance here.')
                timeMatx, distMatx = [], []
                timeRow, distRow = [], []
                for y in nodeList:
                    hsDist = hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.METERS)
                    if (timeUnit == 'second'):
                        timeRow.append(hsDist/(speed/3.6))
                    elif (timeUnit == 'minute'):
                        timeRow.append((hsDist/(speed/3.6))/60)
                    elif (timeUnit == 'hour'):
                        timeRow.append((hsDist/(speed/3.6))/60/60)
                    else:
                        raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                    
                    if (distUnit == 'm'):
                        distRow.append(hsDist)
                    elif (distUnit == 'km'):
                        distRow.append(hsDist/1000)
                    else:
                        raise ValueError(f"distUnit '{distUnit}' not understood.")
                timeMatx.append(timeRow)
                distMatx.append(distRow)
                return np.round(np.array(timeMatx), decimals), np.round(np.array(distMatx), decimals)

            tableInfo = json.loads(r.content)
            if (tableInfo['code'] == 'Ok'):
                if (timeUnit == 'second'):
                    timeMatx = np.array(tableInfo['durations'])
                elif (timeUnit == 'minute'):
                    timeMatx = np.array(tableInfo['durations']) / 60
                elif (timeUnit == 'hour'):
                    timeMatx = np.array(tableInfo['durations']) / 60 / 60
                else:
                    raise ValueError(f"timeUnit '{timeUnit}' not understood")
                
                if (distUnit == 'm'):
                    distMatx = np.array(tableInfo['distances'])
                elif (distUnit == 'km'):
                    distMatx = np.array(tableInfo['distances']) / 1000
                else:
                    raise ValueError(f"distUnit '{distUnit}' not understood")
                return np.round(np.array(timeMatx), decimals), np.round(np.array(distMatx), decimals)
            else:
                warnings.warn('Fail to get data from the OSRM API, so use the haversine distance instead.')
                timeMatx, distMatx = [], []
                timeRow, distRow = [], []
                for y in nodeList:
                    hsDist = hs.haversine((nodeList[0][1],nodeList[0][0]),(y[1],y[0]), unit=hs.Unit.METERS)
                    if (timeUnit == 'second'):
                        timeRow.append(hsDist/(speed/3.6))
                    elif (timeUnit == 'minute'):
                        timeRow.append((hsDist/(speed/3.6))/60)
                    elif (timeUnit == 'hour'):
                        timeRow.append((hsDist/(speed/3.6))/60/60)
                    else:
                        raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                    
                    if (distUnit == 'm'):
                        distRow.append(hsDist)
                    elif (distUnit == 'km'):
                        distRow.append(hsDist/1000)
                    else:
                        raise ValueError(f"distUnit '{distUnit}' not understood.")
                timeMatx.append(timeRow)
                distMatx.append(distRow)
                return np.round(np.array(timeMatx), decimals), np.round(np.array(distMatx), decimals)
        else:
            raise ValueError(f"get '{get}' not understood.")
    
    else:
        # 依據 get 參數決定回傳的值
        if (get == 'duration'):
            nodes += f'?annotations={get}'
            newURL = tableURL + nodes            
            try:
                r = requests.get(newURL, timeout=timeout)
            except requests.exceptions.Timeout:
                warnings.warn('Exceed the maximum timeout to request, so use the haversine distance instead.')
                timeMatx = []
                for x in nodeList:
                    row = []
                    for y in nodeList:
                        hsDist = hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.METERS)
                        if (timeUnit == 'second'):
                            row.append(hsDist/(speed/3.6))
                        elif (timeUnit == 'minute'):
                            row.append((hsDist/(speed/3.6))/60)
                        elif (timeUnit == 'hour'):
                            row.append((hsDist/(speed/3.6))/60/60)
                        else:
                            raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                    timeMatx.append(row)
                return np.round(np.array(timeMatx), decimals)
            
            tableInfo = json.loads(r.content)
            if (tableInfo['code'] == 'Ok'):
                if (timeUnit == 'second'):
                    return np.array(tableInfo['durations'])
                elif (timeUnit == 'minute'):
                    return np.round(np.array(tableInfo['durations'])/60, decimals)
                elif (timeUnit == 'hour'):
                    return np.round(np.array(tableInfo['durations'])/60/60, decimals)
                else:
                    raise ValueError(f"timeUnit '{timeUnit}' not understood.")
            else:
                warnings.warn('Fail to get data from the OSRM API, so use the haversine distance instead.')
                timeMatx = []
                for x in nodeList:
                    row = []
                    for y in nodeList:
                        hsDist = hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.METERS)
                        if (timeUnit == 'second'):
                            row.append(hsDist/(speed/3.6))
                        elif (timeUnit == 'minute'):
                            row.append((hsDist/(speed/3.6))/60)
                        elif (timeUnit == 'hour'):
                            row.append((hsDist/(speed/3.6))/60/60)
                        else:
                            raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                    timeMatx.append(row)
                return np.round(np.array(timeMatx), decimals)
        
        elif (get == 'distance'):
            nodes += f'?annotations={get}'
            newURL = tableURL + nodes
            try:
                r = requests.get(newURL, timeout=timeout)
            except requests.exceptions.Timeout:
                warnings.warn('Exceed the maximum timeout to request, so use the haversine distance instead.')
                distMatx = []
                for x in nodeList:
                    row = []
                    for y in nodeList:
                        if (distUnit == 'm'):
                            row.append(hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.METERS))
                        elif (distUnit == 'km'):
                            row.append(hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.KILOMETERS))
                        else:
                            raise ValueError(f"distUnit '{distUnit}' not understood.")
                    distMatx.append(row)
                return np.round(np.array(distMatx), decimals)

            tableInfo = json.loads(r.content)
            if (tableInfo['code'] == 'Ok'):
                if (distUnit == 'm'):
                    return np.array(tableInfo['distances'])
                elif (distUnit == 'km'):
                    return np.round(np.array(tableInfo['distances'])/1000, decimals)
                else:
                    raise ValueError(f"distUnit '{distUnit}' not understood.")
            else:
                warnings.warn('Fail to get data from the OSRM API, so use the haversine distance instead.')
                distMatx = []
                for x in nodeList:
                    row = []
                    for y in nodeList:
                        if (distUnit == 'm'):
                            row.append(hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.METERS))
                        elif (distUnit == 'km'):
                            row.append(hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.KILOMETERS))
                        else:
                            raise ValueError(f"distUnit '{distUnit}' not understood.")
                    distMatx.append(row)
                return np.round(np.array(distMatx), decimals)
        
        elif (get == 'duration;distance') or (get == 'distance;duration'):
            nodes += f'?annotations={get}'
            newURL = tableURL + nodes
            try:
                r = requests.get(newURL, timeout=timeout)
            except requests.exceptions.Timeout:
                warnings.warn('Exceed the maximum timeout to request, so use the haversine distance instead.')
                timeMatx, distMatx = [], []
                for x in nodeList:
                    timeRow, distRow = [], []
                    for y in nodeList:
                        hsDist = hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.METERS)
                        if (timeUnit == 'second'):
                            timeRow.append(hsDist/(speed/3.6))
                        elif (timeUnit == 'minute'):
                            timeRow.append((hsDist/(speed/3.6))/60)
                        elif (timeUnit == 'hour'):
                            timeRow.append((hsDist/(speed/3.6))/60/60)
                        else:
                            raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                        
                        if (distUnit == 'm'):
                            distRow.append(hsDist)
                        elif (distUnit == 'km'):
                            distRow.append(hsDist/1000)
                        else:
                            raise ValueError(f"distUnit '{distUnit}' not understood.")
                    timeMatx.append(timeRow)
                    distMatx.append(distRow)
                return np.round(np.array(timeMatx), decimals), np.round(np.array(distMatx), decimals)

            tableInfo = json.loads(r.content)
            if (tableInfo['code'] == 'Ok'):
                if (timeUnit == 'second'):
                    timeMatx = np.array(tableInfo['durations'])
                elif (timeUnit == 'minute'):
                    timeMatx = np.array(tableInfo['durations']) / 60
                elif (timeUnit == 'hour'):
                    timeMatx = np.array(tableInfo['durations']) / 60 / 60
                else:
                    raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                
                if (distUnit == 'm'):
                    distMatx = np.array(tableInfo['distances'])
                elif (distUnit == 'km'):
                    distMatx = np.array(tableInfo['distances']) / 1000
                else:
                    raise ValueError(f"distUnit '{distUnit}' not understood.")
                return np.round(np.array(timeMatx), decimals), np.round(np.array(distMatx), decimals)
            else:
                warnings.warn('Fail to get data from the OSRM API, so use the haversine distance instead.')
                timeMatx, distMatx = [], []
                for x in nodeList:
                    timeRow, distRow = [], []
                    for y in nodeList:
                        hsDist = hs.haversine((x[1],x[0]),(y[1],y[0]), unit=hs.Unit.METERS)
                        if (timeUnit == 'second'):
                            timeRow.append(hsDist/(speed/3.6))
                        elif (timeUnit == 'minute'):
                            timeRow.append((hsDist/(speed/3.6))/60)
                        elif (timeUnit == 'hour'):
                            timeRow.append((hsDist/(speed/3.6))/60/60)
                        else:
                            raise ValueError(f"timeUnit '{timeUnit}' not understood.")
                        
                        if (distUnit == 'm'):
                            distRow.append(hsDist)
                        elif (distUnit == 'km'):
                            distRow.append(hsDist/1000)
                        else:
                            raise ValueError(f"distUnit '{distUnit}' not understood.")
                    timeMatx.append(timeRow)
                    distMatx.append(distRow)
                return np.round(np.array(timeMatx), decimals), np.round(np.array(distMatx), decimals)
        else:
            raise ValueError(f"get '{get}' not understood.")
        
def distSeq(nodeList=None, matrix=None, sources=None, distUnit='m', timeout=5):
    if matrix is None:
        matrix = odMatrix(nodeList, get='distance', sources=sources, distUnit=distUnit, timeUnit='second', timeout=timeout)
    elif nodeList is None:
        matrix = matrix
    seq = []
    i = 0
    j = 1
    try:
        while i < matrix.shape[0]-1:
            while j < matrix.shape[1]:
                seq.append(matrix[i][j])
                i += 1
                j += 1
        return seq
    except:
        return matrix

def travTimeSeq(nodeList=None, matrix=None, sources=None, timeUnit='second', timeout=5):
    if matrix is None:
        matrix = odMatrix(nodeList, get='duration', sources=sources, distUnit='m', timeUnit=timeUnit, timeout=timeout)
    elif nodeList is None:
        matrix = matrix
    seq = []
    i = 0
    j = 1
    while i < matrix.shape[0]-1:
        while j < matrix.shape[1]:
            seq.append(matrix[i][j])
            i += 1
            j += 1
    return seq
