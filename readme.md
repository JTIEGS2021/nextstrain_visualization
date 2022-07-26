# Readme for get_meta and json adjust

Input: 
	Five inputs:
	- NCBI metadata csv
		- Default, no user input required
	- DCIPHER metadata csv
		- Default, no user input required
	- Meta Variable Selection
		- Default set of meta variables from the default set of metadata variables
		- Optional users can adjust meta variables to use
		- Full list of possible variables to select from found here [[]]
	-  Additional metadata file [optional]
		- Requirments:
			- CSV format
			- Variable 'name' contain the srr ids of the isolates of interest.
				NOTE: all isolates included in the FASTA input required to be added to the additional metadata CSV. If metadata is not available for specific isolates include the isolate with blanks for missing fields.
	- Meta_date [optional]
		- A character input that can be used to select the date used as the timeline creation.
		- Must match a variable name in either the default metadata or the additional metadata.
		- Default if not given is to select a 'date' named variable from the default metadata.
		
				
   
	
