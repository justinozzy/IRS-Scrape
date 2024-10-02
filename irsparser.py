from urllib.request import urlopen
from bs4 import BeautifulSoup, ResultSet
from states import States

# Information gathered from https://www.irs.gov/e-file-providers/authorized-irs-e-file-providers-for-individuals
# Below is the general sorting of how a business is displayed on the website, including capitalizations
"""
Name of Business: Business Name
Address: 1234 EXAMPLE ST
City/State/ZIP: MY CITY, STATE *****
Point of Contact: FIRST LAST
Telephone: (***) ***-****
Type of Service: Type Of Service
"""

class IrsParser:
    provider_list = []

    def __init__(self) -> None:
        pass

    """
    Accesses the specified url using the zipcode and state for Authorized IRS e-file providers for individuals and businesses
    Return type: BeautifulSoup (html of page with extra methods)
    """
    def get_url(self, zipCode:str, state:int, page:int) -> BeautifulSoup:
        url = "https://www.irs.gov/efile-index-taxpayer-search?zip={0}&state={1}&page={2}".format(zipCode, state, page)
        page = urlopen(url)
        html = page.read().decode("utf-8")
        return BeautifulSoup(html, "html.parser")

    """
    Gets the list of all Authorized IRS e-file providers for individuals and businesses in a specified state and zipcode.
    Data is stored in a 2D array for easier access in the future since we can assign an index to a display field for the frontend.
    Return type: 2D List
    """
    def get_efile_providers(self, zipCode, state:States) -> list:
        # Reset list and set variables
        provider_list = []
        page = 0
        searching = True

        # We add a boolean variable since we are currently checking when to stop once the next button disappears on the webpage.
        # This can be improved by getting the number of matching items from the string at the top of the page which will give
        # an exact amount and allow for multithreading. (I consider this out of scope for now)
        while searching:
            soup = self.get_url(zipCode, state.value, page)
            # All relevant information about e-file providers lies in <td> tags with the class attributes below so gather that html.
            for result_html in soup.find_all(attrs={"class":"views-field views-field-nothing-1 views-align-left"}):
                temp_list = []
                # Only getting the first 7 result of the text split since the 8th is an empty string (equivalent of a for loop running 7 times)
                for result_text in result_html.text.split('\n')[:6]:
                    temp_list.append(result_text)
                self.provider_list.append(temp_list)

            # Here is the check to determine if we are on the last page of providers, see text above for more info.
            if (soup.find('li', {'class': 'next'}) is not None):
                page += 1
            else:
                searching = False

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