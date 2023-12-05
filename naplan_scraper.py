"""Main entry point for scraping NAPLAN Results."""

import argparse
import asyncio
import time

import pandas as pd
from playwright.async_api import async_playwright

from scraper.utils import (
    accept_tcs,
    extract_naplan_results,
    extract_raw_table_results_data,
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "SMLID",
    type=int,
    help="ACARA SML ID for the school of interest",
)
args = parser.parse_args()


# NAPLAN wasn't run in 2020 due to COVID
AVAILABLE_YEARS = ["2017", "2018", "2019", "2021", "2022"]
BASE_URL = "https://www.myschool.edu.au"
SCHOOL_ID = args.SMLID



async def main():
    """Main entrypoint to scraping results.
    """
    async with async_playwright() as p:
        print("Starting browser...")
        browser = await p.chromium.launch(headless=True)
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36";
        page = await browser.new_page(user_agent=user_agent, java_script_enabled=True)
        
        
        # Navigate to website & accept T&C's
        await page.goto(BASE_URL)
        print("Accepting T&C's...")
        await accept_tcs(page) 
        
        print("Scraping results...")
        results = []
        for year_of_interest in AVAILABLE_YEARS:
            print(f"Scraping results for {year_of_interest}...")
            time.sleep(1.5)

            # Navigate to school year
            school_url = f"{BASE_URL}/school/{SCHOOL_ID}/naplan/results"
            await page.goto(f"{school_url}/{year_of_interest}")

            # Extract results table HTML
            table_html = await extract_raw_table_results_data(page)

            # Results for year
            results.append(extract_naplan_results(table_html, year_of_interest)) 

        results_df = pd.concat(results)
        results_df.to_csv(f"{SCHOOL_ID}_results.csv")

        print(results_df)

        await browser.close()



if __name__ == "__main__":

    asyncio.run(main())    
