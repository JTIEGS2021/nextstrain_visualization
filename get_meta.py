import pandas as pd
import argparse
from datetime import datetime

# Read in data
def get_data(ncbi, aspen, select):
    meta_ncbi = pd.read_csv(ncbi)
    meta_aspen = pd.read_csv(aspen)
    meta_select = pd.read_csv(select, sep="\t")
    return(meta_ncbi, meta_aspen, meta_select)

# subset columns fromm meta_ncbi by meta_select
def get_sub(ncbi, select):
    meta_out = ncbi[select.columns.tolist()]
    return(meta_out)

# left join and filter on meta2
def get_filt(aspen, meta_ncbi2):
    out = aspen.merge(meta_ncbi2, left_on = "Sample name", right_on = "Run", how = "left")
    return(out)

# format dates as date
# finds all date columns and formats
def fix_date(meta_filt):
    date_list = meta_filt[[s for s in meta_filt.columns.tolist() if "date" in s]].columns.tolist()
    for i in date_list:
        meta_filt[i] = pd.to_datetime(meta_filt[i])

# Fix column names
# replace all " " with "_", then replace the extra variable "name" as "name2", then replace "sample_name" as "name" to allow augur functionality
def fix_name(meta_filt):
    meta_filt.rename(columns={"sample_name":"sample_name_pnu"}, inplace=True)
    meta_filt.rename(columns=lambda x: x.lower().replace(" ","_"), inplace=True)
    meta_filt.rename(columns={"sample_name":"name"}, inplace=True)


# Num date from date function
def num_date_from_date(dt):
   # dt = datetime.strptime(date, '%Y-%m-%d')
    year_dec = dt.timetuple().tm_yday / datetime(dt.year,12,31).timetuple().tm_yday
    num_date = dt.year + year_dec
    return num_date

# Add num_date to dataframe
def get_num_date(meta_filt):
    date_list = meta_filt[[s for s in meta_filt.columns.tolist() if "date" in s]].columns.tolist()
    date_name = date_list[0]
    # datel = meta_filt[date]
    meta_filt["num_date"] = meta_filt[date_name].apply(num_date_from_date)
    return(meta_filt)
    





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta_ncbi", type=str, required=True)
    parser.add_argument("--meta_aspen", type=str, required=True)
    parser.add_argument("--meta_select", type=str, required=True)

    args=parser.parse_args()

    # get data
    meta_ncbi, meta_aspen, meta_select = get_data(args.meta_ncbi, args.meta_aspen, args.meta_select)
    # subset columns
    meta_ncbi2 = get_sub(meta_ncbi, meta_select)
    # filter rows
    meta_filt = get_filt(meta_aspen, meta_ncbi2)
    # fix date
    fix_date(meta_filt)
    # fix names
    fix_name(meta_filt)
    # meta filt
    meta_filt = get_num_date(meta_filt)
    # write file
    meta_filt.to_csv("./meta_out.csv")

if __name__ == "__main__":
    main()
