class MailCleaner:

    def __init__(self):
        pass

    # This function filters a dataframe to only include rows where name does not contain 
    # certain keywords. This is to avoid units from property shark not owned by individuals
    # params: df - pandas dataframe
    # returns: filtered dataframe
    def filter_names(self, df):
        names_to_remove = ['LLC', 'C/O', 'Trust', 'Inc', 'Corp', 'corp', 'holding', 'Holding', 'Ltd', 'LTD',
                            'L.L.C', 'Management', 'Associates', 'Limited', 'Company', 'Condominium', 'condominium',
                            'Architecture']
                            
        for name in names_to_remove:
            df = df[(df['Owner'].str.contains(name) == False)]

        return df

    # This function loops over the names column and reformats the names. It takes only the
    # first name and switches its order to first name -> last name. 
    # params: df - pandas dataframe
    # returns: dataframe with new name column
    def format_names(self, df):
        new_names = []
        for name in df['Owner']:
            line_split = name.splitlines()
            person_one = line_split[0]
            first_last_split = person_one.split(",")

            #Check if there is a split for names
            if len(first_last_split) > 1:
                reformatted_name = first_last_split[1] + ' ' + first_last_split[0]
            else:
                reformatted_name = first_last_split[0]
            
            new_names.append(reformatted_name.strip())
        
        df['Owner'] = new_names
        return df

    # This function removes units that have commas in them. e.g. Unit 12B, C. as
    # we encounter issues with Poplar when uploading these. This often means somebody owns
    # units 12B and 12C but not always so to be consistent we drop these units.
    # Also accounts for units such a 8C/D
    # params: df - pandas dataframe
    # retuns: dataframe with no multi-units. 
    def filter_multi_units(self, df):
        df = df[(df['Unit/Tax lot'].str.contains(',') == False)]
        return df[(df['Unit/Tax lot'].str.contains('/') == False)]

    # This function removes duplicates based on the name and unit number separately. i.e. it will
    # remove any row where there are more than one row with that name or unit. IMPORTANT: Cannot
    # apply to multiple files or you will remove all dupliate units between buildings
    # params: df - pandas dataframe
    # returns: dataframe with duplicates dropped
    def remove_duplicates(self, df):
        df.drop_duplicates(subset = ['Owner'], inplace=True)
        return df.drop_duplicates(subset = ['Unit/Tax lot'])


    # This function removes any specialty units in Property Shark 
    # (e.g. Parking Spaces, Commercial Units)
    # params: df - pandas dataframe
    # returns: dataframe with speciality units filtered out
    def remove_special_units(self, df):
        unit_types_to_remove = ['PK', 'RES', 'COMM', 'PH', 'STO']

        for remove in unit_types_to_remove:
            df = df[(df['Unit/Tax lot'].str.contains(remove) == False)]

        return df

    # This function deletes the columns passed to it
    # params: df - pandas dataframe
    # returns: dataframe with specificed columns deleted 
    def delete_cols(self, df):
        #Loop thru columns and delete all but owner and unit
        for col_name in df.columns.values.tolist():
            if (col_name != 'Unit/Tax lot') and (col_name != 'Owner'):
                del df[col_name]

        return df

    # This function deletes a specific unit based on user input. Its purpose it to 
    # remove the units that we have renovated in before
    # params: df - pandas dataframe, file_name - name of units file
    # returns: dataframe without the unit in it
    def delete_prev_unit(self, df, file_name):
        unit_input = input('For ' + str(file_name[28:-4]) +  ', What unit(s) have we renovated in before? (NOTE: Report multiple units with a comma -- e.g. 5B, 6G) ')
        prev_units = unit_input.upper().split(',')
        
        #If there is more than one unit passed in, then loop over the units
        if len(prev_units) > 1:
            for i in range(len(prev_units)):
                df = df[(df['Unit/Tax lot']).str.contains(prev_units[i]) == False]
            return df
        
        return df[(df['Unit/Tax lot']).str.contains(prev_units[0]) == False]  

    # This function creates a new column in the dataframe and populates it with what year the building is
    # based on user input
    # params: df - pandas dataframe, file_name - name of units file
    # returns: dataframe with a populated year column
    def populate_year(self, df, file_name):
        post_or_pre = input('What building year is ' + str(file_name[28:-4]) + " NOTE: Type either 'Pre-War' or 'Post-War'")
        df['Building Year'] = [post_or_pre] * len(df)
        
        return df

    # This function creates a new column in the dataframe and populates it with a formatted
    # address of the building. 
    # params: df - pandas dataframe, file_name - name of units file
    # returns: dataframe with a populated address column
    def populate_address(self, df, file_name):
        #Get address from file name - 28 is where the 'Units and Parcels...' part ends
        full_address = file_name[28:-8].split(',')

        #Strip and format
        street = full_address[0].strip()
        city = full_address[1].strip()
        state = full_address[2].split(' ')[1].strip()
        zip_code = full_address[2].split(' ')[2].strip()

        #Create lists to populate columns
        street_col = [street] * len(df)
        city_col = [city] * len(df)
        state_col = [state] * len(df)
        zip_col = [zip_code] * len(df)
        
        df['Address'] = street_col
        df['City'] = city_col
        df['State'] = state_col
        df['Zip Code'] = zip_col
        
        return df


    