# healthmaster
A tool to view how hospitals bill your healthcare to insurance companies.

This project is an attempt to demystify some aspects of hospital billing practices by making the [chargemasters](https://en.wikipedia.org/wiki/Chargemaster) (e.g. prices of billable items sent to insurance companies) for hospitals easily accessible and searchable. Hopefully, this may help those without insurance, or those with high deductibles, save themselves from some big surprise bills.

Thank you to [VOX's surprise billing reporting](https://www.vox.com/health-care/2018/12/18/18134825/emergency-room-bills-health-care-costs-america) for the inspiration for this project.

Data for this project is made possible by the The Affordable Care Act, which as of January 1st, 2019, [requires all hospitals](https://www.ajc.com/news/national/hospital-prices-are-about-public/2jXYHgoR5CObBj6fSJQQUO/) in the U.S. to make their chargemasters publicly available. 

---
# Dependencies
`pip install` the following packages if you don't have them already:
- argparse
- bs4
- numpy
- pandas=0.24.1
- xlrd
---
# Usage
Healthmaster can be used to download and unzip chargemasters, search them for keywords, and order the results.

Clone the repo. From the root of the repo, run

 `python healthmaster.py`
 
 to fetch all standard hospital charges for the the hospitals in the Partners Healthcare Network in the Greater Boston Area (more hospitals coming soon).
 
 ### Options
 `-s, --search` Search the fetched data for a keyword or regex pattern; results will be written to stdout unless specified by the -w option
 
 `-d, --dest_dir` Write the scraped chargemaster files to the designated directory (full directory path). Default is './output'
 
 `-w, --write_to_file` Write the results from -s to the designated file (full file path)
 
 `-o, --order_by` Order the search results by the designated sorting type. Types are:
 
     - description -- orders billing item descriptions alphanumerically
     
     - price -- orders by price, low to high
     
     - price_l2h -- same as above
     
     - price_h2l -- orders by price, high to low
 
 As of right now, methods are in place to scrape the necessary files from the Partners website, download and unpack the files, load them, perform basic parsing and searching, and write the results to stdout or a file.
 
 Currently, all hospital data will be written to in their native Excel workbook format.
 
 ## Current limitations
 * only tested on Linux environment, Python 2.7.12, Pandas 0.24.1
 * only works for Partners Healthcare Network hospitals in the Boston area (see their data listing [here](https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx))
 * only works for Excel workbooks
 
## High-level, prioritized TODOs
1. Improve search capabilities to be more flexible (CLI/web)
2. Allow user to search hospitals by distance from their zipcode (CLI/web)
3. Implement Knapsack or Simplex algorithm for optimizing price of service and distance to hospital (CLI/web)
4. Set up accessible web app, hosting Partners data
5. Make UI reactive, suitable for mobile
6. Set up proper database
7. Pull in data from other hospitals in an area, given a zipcode and radius

### Smaller scale TODOs
- add option to overwrite output file instead of continually adding to it
- add option to sort by multiple params
- add option to sort by chargecode
- add option to write results to .csv instead of .txt
- break out script into just a main.py script and then a healthmaster.py core module and associated helper modules
- create a reference.py module for mapping abbreviated hospital names (e.g. MGH) to full names (e.g. Massachusetts General Hospital), and then write the full names to the results file instead of the filenames, for clarity
- make it the default to not pull down the zip'd files if they already exist in dest_dir
- add option to overwrite the chargemaster files if desired


