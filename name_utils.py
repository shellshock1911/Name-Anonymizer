#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re # Used to parse input file
import string # Contains list of English punctuation

# Remembers order in which names are matched in a text
from collections import OrderedDict 

def _str_to_bool(option):
    """Converts True and False option strings to booleans."""
    
    if option == 'True':
        return True
    elif option == 'False':
        return False
    else:
        raise ValueError("Options can only be True or False")
        
def _fetch_names(tolerance):
    """Fetches set of lowercase English names, filters out homographs, and 
    adds capitalized version of each one."""

    # Prepare set of homographic names that could cause matching issues
    with open('homographs/{}.txt'.format(tolerance), 'r') as homograph_handle:
        homograph_names = set(homograph_handle.read().split())
        
    # Prepare unfiltered set of 5,163 English names
    with open('english_names.txt', 'r') as names_handle:
        en_names = set(names_handle.read().split())
        
    # Filter out names that are homographs, leaving 4,577 names
    en_names = {name for name in en_names if name not in homograph_names}
    # Extend set to include capitalized form of each name
    en_names = en_names | {name.capitalize() for name in en_names}

    return en_names

def _read_input(input_file):
    """Reads input file and prepares text for name replacing."""
    
    # Read in input file into a string 
    with open(input_file, 'r') as input_handle:
        passage = input_handle.read()
            
    # Split passage into alphanumeric, whitespace, and punctuation tokens
    split_passage = re.findall(r'\w+|\s|[{}]'.format(
        string.punctuation), passage)

    return split_passage
  
def replace_names(tokens, name_list):
    """Replaces names in text with anonymous tags."""
    
    matched_names = OrderedDict() # Maintain order of matched names
    for token in tokens: # Pull next token from the passage
        if token in name_list: # Token is an English name
            matched_names[token] = 1 # Add it to matched_names
                
    matched_names = list(matched_names) # Make matched_names indexable
    
    # The outer index i represents order in which names were matched.
        # Outer index is used for renaming persons to 'proper_name_i'.
    for i, name in enumerate(matched_names):
        # Matching tokens by inner index j allows exact matching only.
            # E.g. "Bea" will only match "Bea" but not "Beatles".
        for j, token in enumerate(tokens):
            if name == token: # Match is found at inner index
                # Replace name at inner index with 'proper_name_i' at outer index
                tokens[j] = "proper_name_{}".format(i)  
                
    # Rebuild passage from new tokens
    rebuilt_passage = ''.join(tokens)

    return rebuilt_passage