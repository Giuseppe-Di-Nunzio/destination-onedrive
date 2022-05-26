# Onedrive Destination

This is the repository of the Airbyte destination connector for OneDrive, written in Python. It enables you to copy data from any source to your OneDrive Business as csv files.
OneDrive connector makes easy to integrate enterprise data with Microsoft powerful tool like Power BI and more.

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.7.0`

#### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:
```
source .venv/bin/activate
pip install -r requirements.txt
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.
If this is mumbo jumbo to you, don't worry about it, just put your deps in `setup.py` but install using `pip install -r requirements.txt` and everything
should work as you expect.



### Locally running the connector docker image

#### Build
First, be sure to include the following in the Dockerfile in order to build an alpine docker image with criptografy libraries.

```
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base \
    && apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo
```
  

Second, make sure you build the latest Docker image:
```
docker build . -t airbyte/destination-onedrive:dev
```

#### Register your app in Azure Portal (https://portal.azure.com/)

    Sign in to the Azure portal.
    Select Azure Active Directory from the left nav.
    Select App registrations from the new nav blade.

Register the client app:

    In App registrations page, select New registration.

    When the Register an application page appears, enter your application's registration information:
        In the Name section, enter a meaningful application name that will be displayed to users of the app, for example desktop-sample.
        In the Supported account types section, select any option.


    Select Register to create the application.

    On the app Overview page, find the Application (client) ID value and use it later  in your connection setup as  client_id entry.

    In *Authentication select the recommended Redirect URIs for public clients.

    Then set the "Default Client Type: Treat application as a public client" to Yes and Save.

    In the list of pages for the app, select API permissions
        Click the Add a permission button and then,
        Ensure that the Microsoft APIs tab is selected
        In the Commonly used Microsoft APIs section, click on Microsoft Graph
        In the Delegated permissions section, ensure that the right permissions are checked: Files.ReadWrite. Use the search box if necessary.
        Select the Add permissions button

    Permissions are now assigned correctly, but the very first time you run the connector, you'll get an error with an URL to click for getting signed-in user consent. Click on it to let the process flow.  
     

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-onedrive:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-onedrive:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-onedrive:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```
