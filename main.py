from irsparser import IrsParser
from states import States
from flask import Flask, render_template, request

app = Flask(__name__)

providers = IrsParser()

@app.route('/')
def index():
    return render_template('index.html', states=States, providers=providers.provider_list)

@app.route('/getproviders', methods=['GET'])
def get_providers():
    zipCode = request.args.get('zipCode')
    state = request.args.get('state')
    providers.get_efile_providers(zipCode, int(state))
    print(providers.provider_list)
    return render_template('index.html', states=States, providers=providers.provider_list)

@app.route('/sort', methods=['GET'])
def sort_providers():
    sort_by = request.args.get('sort_by')

    # Sorting logic - sorts based on whatever the value of x is from the provider list
    match sort_by:
        case 'zip':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[2].split(" ")[-1])
        case 'name':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[0])
        case 'contact':
            sorted_providers = sorted(providers.provider_list, key=lambda x: x[3])
        case _:
            # Default return
            sorted_providers = providers.provider_list

    # Use the provider.html render template to re-create the rows once they are sorted
    return render_template('provider.html', states=States, providers=sorted_providers)

if __name__ == "__main__":
    app.run()