from bs4 import BeautifulSoup
import os
import re
import urllib
import zipfile


page_url = "https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx"

# create destination directory if necessary
# TODO: make this configurable from CLI
dest_dir = "./output"
try:
    os.makedir(dest_dir)
# makedir throws an exception if directory already exists; ignore it
except:
    pass

# open whole Partners page
html_page = urllib.urlopen(page_url)
html_soup = BeautifulSoup(html_page, "html.parser")

# match all links in the HTML dump that contain the text "Hospital-Charges"; these should be the zip links
for link_html in html_soup.findAll('a', attrs={'href': re.compile("Hospital-Charges")}):
    link = link_html.get('href')

    try:
        # download the zip file from the url
        zip_name, headers = urllib.urlretrieve(link)
        # unpack zip to designated directory
        with zipfile.ZipFile(zip_name) as zip:
            zip.extractall(dest_dir)
            print "Successfully unpacked zip '{}' \n\t Link:{} \n\t Destination:{}.".format(zip_name, link, dest_dir)
            for file in zip.filelist:
                print "\t Files: \n\t\t {}".format(file.filename)
    except Exception as e:
        print "Error with zip '{}' from link {}".format(zip_name, link)







