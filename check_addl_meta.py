## Currently not used
import pandas as pd
import argparse
from datetime import datetime
from traceback import print_exc

def  get_meta(meta):
    """
    Obtain metadata

    Parameters
    ---
    arg1: str
    	path to metadata csv

    Returns
    ---
    dataframe
    	metadata
    """
    meta = pd.read_csv(meta)
    return(meta)

def check_name(meta):
    """
    Checks that name is a variable in meta dataframe

    Find variable 'name' where case does not matter

    Parameters
    ---
    arg1: str
    	metadata csv

    Returns
    ---
    dataframe
    	
    """
    var = list(map(lambda x: x.lower(), meta.columns))
    if "name" not in var:
        print("ERROR: no variable defined as 'name' detected")
    else:
        print("Name variable identified")

def check_dates(meta):
    var = list(map(lambda x: x.lower(), meta.columns))
    date_list = meta[[s for s in var if "date" in s]].columns.tolist()
    if date_list:
        for date in date_list:
            try:
                pd.to_datetime(meta[date])
                print("Date identified columns okay")
            except Exception as e:
                print("Error with parsing date idetified column")
                print("type is:", e.__class__.__name__)
                print_exc()
    else:
        print("No date variables identified")
    


def main():
    parser = argparse.ArgumentParser()
    # required
    parser.add_argument("--addl_meta", type=str, required=True)
 
    args=parser.parse_args()

    meta = get_meta(args.addl_meta)
    check_name(meta)
    check_dates(meta)
    
if __name__ == "__main__":
    main()
