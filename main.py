from irsparser import IrsParser
from states import States
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    providers = IrsParser()
    providers.get_efile_providers('93030', States.CALIFORNIA)
    return render_template('index.html', providers=providers.provider_list)

if __name__ == "__main__":
    app.run()