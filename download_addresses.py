import pandas as pd
import os
import datetime
from mailcleaner import MailCleaner
from fileordering import *


### Driver code ###
if __name__ == "__main__":
    #Link to directory of files to clean
    file_path =  input("What's the absolute file path where you are storing the files?: ")
    directory = r'{}'.format(file_path)
    
    #convert xls files to csv 
    print('Converting excel files to csv...')
    for file_name in os.listdir(directory):
        print(file_name)
        if file_name[-3:] != 'xls':
            continue

        convert_to_csv(file_name)
    
    #Create empty dataframes 
    manhattan_df = pd.DataFrame(columns = ['Address 2', 'Name', 'Address', 'City', 
    'State', 'Zip Code', 'Building Year'])

    brooklyn_df = pd.DataFrame(columns = ['Address 2', 'Name', 'Address', 'City', 
    'State', 'Zip Code', 'Building Year'])

    unknown_df = pd.DataFrame(columns = ['Address 2', 'Name', 'Address', 'City', 
    'State', 'Zip Code', 'Building Year'])

    #Loop over the directory and apply a cleaner to each
    for file_name in os.listdir(directory):
        #Skip the non-csv version of the file
        if file_name[-3:] != 'csv':
            continue

        #Read in the dataframe and the cleaner file
        df = pd.read_csv(file_path + '/' + file_name)
        print('\n')
        print('original data for ' + file_name[28:-4] + ' has ' + str(df.shape[0]) + ' rows')

        #Create cleaner
        cleaner = MailCleaner()

        #Clean data
        df = cleaner.filter_names(df)
        df = cleaner.format_names(df)
        df = cleaner.remove_duplicates(df)
        df = cleaner.remove_special_units(df)
        df = cleaner.filter_multi_units(df)
        df = cleaner.delete_cols(df)
        df = cleaner.delete_prev_unit(df=df, file_name=file_name)
        df = cleaner.populate_address(df, file_name)
        df = cleaner.populate_year(df=df, file_name=file_name)

        #Rename columns to match sheets  
        df.rename(columns={"Unit/Tax lot": "Address 2", "Owner": "Name"}, inplace=True)

        print('cleaned data for ' + file_name[28:-4] + ' has ' + str(df.shape[0]) + ' rows')
        
        
        print('appending data ...')
        #Switch over the address to find proper df (Brooklyn, Manhattan or Unkonwn')
        if 'Brooklyn' in df['City'].values.tolist():
            brooklyn_df = brooklyn_df.append(df)
        elif 'New York' in df['City'].values.tolist():
            manhattan_df = manhattan_df.append(df)
        else:
            unknown_df = unknown_df.append(df)

        print('---------------------------------------------')

    #Get time to create a unique file each time
    time = str(datetime.datetime.now())[0:19].replace(':', '-')
   
    #Print and Download data based on time stamp
    #Manhattan
    print('Manhattan Data: ')
    print(manhattan_df)
    manhattan_df.to_csv('manhattan_data - ' + time + '.csv')
    print('\n')

    #Brooklyn
    print('Brooklyn Data: ')
    print(brooklyn_df)
    brooklyn_df.to_csv('brooklyn_data - ' + time + '.csv')
    print('\n')

    #Unknown
    print('Uncategorized Data: ')
    print(unknown_df)
    unknown_df.to_csv('unknown_data - ' + time + '.csv')

    
