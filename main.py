import os
import urllib
import zipfile


page_url = "https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx"
resource_url = "https://www.partners.org/Assets/Documents/For-Patients/Financial-Assistance-Billing/Hospital-Charges/BWH-Standard-Charges.zip"

# download the zip file from the url
zip_path, headers = urllib.urlretrieve(resource_url)

# create destination directory if necessary
dest_dir = "./output"
try:
    os.makedir(dest_dir)
# makedir throws an exception if directory already exists; ignore it
except:
    pass

# unpack zip to designated directory
with zipfile.ZipFile(zip_path) as zip:
    zip.extractall(dest_dir)


