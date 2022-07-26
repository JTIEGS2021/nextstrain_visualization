import argparse
from datetime import datetime
import json as js
import pandas as pd

def get_data(json, meta):
    """
    Obtains the metadata and json_export files from arg list

    The prior nextflow steps output a refined tree json and metadata csv.
    The metadata is used to get timeline measures and the tree is further refined to include num_date fields for each tree node

    Parameters
    ----
    arg1: str
	path to metadata csv
    arg2: str
    	path to tree json

    Returns
    ---
    dataframe
    	date_range - metadata as pandas dataframe
    dict
    	data - full data dict
    dict
    	node - tree json as nested dict
    """
    
    # load meta_out 
    meta1 = meta
    # get date_range from metadata
    date_range = [meta1["num_date"].min(), meta1["num_date"].max()]
    # load json
    f = open(json)
    data = js.load(f)
    # get node tree from json
    node = data["tree"]
    # return date_range and json node
    return (date_range, data, node)

# loads data if meta has no num_date
def get_data2(json):
    f = open(json)
    data = js.load(f)
    return(data)

    
def get_leaf_struc(node):
    """
    Finds first leaf node and captures a copy of the node_attrs structure
    
    Obtain the leaf node dictionairy structure to be used for reording the updated internal node dictionairy objects order.
    Recursively searches the nested dict, using the 'children' dict key to access nested child nodes.
    When leaf node is found, returns the node_attrs dict object 
        
    Parameters:
    ----
    arg1: dict
    	nested dictionairy from the tree json

    Returns:
    ---
    dict:
    	single dictionairy copy of the first leaf node node_attrs dictionairy object
    """

    for k in node:
        if "children" in k.keys():
            return get_leaf_struc(k["children"])
        else:
            return k["node_attrs"]
        break


def num_date_from_date(dt):

    """
    Formats date to float as year.date_proportion 

    Parameters:
    ----
    arg1: str
    	date as string

    Returns:
    ---
    arg2: float
    	date as float 
    """
    
    dt = datetime.strptime(dt, "%Y-%m-%d")
    year_dec = dt.timetuple().tm_yday / datetime(dt.year,12,31).timetuple().tm_yday
    num_date = dt.year + year_dec
    return num_date

def parse_div_max(node, div):
    """
    Recursive search for max divergence. Held in 'node_attrs'|'div'

    Parameters:
    ---
    arg1: dict
    	tree as nested dict
    arg2: int
    	div as float. Carries running div_max. Initiate with 0

    Returns
    ---
    float
    	div_max
    """
    
    div_max = div
    # for base node
    if isinstance(node, dict):
        div_return = parse_div_max(node["children"], div_max)
        if div_return > div_max:
            div_max = div_return
        return div_max
    # for nested nodes
    else:
        for k in node:
            if "children" in k.keys():
                div_max = parse_div_max(k["children"], div_max)
            if k["node_attrs"]["div"] > div_max:
                div_max = k["node_attrs"]["div"]
        return div_max
    

def parse_nested_node(node, node_ord):
    """
    Recursive addition of num_date dict object to internal node dict

    Recursively identifies internal nodes by 'children' dict object.
    num_date set as node min(date_range) + ((node div/div_max) * max(date_range) - min(date_range)) - (max(date_range)-min(date_range))
    	this is a proportional date based on proportional divergence per node, left shifted to one whole date range frame
    Updated node_attrs is arranged according to the leaf node order.
    
    Parameters
    ---
    arg1: dict
    	tree as nested dict
    arg2: dict
    	leaf node 'node_attrs' dict for arranging updated node structure

    Returns
    ---
    No object returned. Tree dict is updated inplace
    """
    
    for k in node:
        if "children" in k.keys():
            # get node_attrs
            l = k["node_attrs"]
            # get div
            div = k["node_attrs"]["div"]
            # set num_date
            date = date_range[0] + ((div/div_max) * (date_range[1]-date_range[0])) - (date_range[1] - date_range[0])
            # add num_date to dict
            l["num_date"] = {"value": date}
            # reorder dict
            # l = {k: l[k] for k in node_ord}
            # set updated node_attrs to the tree dict
            k["node_attrs"] = l
            # recursion
            parse_nested_node(k["children"], node_ord)
            # this shouldn't be needed
            # div = l["div"]


            
def parse_first_node(node, node_ord):
    """
    Updates the base node node with same method in parse_nested_node()
    Required because the base node is not in a list data structure
    """
    
    l = node["node_attrs"]
    div = node["node_attrs"]["div"]
    date = date_range[0] + ((div/div_max) * (date_range[1]-date_range[0])) - (date_range[1]-date_range[0])
    l["num_date"] = {"value": date}
    # l = {k: l[k] for k in node_ord}
    node["node_attrs"] = l
    


def parse_nodes(node, node_ord):
    """
    Group parse_first_node and parse_nested_node

    Parameters
    ---
    arg1:
    	tree as nested dict

    Returns
    ---
    No return, tree is updated inplace
    """
    
    parse_first_node(node, node_ord)    
    parse_nested_node(node["children"], node_ord)    


def write_json_out(data, json_out):
    """
    Write tree as nested dict to json file

    Parameters
    ---
    arg1: dict
    	updated tree as nested dict
    arg2: str
    	path to json_out from args
    """

    with open(json_out, "w") as f:
        js.dump(data, f, ensure_ascii=False, indent=4)




def main():
    """
    Script updates the tree json from prior nextflow outputs and updates the num_date field for each internal node
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=str, required=True)
    parser.add_argument("--meta", type=str, required=True)
    parser.add_argument("--json_out", type=str, required=True)


    args=parser.parse_args()
    global date_range, div_max

    # read in meta csv first to check if num_date exists
    meta = pd.read_csv(args.meta)
    if "num_date" in meta.columns:
        print("num date exists")
        # get data
        date_range, data, node = get_data(args.json, meta)
        # get json leaf node structure (outline)
        node_ord = list(get_leaf_struc(node["children"]).keys())
        # get div_max (div_dict can be ignored)
        div_max = parse_div_max(node, 0)

        if div_max == 0:
            div_max = 1
        
        # parse nodes
        parse_nodes(node, node_ord)
        # write json output
        write_json_out(data, args.json_out)
    else:
        print("num_date does not exist, returning json")
        # get data
        data = get_data2(args.json)
        # write json_output
        write_json_out(data, args.json_out)
       
    
    
if __name__ == "__main__":
    main()

pd.read_csv("./rst/meta_out.csv")
