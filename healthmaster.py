"""
healthmaster.py

A CLI tool to fetch and parse hospital chargemasters (i.e. billing list sent to insurance companies).

See README.md for future TODOs, usage, and explained purpose.

written by: Aristana Scourtas
last updated: 2/21/19

"""


from argparse import ArgumentParser, RawTextHelpFormatter
from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import urllib
import zipfile

"""
Dependencies:
    xlrd
    numpy

"""

def read_arguments():
    """
    Define and read in commandline arguments.

    :return: A tuple of the argument values.
    """
    # use argeparse with our own formatting for 'help' strings
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.description = "A commandline utility to fetch hospital chargemasters (i.e. billing lists to insurance \n" \
                         "companies). Use flags to optionally search for and output specific chargemaster items."
    parser.add_argument("-s", "--search", dest="pattern",
                                            help="The keyword or regex pattern to search for in the chargemaster \n"
                                                "descriptions. Case insensitive. \n\n"
                                                ""
                                                "Ex: 'python healthmaster.py -k colon' matches any data \n"
                                                "entry that contains the substring 'colon', such as: \n"
                                                "'colonoscopy', 'Colon', 'colonies'\n\n"
                                                ""
                                                "Ex: 'python healthmaster.py -k \\bcolon\\b will only \n"
                                                "match the substring 'colon' (still case insensitive)\n")

    parser.add_argument("-d", "--dest_dir", help="The full path to the directory to write the scraped files to.")
    parser.add_argument("-w", "--write_to_file", dest="out_path",
                                            help="The full filepath to a file to write the search results to. \n"
                                                 "If not specified, the results will be written to stdout.\n"
                                                 "Results are written as a formatted string.\n\n"
                                                 ""
                                                 "NOTE: Does NOT overwrite file; if you use the same filename\n"
                                                 "twice in a row, the results will be appended at the bottom.\n")
    parser.add_argument("-o", "--order_by", dest="sort_type",
                                            help="Orders the search results in designated manner. Options are:\n"
                                                 "\t- description -- orders by billing item description\n"
                                                 "\t\t alphanumerically.\n"
                                                 "\t- price, or price_l2h -- orders by price, low to high\n"
                                                 "\t- price_h2l -- orders by price, high to low\n")

    args = parser.parse_args()

    if args.dest_dir is None:
        dest_dir = "./output"
    else:
        dest_dir = args.dest_dir

    # create destination directory if necessary
    try:
        os.makedir(dest_dir)
    # makedir throws an exception if directory already exists; ignore it
    except:
        pass

    return (args.pattern, dest_dir, args.out_path, args.sort_type)


def fetch_zip_files(dest_dir, url, pattern):
    """
    Fetches and writes data files (.zip files, specifically) from links scraped from the url,
    given a designated link pattern to search for.

    :param dest_dir: The full destination folder path of the files.
    :param url: The webpage to scrape links for .zip files from.
    :param pattern: The regex pattern uses to match links on the page.
    :return: N/A
    """

    # get HTML dump from url
    html_page = urllib.urlopen(url)
    html_soup = BeautifulSoup(html_page, "html.parser")

    # match all links in the HTML dump that contain the designated regex pattern; these should be the zip links
    for link_html in html_soup.findAll('a', attrs={'href': re.compile(pattern)}):
        link = link_html.get('href')

        try:
            # download the zip file from the url
            zip_name, headers = urllib.urlretrieve(link)
            # unpack zip to designated directory and print status
            with zipfile.ZipFile(zip_name) as zip:
                zip.extractall(dest_dir)
                print "Successfully unpacked zip '{}' \n\t Link:{} \n\t Destination:{}.".format(zip_name, link,
                                                                                                dest_dir)
                for file in zip.filelist:
                    print "\t Files: \n\t\t {}".format(file.filename)
        except zipfile.BadZipfile as e:
            print "Error unpacking zip from link '{}': {}".format(link, str(e))
        except Exception as e:
            print "Error retrieving file from link '{}': {}".format(link, str(e))


