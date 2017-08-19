#!/usr/bin/env python3
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
is recommended for the first run to find any such bad input files. 

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
import time # Calculates script runtime
import name_utils # Collection of helper functions in the utils file

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

# Level of homographs to filter
# Force setting to 4 if invalid option is passed
TOLERANCE = '4' if int(OPTIONS.tolerance) not in {1,2,3,4} else OPTIONS.tolerance 

# Ensure input directory exists, otherwise the script exits
assert os.path.isdir(INPUT_DIR), \
        "The input directory doesn't exist in the working directory"

# Default name for output directory, change if needed
OUTPUT_DIR = './renamed_output'
# Check if output directory exists, otherwise create one
if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
    

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
    debug = name_utils._str_to_bool(debug)
    verbose = name_utils._str_to_bool(verbose)
    
    # Initialize generator that fetches input files one by one
    input_fetcher = glob.iglob('{}/*.txt'.format(input_dir))
    
    # Fetch list of english names
    en_names = name_utils._fetch_names(tolerance)
    
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
        
        # Create a path for the output file in the output directory
        # Flag each output file with '--RENAMED', indicating that all
            # person names in the passages have been anonymized
        current_output = '{}--RENAMED.txt'.format(os.path.join(OUTPUT_DIR,
            os.path.split(current_input)[1][:-4]))
     
        attempted_files += 1 # Increment prior to processing
        
        # 
        split_passage = name_utils._read_input(current_input)
 
        # Check input to ensure that each file contains content before sending 
            # to parser. Skip and log files that don't meet this criteria
        if not split_passage:
            # Display bad input file
            if verbose:
                print("* ".rjust(2) + "No text was found in {}. "
                      "Nothing to convert.".format(current_input))
                # Log bad input file for later
                if debug:
                    bad_input_files.append(current_input)
            continue

        rebuilt_passage = name_utils.replace_names(split_passage, en_names)
        
        # Write new passage to file in output directory at the path
            # specified in current_output variable
        with open(current_output, 'w') as file_handle:
            file_handle.write(rebuilt_passage)
        # Display where current output file is located on the local file system
        if verbose:
            print("*".rjust(5), "\t", current_input, ">>>", current_output)
        
        # Increment upon successful processing of current input file
        completed_files += 1
    
    # Main loop ends
    end_time = time.time() # Runtime ends
    # Output Report
    if verbose:
        print("\n--------------------------------------------\n"
              "Conversion complete using tolerance level {0}\n"
              "{1} of {2} files converted in {3} seconds\n"
              "--------------------------------------------\n".format(TOLERANCE,
                  completed_files, attempted_files, round((end_time - start_time), 2)))
    
        # Output any bad input files to the console
            # Only works when debug=True
        if bad_input_files:
            print("These files had no content:")
            for item in bad_input_files:
                print("*".rjust(5), "\t", item)
     
    # Exit
    return 
    
# Standard code that allows the file to be run as a script from the terminal   
if __name__ == '__main__':
    name_replacer(INPUT_DIR, debug=DEBUG, verbose=VERBOSE, tolerance=TOLERANCE)
