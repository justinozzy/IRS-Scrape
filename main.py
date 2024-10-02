from irsparser import IrsParser
from states import States
from flask import Flask, render_template, request

app = Flask(__name__)

providers = IrsParser()

"""
Index page for website, renders the basic elements when the page is first loaded.
Return type: String
"""
@app.route('/')
def index():
    return render_template('index.html', states=States, providers=providers.provider_list)

"""
Endpoint for getting E-file provider information based on selected state and zipcode.
Return type: String
"""
@app.route('/getproviders', methods=['GET'])
def get_providers():
    zipCode = request.args.get('zipCode')
    state = request.args.get('state')
    providers.get_efile_providers(zipCode, int(state))
    return render_template('index.html', states=States, providers=providers.provider_list)

"""
Endpoint for sorting E-file providers based on selected sorting option. Requires user to have already submitted
a request for a state and zip.
Return type: String
"""
@app.route('/sort', methods=['GET'])
def sort_providers():
    sort_by = request.args.get('sort_by')

    # Sorting logic - sorts based on whatever the value of x is from the provider list
    match sort_by:
        case 'bname':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[0])
        case 'zip':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[2].split(" ")[-1])
        case 'fname':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[3].split(" ")[0])
        case 'lname':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[3].split(" ")[1])
        case 'phone':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[4])
        case _:
            # Default return
            sorted_providers = providers.provider_list

    # Use the provider.html render template to re-create the rows once they are sorted
    return render_template('provider.html', states=States, providers=sorted_providers)

if __name__ == "__main__":
    app.run()