"""
usage: munger.py [-h] [-f FILES [FILES ...]] [-r INDEX_FILE] [-c] [-o OUTPUT_FILENAME]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        TCGA Gene Expression TXT files
  -c, --csv
  -r FILE_INDEX         A file with input files, one each line. Merged with -f files.
  -o OUTPUT_FILENAME, --output_filename OUTPUT_FILENAME
"""

import pandas as pd
import argparse
import sys

# To read TXT files:
# df = pd.read_table(filename)
# To read MAF files:
# df = pd.read_table(filename, skiprows=1) # to skip the version row

def get_dataframe_list(args_files, args_file_index, data_fields=('gene', 'raw_counts')):
    """ get a list of dataframes from -f or -r """

    # if you passed files to munger.py via -f, set them as the files variable
    files = args_files or []

    # if you have an index as the file pointer, use this to get the files
    if args_file_index:
        with open(args_file_index) as fp:
            files.extend(fp.readlines())
    files = sorted(filter(None, set([f.strip() for f in files])))

    # now iterate over the files and get the list of dataframes
    dfs = []
    for f in files:
        # Get only specific columns you want with 'usecols'
        # if you do not find the data_fields in this file, continue onto next item
        try:
            dfs.append(pd.read_table(f, usecols=data_fields))
        except:
            continue
    return dfs, files # a list of dataframes and the files index

def get_metadata_tag(filename):
    """ Gets a filename (without extension) from a provided path """
    UNCID = filename.split('/')[-1].split('.')[0]
    TCGA = filename.split('/')[-1].split('.')[1]
    return TCGA

def merge_texts(args_files, args_file_index):
    """ merge the dataframes in your list """
    dfs, filenames = get_dataframe_list(args_files, args_file_index)
    # rename the columns of the first df
    df = dfs[0].rename(columns={'raw_counts': 'raw_counts_' + get_metadata_tag(filenames[0])})
    # enumerate over the list, merge, and rename columns
    for i, frame in enumerate(dfs[1:], 2):
        try:
            df = df.merge(frame, on='gene').rename(columns={'raw_counts':'raw_counts_' + get_metadata_tag(filenames[i-1])})
        except:
            continue
    return df

def get_csv(df, args_csv=None, args_output_filename=None, filename='GEX_dataframe.csv', header_opt=False, index_opt=False):
    """ if csv is true and an output filename is given, rename """
    # there is a default filename, so it should pass if --csv is True
    if args['csv'] and args['output_filename']:
        return df.to_csv(path_or_buf=filename, header=header_opt, index=index_opt)

def get_transpose(df):
    """ get the transpose of your matrix (index by case) """
    df_transpose = df.transpose()
    df_transpose = df_transpose.rename(index = {'gene':'case'})
    return df_transpose

def main(args):
    """ main: get a concise matrix/df of RNAseq raw counts indexed by gene (and case) """
    df_gene = merge_texts(args['files'], args['file_index'])
    get_csv(df_gene, args['csv'], args['output_filename'], filename=str(args['output_filename']) + '_by_gene.csv', header_opt=True)
    if args['transpose']:
        get_csv(get_transpose(df_gene), args['csv'], args['output_filename'], filename=str(args['output_filename']) + '_by_case.csv', header_opt=False, index_opt=True)
    return df_gene

if __name__ == "__main__":
    # Parse your args
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", help="TCGA Gene Expression TXT files", nargs="+")
    parser.add_argument("-c", "--csv", action="store_true", default=False)
    parser.add_argument("-t", "--transpose", action="store_true", default=False)
    parser.add_argument("-o", "--output_filename", type=str, default="GEX_dataframe")
    parser.add_argument("-r", "--file_index", type=str, default=None)
    args = vars(parser.parse_args())

    # Check to make sure you have your files or indices (XOR)
    if not args['files'] and not args['file_index']:
        parser.print_help()
        sys.exit(0)

    df = main(args)