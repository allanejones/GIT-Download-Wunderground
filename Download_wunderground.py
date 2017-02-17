##
## This script establishes and calls the function which downloads the data from
## Weather Underground.
##
## Must write function first, then write scripted call.
##
## Author: Allan Jones
## Date: 2/6/2015
##


## defining the function to download the wunderground data
def WUG_download(stationID =  'KORPORTL26', begin_date = 'today',
                 end_date = 'today', savefileID = 'unspecified',
                 file_directory = 'current', airportID = 'unspecified'):
    """\
Basic input:
WUG_download(stationID =  'KORPORTL26', begin_date = 'today',
                 end_date = 'today', savefileID = 'unspecified',
                 file_directory = 'current', airportID = 'unspecified'):

This script (written for Python2.7) is desgined to download the weather
data from personal weather stations (PWSs) from wunderground.com. The
data is then saved in a .csv file for later retrieval.

Description of inputs:  ALL INPUTS ARE STRINGS.
The inputs are preset to retrieve all available data for today for PWS
KORPORTL26 and save it in the current directory with the default
filename. ALL INPUTS ARE STRINGS.

All inputs should be strings. 'stationID' is the ten-digit alphanumeric
identification string for each site.

'begin_date' is a string denoting the earliest time from which to retreive
data. All dates should be specified as followed 'YYYY-MM-DD'. An example
of an acceptable 'begin_date' would be '2007-10-01'.

The 'end_date' signifies the end of the time period for data retrieval. The
string 'end_date' may either be a specified date (format 'YYYY-MM-DD') or
a the string 'today', where the script will use the current date. As a
warning when using 'today' as the 'end_date' the wunderground download will
only include data until the time of your query. For example, if you ask for
the data at 1200 PM, the returned data will be all data before 1200 PM on
today's date.

The 'savefileID' input will allow you to specify the
filename of the data to be saved. If no file name is specified, the
default filename will be:
[stationID+'_data_from_'+begin_date+'_to_'+end_date+'.txt'].

'file_directory' allows the user to specify the directory of the
file-to-be-saved. When specifying a file directory, make sure to include
"\\" for every backslash in the directory. If no file directory is specified,
the file will save in the current directory. You may specify a file directory
that does not yet exist and the function will create it for you and save the
files accordingly (use this option with care).

'airportID' signifies the type of weather station from which you are
querying data. You need to clarify whether the 'stationID' you are passing
the function is associated with a PWS (use airportID = 'private') or an
airport (use airportID = 'airport'). If nothing is supplied the function
return an error.

Remember:
!!! ALL INPUTS ARE STRINGS !!!!
"""
    
    ### Imports
    print('Beginning download for site number: '+stationID+' \n')
    import urllib
    import re
    import os
    import sys
    import time
    from datetime import date, timedelta as td
    from bs4 import BeautifulSoup
    from bs4 import NavigableString

    ## find begin_date and end_date, if default 'today is used
    time_fmt = "%Y-%m-%d"
    if end_date == 'today':
        end_date = time.strftime(time_fmt)

    if begin_date == 'today':
        begin_date =  time.strftime(time_fmt)

    print('The following dates are used to obtain information: \n'+
          'Begin date: ' + begin_date + '\n' +
          'Final date: ' + end_date + '\n')

    ## create list of days between begin and end date
    delta =  (date(int(end_date[:4]), int(end_date[5:7]), int(end_date[-2:]))-
              date(int(begin_date[:4]), int(begin_date[5:7]), int(begin_date[-2:])))
    date_list = []
    for iii in range(delta.days +1):
        date_list.append(date(int(begin_date[:4]), int(begin_date[5:7]), int(begin_date[-2:]))+
                         td(days = iii))

    ## looping through the date list and passing each date's information (day, month, year)
    ## to the URL for download
    counter = 1
    all_data = []
    for entry in date_list:
        day_num      = str(entry.day)
        month_num = str(entry.month)
        year_num     = str(entry.year)

        ## finding the proper airport Id to use
        if airportID.lower() == 'private':
            ## URL to use for downloading personal weather station (PWS) data
            URL = ('http://www.wunderground.com/weatherstation/WXDailyHistory.asp?'+
                'ID=' + stationID +
                '&day=' + day_num +
                '&month=' + month_num +
                '&year=' + year_num + '&graphspan=day&format=1')

        elif airportID.lower() == 'airport':
            URL = ('http://www.wunderground.com/history/airport/' + stationID +
            '/' + year_num + '/' + month_num + '/' + day_num +
            '/DailyHistory.html?&reqdb.magic=1&reqdb.wmo=99999&format=1')
            return
            
        elif airportID.lower() == 'unsecified':
            print('You must specify whether station ('+stationID+') is an "airport" or a '+
                  '"private" weather station. \n\n')
            return

        if counter == 1:
            print('Attempting access information via the following URL:'+'\n'+URL+'\n\n')

        ## accessing the URL and the source page data
        try:
            website          = urllib.urlopen(URL)
            source_page = website.read()
        except:
            print('There was an error with the connection. Try again later.'+'\n')
            return (stationID+'\tConnection issues...')
        
        ## checking that the text downloaded from page has actual data
        ## length of download should be longer than 300 characters
        if len(source_page) > 300:
            ## reformating all the data/information
            raw_lines = source_page.replace('\n','').split('<br>')

            # save first and last date (for saving) and first headers for writing the file
            if counter == 1:
                headers_line =  raw_lines[0]
                date_1 =  raw_lines[1][0:10]
                date_2 =  raw_lines[-2][0:10]
                
            elif counter == len(date_list):
                date_2 =  raw_lines[-2][0:10]

            ## appending all the raw lines after headers to the all_data list
            all_data.append(raw_lines[1:])

            # update the counter
            counter += 1

    ### WRITING THE DATA TO A FILE
    # concatenate final filename
    if savefileID == 'unspecified':
        savefileID = (stationID+'_weatherstationdata_from_'+date_1+
                     '_to_'+date_2+'.csv')

    ### Find current file directory
    if file_directory == 'current':
        file_directory = os.getcwd()

    ### Writing the data (string) to the file
    path_full = file_directory + '\\' + savefileID
    print('Finished downloading the data. Attempting to write it to file: \n'
          +path_full+'\n')
    try:
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)
        with open(path_full, "w") as file_out:
            file_out.write(headers_line +'\n')
            for days in all_data:
                for line in days:
                    file_out.write(line+'\n') # writing the data to the file
            print("The requested file has been written and saved. \n")
    except IOError as e:
        print("\nCould not write to file. \n")
        sys.exit(1)

### Returns the full directory path of the file saved so that you may
### easily call the saved file for subsequent analysis
    print('The following is the file directory of the downloaded data for site: '
          +stationID +'\n'+path_full +'\n')
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'+
          '%%% \n\n\n')
    #return path_full

            
    
        

        

###############################################################################
###############################################################################
###############################################################################
##                                                          FUNCTION OVER!!                                                            ##
###############################################################################
###############################################################################
###############################################################################
        
test = WUG_download(stationID = 'KWAVANCO175', begin_date = '2016-08-01',
                    airportID = 'private',
                    file_directory = 'C:\\Users\\geo-aej662\\Desktop\\')
