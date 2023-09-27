import requests
import json
import numpy as np


__version__ = '0.1.0'


tableURL = 'http://router.project-osrm.org/table/v1/driving/'
routeURL = 'http://router.project-osrm.org/route/v1/driving/'


def distance(orign, destn, unit='m', steps='false'):
    newURL = routeURL + f'{orign[0]},{orign[1]};{destn[0]},{destn[1]}' + f'?steps={steps}'
    r = requests.get(newURL)
    routeInfo = json.loads(r.content)
    if routeInfo['code'] != 'Ok':
        return np.nan
    if steps == 'false':
        if unit == 'm':
            return routeInfo['routes'][0]['legs'][0]['distance']
        elif unit == 'km':
            return routeInfo['routes'][0]['legs'][0]['distance'] / 1000
    elif steps == 'true':
        if unit == 'm':
            return routeInfo['routes'][0]['legs'][0]['distance'], routeInfo['routes'][0]['legs'][0]['summary']
        elif unit == 'km':
            return routeInfo['routes'][0]['legs'][0]['distance'] / 1000, routeInfo['routes'][0]['legs'][0]['summary']

def travTime(orign, destn, unit='second', steps='false'):
    newURL = routeURL + f'{orign[0]},{orign[1]};{destn[0]},{destn[1]}' + f'?steps={steps}'
    r = requests.get(newURL)
    routeInfo = json.loads(r.content)
    if routeInfo['code'] != 'Ok':
        return np.nan
    if steps == 'false':
        if unit =='second':
            return routeInfo['routes'][0]['legs'][0]['duration']
        elif unit == 'minute':
            return routeInfo['routes'][0]['legs'][0]['duration'] / 60
        elif unit == 'hour':
            return routeInfo['routes'][0]['legs'][0]['duration'] / 60 / 60
    elif steps == 'true':
        if unit =='second':
            return routeInfo['routes'][0]['legs'][0]['duration'], routeInfo['routes'][0]['legs'][0]['summary']
        elif unit == 'minute':
            return routeInfo['routes'][0]['legs'][0]['duration'] / 60, routeInfo['routes'][0]['legs'][0]['summary']
        elif unit == 'hour':
            return routeInfo['routes'][0]['legs'][0]['duration'] / 60 / 60, routeInfo['routes'][0]['legs'][0]['summary']

def odMatrix(nodeList, get='distance', sources=None, distUnit='m', timeUnit='second'):
    # input: [(), (), ... , ()]
    nodes = ''
    for i, node in enumerate(nodeList):
        if i < len(nodeList)-1:
            nodes += str(node[0]) + ',' + str(node[1]) + ';'
        else:
            nodes += str(node[0]) + ',' + str(node[1])
    
    # sources = 0
    if sources == 0:
        nodes += '?sources=0'
        # 依據 get 參數決定回傳的值
        if get == 'duration':
            nodes += f'&annotations={get}'
            newURL = tableURL + nodes
            r = requests.get(newURL)
            info = json.loads(r.content)
            try:
                if timeUnit == 'second':
                    return np.array(info['durations'])
                elif timeUnit == 'minute':
                    return np.array(info['durations']) / 60
                elif timeUnit == 'hour':
                    return np.array(info['durations']) / 60 / 60
            except:
                return 'Cannot Find Information about Travel Time'
        
        elif get == 'distance':
            nodes += f'&annotations={get}'
            newURL = tableURL + nodes
            r = requests.get(newURL)
            info = json.loads(r.content)
            try:
                if distUnit == 'm':
                    return np.array(info['distances'])
                elif distUnit == 'km':
                    return np.array(info['distances']) / 1000
            except:
                return 'Cannot Find Information about Distance'
        
        else:
            nodes += f'&annotations={get}'
            newURL = tableURL + nodes
            r = requests.get(newURL)
            info = json.loads(r.content)
            if timeUnit == 'second':
                timeArray = np.array(info['durations'])
            elif timeUnit == 'minute':
                timeArray = np.array(info['durations']) / 60
            elif timeUnit == 'hour':
                timeArray = np.array(info['durations']) / 60 / 60
            
            if distUnit == 'm':
                distArray = np.array(info['distances'])
            elif distUnit == 'km':
                distArray = np.array(info['distances']) / 1000
            
            return timeArray, distArray
    
    else:
        # 依據 get 參數決定回傳的值
        if get == 'duration':
            nodes += f'?annotations={get}'
            newURL = tableURL + nodes
            r = requests.get(newURL)
            info = json.loads(r.content)
            try:
                if timeUnit == 'second':
                    return np.array(info['durations'])
                elif timeUnit == 'minute':
                    return np.array(info['durations']) / 60
                elif timeUnit == 'hour':
                    return np.array(info['durations']) / 60 / 60
            except:
                return 'Cannot Find Information about Travel Time'
        
        elif get == 'distance':
            nodes += f'?annotations={get}'
            newURL = tableURL + nodes
            r = requests.get(newURL)
            info = json.loads(r.content)
            try:
                if distUnit == 'm':
                    return np.array(info['distances'])
                elif distUnit == 'km':
                    return np.array(info['distances']) / 1000
            except:
                return 'Cannot Find Information about Distance'
        
        else:
            nodes += f'?annotations={get}'
            newURL = tableURL + nodes
            r = requests.get(newURL)
            info = json.loads(r.content)
            if timeUnit == 'second':
                timeArray = np.array(info['durations'])
            elif timeUnit == 'minute':
                timeArray = np.array(info['durations']) / 60
            elif timeUnit == 'hour':
                timeArray = np.array(info['durations']) / 60 / 60
            
            if distUnit == 'm':
                distArray = np.array(info['distances'])
            elif distUnit == 'km':
                distArray = np.array(info['distances']) / 1000
            
            return timeArray, distArray
        
def distSeq(nodeList=None, matrix=None, sources=None, distUnit='m'):
    if matrix is None:
        matrix = odMatrix(nodeList, get='distance', sources=sources, distUnit=distUnit, timeUnit='second')
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

def travTimeSeq(nodeList=None, matrix=None, sources=None, timeUnit='second'):
    if matrix is None:
        matrix = odMatrix(nodeList, get='duration', sources=sources, distUnit='m', timeUnit=timeUnit)
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
