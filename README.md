# Name Anonymizer

This script helps to automate anonymizing texts by replacing person
names with tags, thus preserving syntactic relationships between subjects, 
while removing their specific referents. In the current version these tags 
are "proper_name_0", "proper_name_1", "proper_name_2" etc. Batch processing is 
supported and the script operates on the directory level by processing all '.txt' 
files in an input directory sequentially. The files in the input directory should
each contain one text that has person names that need replacing. To get started,
run the following at the Terminal prompt for Python 2.7:
    
    $ python name_replace.py --input test_batch_input --debug True

or (for Python 3.x)

    $ python3 name_replace.py --input test_batch_input --debug True

-------------------------------

Capitalized, lowercase, and possessive forms of names are all found and replaced, 
provided they exist in English names file. Using the debug flag, empty input and 
failed conversions are able to be tracked and reported. Running with --debug True 
is recommended for the first run to find any such bad input files. 

-------------------------------

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

- 1: 1072
- 2: 664
- 3: 585
- 4: 303
