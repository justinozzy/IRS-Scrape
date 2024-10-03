# IRS-Scrape

Gathers information from [IRS E-File providers](https://www.irs.gov/e-file-providers/authorized-irs-e-file-providers-for-individuals) based on zip code and state then displays that information and allows for sorting on different parameters.

### Installation Pre-requisites

- [Python 3.12.7](https://www.python.org/downloads/release/python-3127/)
- [Pipenv](https://pypi.org/project/pipenv/)
> If you are installing on mac make sure to run the Install Certificates.command script in Python 3.12 folder

### Installation

1. Download the source code and place it in a folder of your choosing
2. Open a terminal inside the folder and run the following command: `pipenv sync`
3. Open up the pipenv shell: `pipenv shell`
4. Run the Flask application: `python3 main.py`
5. Type `exit` to leave the pipenv shell

> 📝 **Randomized Sleep Intervals:** While retrieving data the code will sleep anywhere from a one to three second interval, be patient and your result will (eventually) show up.

> :warning: **POTENTIAL LONG RUNTIMES:** Please test the zip code and state combination on the [website](https://www.irs.gov/e-file-providers/authorized-irs-e-file-providers-for-individuals) first. The following code runs through each page one by one and will take a very long time to run depending on result count.
