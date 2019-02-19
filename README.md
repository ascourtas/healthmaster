# healthmaster
A tool to view how hospitals bill your healthcare to insurance companies.

This project is an attempt to demystify some aspects of hospital billing practices by making the [chargemasters](https://en.wikipedia.org/wiki/Chargemaster) (e.g. prices of billable items sent to insurance companies) for hospitals easily accessible and searchable. Hopefully, this may help those without insurance, or those with high deductibles, save themselves from some big surprise bills.

Thank you to [VOX's surprise billing reporting](https://www.vox.com/health-care/2018/12/18/18134825/emergency-room-bills-health-care-costs-america) for the inspiration for this project.

Data for this project is made possible by the The Affordable Care Act, which as of January 1st, 2019, [requires all hospitals](https://www.ajc.com/news/national/hospital-prices-are-about-public/2jXYHgoR5CObBj6fSJQQUO/) in the U.S. to make their chargemasters publicly available. 

---
# Usage
Clone the repo. From the root of the repo, run

 `python healthmaster.py`
 
 to fetch all standard hospital charges for the the hospitals in the Partners Healthcare Network in the Greater Boston Area (more hospitals coming soon).
 
 As of right now, methods are in place to scrape the necessary files from the Partners website, download and unpack the files, load them, and perform basic parsing.
 
 Currently, all hospital data will be written to `/output` in their native Excel workbook format.
 
 ## Current limitations
 * only tested on Linux environment, Python 2.7.12
 * only works for Partners Healthcare Network hospitals in the Boston area (see their data listing [here](https://www.partners.org/for-patients/Patient-Billing-Financial-Assistance/Hospital-Charge-Listing.aspx))
 * only works for Excel workbooks
 
## Prioritized TODOs
1. Set up accessible web app, hosting Partners data
2. Make data searchable
3. Make UI reactive, suitable for mobile
4. Pull in data from other hospitals in an area, given a zipcode and radius
5. Make a separate CLI tool


