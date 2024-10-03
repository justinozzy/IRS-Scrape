from db import Database
from random import randint
from time import sleep
from urllib.request import urlopen
from bs4 import BeautifulSoup, ResultSet
from states import States

# Information gathered from https://www.irs.gov/e-file-providers/authorized-irs-e-file-providers-for-individuals
# Below is the general sorting of how a business is displayed on the website, including capitalizations
"""
[0] Name of Business: Business Name
[1] Address: 1234 EXAMPLE ST
[2] City/State/ZIP: MY CITY, STATE *****
[3] Point of Contact: FIRST LAST
[4] Telephone: (***) ***-****
[5] Type of Service: Type Of Service
"""

class IrsParser:
    provider_list = []

    def __init__(self, database: Database) -> None:
        self.database = database

    """
    Accesses the specified url using the zipcode and state for Authorized IRS e-file providers for individuals and businesses
    Return type: BeautifulSoup (html of page with extra methods)
    """
    def get_url(self, zipCode:str, state:int, page:int) -> BeautifulSoup:
        # IRS website uses numbering system (1 - 56) for states so have to use this hack for any state.
        if (state == 0):
            state = "All"
        url = "https://www.irs.gov/efile-index-taxpayer-search?zip={0}&state={1}&page={2}".format(zipCode, state, page)
        page = urlopen(url)
        html = page.read().decode("utf-8")
        return BeautifulSoup(html, "html.parser")

    """
    Gets the list of all Authorized IRS e-file providers for individuals and businesses in a specified state and zipcode.
    Data is stored in a 2D array for easier access in the future since we can assign an index to a display field for the frontend.
    Return type: 2D List
    """
    def get_efile_providers(self, zipCode, state) -> list:
        # Reset list and set variables
        conn = self.database.get_db()
        self.provider_list = []
        page = 0
        searching = True
        
        # Run the database check to determine if we have already gathered data from this zipcode
        # This step gets skipped if we already have the data for this zip in the database.
        db_check = self.database.check_and_update_accessed(zipCode, state)
        if db_check:
            # We add a boolean variable since we are currently checking when to stop once the next button disappears on the webpage.
            # This can be improved by getting the number of matching items from the string at the top of the page which will give
            # an exact amount and allow for multithreading. (I consider this out of scope for now)
            while searching:
                soup = self.get_url(zipCode, state, page)
                # All relevant information about e-file providers lies in <td> tags with the class attributes below so gather that html.
                for result_html in soup.find_all(attrs={"class":"views-field views-field-nothing-1 views-align-left"}):
                    # Only getting the first 7 result of the text split since the 8th is an empty string (equivalent of a for loop running 7 times)
                    temp_list = [result_text for result_text in result_html.text.split('\n')[:6]]
                    # Hacky solution: since urls are accessed by zip code and state we need to add these at the end of our data
                    # for each result. After this we send all of that data (gets unraveled by *) to the update provider data method.
                    temp_list.append(zipCode)
                    temp_list.append(state)
                    self.database.update_provider_data(*temp_list)

                # Here is the check to determine if we are on the last page of providers, see text above for more info.
                if (soup.find('li', {'class': 'next'}) is not None):
                    page += 1
                else:
                    searching = False

                # Force a sleep of one to three seconds to avoid abusing server hardware (disable if your result count is low)
                sleep(randint(1, 3))

        # Load data into an array from the database and close databae connection
        self.provider_list = self.database.get_providers(zipCode, state)
        self.database.close_db(conn)
        return self.provider_list

    """
    Prints all of the providers currently stored.
    Return type: None
    """
    def print_providers(self) -> None:
        for provider in self.provider_list:
            for field in provider:
                print(field)
            print('\n\n')