def load_data(dir):
    """
    Load all Excel files in the designated directory (dir) into a dict mapped by filename.

    NOTE: currently only works with Excel files (.xlsx and .xls only).

    :param dir: Directory to load data files from.
    :return: Dict with filenames (sans extensions) as keys and pd.Dataframes of data as values.
    """
    data_dict = {}
    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)

        if os.path.isfile(filepath):
            # get name and file extension
            filename_parts = filename.split(".")
            if len(filename_parts) < 2:
                print "Error: filename {} does not have a proper file extension; skipping".format(filename)
                continue

            # check that we have proper file extension, then load workbook data
            if filename_parts[-1] in ['xlsx', 'xls']:
                data = pd.ExcelFile(filepath)
                print "Successfully loaded {}".format(filepath)
            else:
                print "Error: File format {} not currently supported, cannot load {}".format(filename_parts[-1], filepath)
                continue
            # map dataframe to filename (sans extension)
            data_dict[filename_parts[0]] = data

    return data_dict


def get_charge_sheet(wrkbk, sheet_index):
    """
    Return the designated workbook sheet from the workbook, dropping garbage rows from the Partners workbooks.

    NOTE: currently only works for the Partners workbooks
    :param wrkbk: The pd.Dataframe of the whole workbook
    :return: The properly formatted charge sheet (pd.Dataframe) of the workbook
    """
    # Note: pass None as sheet_names arg to get all sheets
    sheet = wrkbk.parse(sheet_index)

    # reorganize sheet to have proper column names and drop unnecessary rows
    sheet.columns = sheet.iloc[2]
    # these rows are just free text info describing the chargemaster; drop them and reset the index
    sheet = sheet.drop([0, 1, 2]).reset_index(drop=True)

    return sheet


def write_results(df, hospital_filename, filepath):
    """
    Write the dataframe to either stdout or filepath (if specified) in a nice human-readable format (without indicies,
    and with the original hospital filename as a title).

    NOTE: Does NOT overwrite file at filepath if designated; only appends results to the bottom of the file.

    :param df: The dataframe containing the Charge Code, Description, and Price of each billable item.
    :param hospital_filename: The filename of the chargemaster, containing the originating hospital's name.
    :param filepath: If designated, writes the results to the full filepath instead of stdout.
    :return: N/A
    """
    # write out the dataframe as a string
    hospital_header = "\n\n {} \n".format(hospital_filename)
    data_string = df.to_string(index=False)

    # if designated on commandline, write to file
    if filepath:
        print "Writing search results for {} to {}".format(hospital_filename, filepath)
        with open(filepath, "a") as out:
            out.write(hospital_header)
            out.write(data_string)
    # otherwise, write to stdout
    else:
        print hospital_header
        print data_string


def order_by(df, sort_type):
    """
    Order the Dataframe rows according to description or price (low to high or high to low), as designated by the user
    at the commandline.

    :param df: The Dataframe of Partners data to be sorted.
    :param sort_type: 'description' (alphanumeric); 'price' or 'price_l2h' (price low to high); 'price_h2l'
        (price high to low)
    :return: Sorted Dataframe.
    """
    sort_type = sort_type.lower()
    # alphanumeric
    if sort_type == "description":
        return df.sort_values("Description")
    elif "price" in sort_type:
        # high to low
        if sort_type == "price_h2l":
            return df.sort_values("Charge", ascending=True)
        # low to high
        else:
            return df.sort_values("Charge", ascending=False)
    else:
        raise Exception("Sorting type '{}' not recognized; please try again".format(sort_type))


def main():
    # get arguments from the commandline
    pattern, dest_dir, out_path, sort_type = read_arguments()

    page_url = "https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx"

    # get data files and store them in dest_dir
    fetch_zip_files(dest_dir, page_url, "Hospital-Charges")

    # create a dict of workbook Dataframes, with filenames as keys
    hospital_prices = load_data(dest_dir)

    # if user specifies a search pattern or keyword, then we should search for the relevant rows in all hospital data
    if pattern:
        for hospital_filename, data in hospital_prices.iteritems():
            # get first sheet (i.e. the only relevant one in Partners data)
            sheet = get_charge_sheet(data, 0)
            # find all of the rows that contain the search pattern (case insensitive), and then extract them
            matching_data = sheet[sheet['Description'].str.contains(pattern, case=False)]
            # write the valid results, sorted as necessary
            if not matching_data.empty:
                if sort_type:
                    matching_data = order_by(matching_data, sort_type)
                write_results(matching_data, hospital_filename, out_path)



if __name__ == "__main__":
    main()
