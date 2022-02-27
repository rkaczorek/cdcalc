#!/usr/bin/env python3
# coding=utf-8

#  Copyright(c) 2022 Radek Kaczorek  <rkaczorek AT gmail DOT com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License version 3 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; see the file COPYING.LIB.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.
#
# This library uses online HyperLeda database: http://leda.univ-lyon1.fr/
# Online querying is documented here: http://leda.univ-lyon1.fr/fullsql.html
# Example query: http://leda.univ-lyon1.fr/fG.cgi?n=meandata&c=o&of=1,leda,simbad&nra=l&nakd=1&d=modz%2Cmod0%2Cmodbest&sql=objname%3D%27IC3943%27&ob=&a=csv[';']

import sys, requests

if len(sys.argv) < 2:
    print('Missing file argument')
    sys.exit(1)

filename = sys.argv[1]

api = "http://leda.univ-lyon1.fr/fG.cgi"

def getDistance(object):

    # prepare object
    objectarg = 'objname=\'' + object + '\''

    # prepare query
    table = 'meandata'
    fields = 'objname,modz,mod0,modbest'
    delimiter = ';'
    format = 'csv[' + delimiter + ']'
    args = {'n': table, 'c':'o', 'of':'1,leda,simbad', 'nra':'l', 'nakd':'1', 'd': fields, 'sql': objectarg, 'ob':'', 'a': format}

    # query database
    ret = requests.get(url = api, params = args)

    # check query status
    if ret.status_code != 200:
        print('Error connecting to HyperLeda database')
        return

    # parse query results
    results  = ret.text
    data = []
    lines = results.split('\n')

    # load to list
    for line in lines:
        if '#' in line:
            continue
        if len(line) > 1:
            data.append(line.split(delimiter))

    # return if no data
    if len(data) == 0:
        return 0

    # remove headers
    data.pop(0)

    # calculate distance in Mly
    for obj in data:
        if obj[3]:
            distanceMLy = 3.26163344 * 10 ** ((float(obj[3]) - 25) / 5)
        elif obj[2]:
            distanceMLy = 3.26163344 * 10 ** ((float(obj[2]) - 25) / 5)
        elif obj[1]:
            distanceMLy = 3.26163344 * 10 ** ((float(obj[1]) - 25) / 5)
        else:
            distanceMLy = 0

    return distanceMLy

def main():
    # open source file
    fd = open(filename, 'r')
    lines = fd.readlines()

    # parse source file to list
    objects = []
    for line in lines:
        if len(line) == 0 or ';' not in line or 'Name' in line:
            continue
        objects.append(line.strip().split(';')[0])

    galaxycount = len(objects)
    maxdist = 0
    maxdistgalaxy = 'none'

    print("Querying online database", end = '', flush = True)

    # check distances
    for obj in objects:
        print(".", end = '', flush = True)
        distance = getDistance(obj)
        if distance > maxdist:
            maxdist = distance
            maxdistgalaxy = obj

    print()
    print('Galaxies found: %d' % galaxycount)
    print('Most distant: %s' % maxdistgalaxy)
    print('Distance: %f Mly' % maxdist)

if __name__ == '__main__':
    main()
