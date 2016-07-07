"""
usage: gene_expression_munger.py [-h] [-f FILES [FILES ...]] [-c] [-t]
                                 [-o OUTPUT_FILENAME] [-r FILE_INDEX]
                                 [-d DATA_TYPE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        TCGA Gene Expression TXT files
  -c, --csv
  -t, --transpose
  -o OUTPUT_FILENAME, --output_filename OUTPUT_FILENAME
  -r FILE_INDEX, --file_index FILE_INDEX
"""

import pandas as pd
import argparse
import sys

def get_dataframe_list(files, file_index, data_fields=('gene', 'raw_counts')):
    """ get a list of dataframes from -f or -r """

    # if you passed files to munger.py via -f, set them as the files variable
    files = files or []

    # if you have an index as the file pointer, use this to get the files
    if file_index:
        with open(file_index) as fp:
            files.extend(fp.readlines())
    sorted_files = sorted(filter(None, set([f.strip() for f in files])))

    # now iterate over the files and get the list of dataframes
    dfs = []
    for f in sorted_files:
        # Get only specific columns you want with 'usecols'
        # if you do not find the data_fields in this file, continue onto next item
        try: dfs.append(pd.read_table(f, usecols=data_fields))
        except: continue
    return dfs, sorted_files # a list of dataframes and the files index

def get_metadata_tag(filename):
    """ Gets a filename (without extension) from a provided path """
    UNCID = filename.split('/')[-1].split('.')[0]
    TCGA = filename.split('/')[-1].split('.')[1]
    return TCGA

def merge_texts(files, file_index):
    """ merge the dataframes in your list """
    dfs, filenames = get_dataframe_list(files, file_index)
    # rename the columns of the first df
    df = dfs[0].rename(columns={'raw_counts': 'raw_counts_' + get_metadata_tag(filenames[0])})
    # enumerate over the list, merge, and rename columns
    for i, frame in enumerate(dfs[1:], 2):
        try: df = df.merge(frame, on='gene').rename(columns={'raw_counts':'raw_counts_' + get_metadata_tag(filenames[i-1])})
        except: continue
    return df

def save_csv(df, csv, output_filename, filename, header_opt=False, index_opt=False):
    """ if csv is true and an output filename is given, rename """
    # there is a default filename, so it should pass if --csv is True
    if csv and output_filename:
        return df.to_csv(path_or_buf=filename, header=header_opt, index=index_opt)

def get_transpose(df):
    """ get the transpose of your matrix (index by case) """
    df_transpose = df.transpose()
    df_transpose = df_transpose.rename(index = {'gene':'case'})
    return df_transpose

def main(files, csv, transpose, output_filename, file_index, data_type):
    """ main: get a concise matrix/df of RNAseq raw counts indexed by gene (and case) """
    df_gene = merge_texts(files, file_index)
    save_csv(df_gene, csv, output_filename, filename=str(output_filename) + '_by_gene.csv', header_opt=True)
    if transpose:
        save_csv(get_transpose(df_gene), csv, output_filename, filename=str(output_filename) + '_by_case.csv',
                                        header_opt=False, index_opt=True)
    return df_gene

if __name__ == "__main__":
    # Parse your args
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", help="TCGA Gene Expression TXT files", nargs="+")
    parser.add_argument("-c", "--csv", action="store_true", default=False)
    parser.add_argument("-t", "--transpose", action="store_true", default=False)
    parser.add_argument("-o", "--output_filename", type=str, default="GEX_dataframe")
    parser.add_argument("-r", "--file_index", type=str, default=None)
    parser.add_argument("-d", "--data_type", type=str, default="gene")
    args = vars(parser.parse_args())

    files = args['files']
    csv = args['csv']
    transpose = args['transpose']
    output_filename = args['output_filename']
    file_index = args['file_index']
    data_type = args['data_type']

    # Check to make sure you have your files or indices (XOR)
    if not files and not file_index:
        parser.print_help()
        sys.exit(0)

    df = main(files, csv, transpose, output_filename, file_index, data_type)