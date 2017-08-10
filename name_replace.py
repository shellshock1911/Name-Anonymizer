#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""This script helps to automate anonymizing texts by replacing person
names with tags, thus preserving syntactic relationships between subjects, 
while removing their specific referents. In the current version these tags 
are "proper_name_0", "proper_name_1", "proper_name_2" etc. Batch processing is 
supported and the script operates on the directory level by processing all '.txt' 
files in an input directory sequentially. The files in the input directory should
each contain one passage / text that has person names that need replacing.

Capitalized, lower case, and possessive forms of names are all found and replaced,
provided they exist in English names file. Using the debug flag, empty input and 
failed conversions are able to be tracked and reported. Running with --debug True 
is recommended for the first run to find any such bad input files. Because the 
core function involves a nested for loop, time complexity is quadratic. Script 
has been tested on 1000 files with a runtime of roughly 1.3 minutes and 28,000 
files with a runtime of roughly 38.5 minutes.

At a broad level, the success of the output can be interpreted as a trade-off
between false positives and false negatives. False positives occur when a true 
word is incorrectly replaced, e.g. South America becomes South proper_name_0. 
False negatives occur when a true name fails to be replaced, e.g. Charlotte 
remains Charlotte instead of receiving a proper_name tag. False negatives
generally appear more desirable than false positives, however the desired 
balance of each depends on specific usage contexts. In order to tune the balance, 
four homographic name files have been included that create this functionality.
Setting the --tolerance level to 1 will favor false negatives while setting it 
to 4 will favor false positives. The default level is 3. For a more transparent
idea about how this works, the amount of homographic names that are ignored
at each tolerance level are provided below:

1: 1072
2: 664
3: 585
4: 303

