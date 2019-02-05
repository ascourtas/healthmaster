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
                                            help="The full filepath to a file to write the search results to.")

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

    return (args.pattern, dest_dir, args.out_path)


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
    Load all files in the designated directory (dir) into a dict mapped by filename.

    NOTE: currently only works with Excel files (.xlsx and .xls only).

    :param dir: Directory to load data files from.
    :return: Dict with filenames (sans extensions) as keys and pd.Dataframes of data as values.
    """
    data_dict = {}
    for filename in os.listdir(dir):
        # TODO: remove, just meant for debugging
        # if "MGH" not in filename : continue

        # get name and file extension
        filename_parts = filename.split(".")

        if filename_parts[1] in ['xlsx', 'xls']:
            filepath = os.path.join(dir, filename)
            data = pd.ExcelFile(filepath)
            print "Successfully loaded {}".format(filepath)
        else:
            print "Error: File format {} not currently supported, cannot load {}".format(filename_parts[1], filepath)
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


def main():
    # get arguments from the commandline
    pattern, dest_dir, out_path = read_arguments()

    page_url = "https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx"

    # get data files and store them in dest_dir
    fetch_zip_files(dest_dir, page_url, "Hospital-Charges")

    # create a dict of workbook Dataframes, with filenames as keys
    hospital_prices = load_data(dest_dir)

    # if user specifies a search pattern or keyword, then we should search for the relevant rows in all hospital data
    if pattern:
        for hospital_file, data in hospital_prices.iteritems():
            # get first sheet (i.e. the only relevant one in Partners data)
            sheet = get_charge_sheet(data, 0)
            # find all of the rows that contain the search pattern (case insensitive), and then extract them
            matching_data = sheet[sheet['Description'].str.contains(pattern, case=False)]
            if not matching_data.empty:
                print "\n\n {} \n".format(hospital_file)
                print matching_data


if __name__ == "__main__":
    main()







