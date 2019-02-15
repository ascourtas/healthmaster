from bs4 import BeautifulSoup
import os
import re
import urllib
import zipfile



def fetch_data_files(dest_dir, url, pattern):
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


def main():
    page_url = "https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx"

    # create destination directory if necessary
    # TODO: make this configurable from CLI
    dest_dir = "./output"
    try:
        os.makedir(dest_dir)
    # makedir throws an exception if directory already exists; ignore it
    except:
        pass

    fetch_data_files(dest_dir, page_url, "Hospital-Charges")




if __name__ == "__main__":
    main()