"""

import glob # Allows batch input file fetching
import os   # Allows convenient file handling
import re # Used to parse input file
import string # Contains list of English punctuation
import time # Calculates script runtime

# Remembers order in which names are matched in a text
from collections import OrderedDict 

# Allows parsing of user-specified options at script call
from optparse import OptionParser 

# Initialize parser, then add four arguments. Input is required, 
# debug, verbose, and tolerance are optional.
PARSER = OptionParser()

PARSER.add_option('-i', '--input', dest='input_directory',
                  help='input directory with files that need to be converted')
PARSER.add_option('-d', '--debug', dest='debug', default="False",
                  help='find and display files that fail conversion')
PARSER.add_option('-v', '--verbose', dest='verbose', default="True",
                  help='toggle console output')
PARSER.add_option('-t', '--tolerance', dest='tolerance', default="3",
                  help=r'tune fault tolerance (1: low / 4: high)')

OPTIONS, _ = PARSER.parse_args() # Convert options into usable strings

# Load user options into global constants for use in the script
INPUT_DIR = OPTIONS.input_directory # Directory containing input files (required)
DEBUG = OPTIONS.debug # Help user track sources of error (optional)
VERBOSE = OPTIONS.verbose # Display console output (optional)
TOLERANCE = OPTIONS.tolerance # Level of homographs to filter

# Ensure input directory exists, otherwise the script exits
assert os.path.isdir(INPUT_DIR), \
        "The input directory doesn't exist in the working directory"

# Check if output directory exists, otherwise create one
OUTPUT_DIR = './output'  # Default name for output directory, change if needed
if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)   
    
# Necessary for converting True and False option strings into booleans
# that Python requires for use inside Main Function
def _str_to_bool(option):

    # Should not be used outside scope of Main Function
    if option == 'True':
        return True
    elif option == 'False':
        return False
    else:
        raise ValueError("Options can only be True or False")

##### Main Function #####
def name_replacer(input_dir, debug='False', verbose='True', tolerance='3'):
    
    """Takes an input directory and processes all .txt files within, replacing 
    person names in each input text with their respective matches in an English 
    names list. Outputs to a separate directory new files where all names of 
    persons have been replaced with 'proper_name_0', 'proper_name_1', '
    proper_name_2', etc., based on the order in which they are first located 
    in the input text.
    
    `input_dir` = name of directory that contains input .txt files
    `debug` = reports files that contain bad input (default False)
    `verbose` = toggles console output (default True)
    'tolerance` = tunes level of fault tolerance from 1 to 4 (default 3)
        1 results in more false negatives (some names failing to be replaced)
        4 results in more false positives (some words being incorrectly replaced)
        
    """ 
    start_time = time.time() # Start runtime
    
    # Set debug and verbose flags for use throughout
    debug = _str_to_bool(debug)
    verbose = _str_to_bool(verbose)
    
    # Initialize generator that fetches input files one by one
    input_fetcher = glob.iglob('{}/*.txt'.format(input_dir))
    
    # Prepare list of homographic names that could cause matching issues
    with open('homographs/{}.txt'.format(tolerance), 'r') as homograph_handle:
        homograph_names = homograph_handle.read().split()
    
    # Prepare unfiltered list of 5163 English names
    with open('english_names.txt', 'r') as names_handle:
        en_names = names_handle.read().split()
    # Filter out names that are homographs
    en_names = [name for name in en_names if name not in homograph_names]
    # Extend list to include capitalized form of each name
    en_names = en_names + [name.capitalize() for name in en_names]
    
    # Script begins
    if verbose:
        print("\n-------------------\n"
              "Conversion starting\n"
              "-------------------\n")
        
    attempted_files = 0 # Track how many files attempted conversion
    completed_files = 0 # Track how many files converted successfully
    bad_input_files = [] # Store any bad input files
    
    # Main loop that batch processes input files 
    while input_fetcher:
        try:
            current_input = next(input_fetcher) # Fetch next input file
        except StopIteration:
            break # Execute when there are no more files to fetch
        
        # Create a path for the output file in the output directory.
        # Flag each output file with '--RENAMED', indicating that all
            # person names in the passages have been anonymized.
        current_output = 'output/{}--RENAMED.txt'.format(
            os.path.split(current_input)[1][:-4])
     
        # Increment prior to actual processing
        attempted_files += 1

        # Read in input file into a string. 
            # No parsing of punctuation or new line characters is involved.
        with open(current_input, 'r') as input_handle:
            passage = input_handle.read()
            
        # Split passage into alphanumeric, whitespace, and punctuation tokens
        split_passage = re.findall(r'\w+|\s|[{}]'.format(
                string.punctuation), passage)
        
        # Check input to ensure that each file contains content before sending 
            # to parser. Skip and log files that don't meet this criteria.
        if not split_passage:
            # Display bad input file
            if verbose:
                print("* ".rjust(2) + "No text was found in {}. "
                      "Nothing to convert.".format(current_input))
                # Log bad input file for later
                if debug:
                    bad_input_files.append(current_input)
            continue

        ## Core Function ##
        
        matched_names = OrderedDict() # Maintain order of matched names
        for token in split_passage: # Pull next token from the passage
            if token in en_names: # Token is an English name
                matched_names[token] = 1 # Add it to matched_names
                
        matched_names = list(matched_names) # Make matched_names indexable
        # The outer index i represents order in which names were matched.
            # Outer index is used for renaming persons to 'proper_name_i'.
        for i, name in enumerate(matched_names):
            # Matching tokens by inner index j allows exact matching only.
                # E.g. "Bea" will only match "Bea" but not "Beatles".
            for j, token in enumerate(split_passage):
                if name == token: # Match is found at inner index
            # Replace name at inner index with 'proper_name_i' at outer index
                    split_passage[j] = "proper_name_{}".format(i) 
                    
        # Rebuild passage from new tokens
        new_passage = ''.join(split_passage)
                    
        ##    ##    ##    ##
        
        # Write new passage to file in output directory at the path
            # specified in current_output variable
        with open(current_output, 'w') as file_handle:
            file_handle.write(new_passage)
        # Display where current output file is located on the local file system
        if verbose:
            print "*".rjust(5), "\t", current_input, ">>>", current_output
        
        # Increment upon successful processing of current input file
        completed_files += 1
    
    # Main loop ends
    end_time = time.time() # Runtime ends
    duration = end_time - start_time # Runtime calculated
    # Output Report
    if verbose:
        print("\n--------------------------------------------\n"
              "Conversion complete\n"
              "{0} of {1} files converted in {2} minutes\n"
              "--------------------------------------------\n".format(
                  completed_files, attempted_files, round(duration / 60, 3)))
    
        # Output any bad input files to the console
            # Only works when debug=True
        if bad_input_files:
            print "These files had no content:"
            for item in bad_input_files:
                print "*".rjust(5), "\t", item
     
    # Exit
    return 
    
# Standard code that allows the file to be run as a script from the terminal   
if __name__ == '__main__':
    name_replacer(INPUT_DIR, debug=DEBUG, verbose=VERBOSE, tolerance=TOLERANCE)
