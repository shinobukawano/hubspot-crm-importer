# HubSpot CRM Importer

HubSpot offers the functionality of importing data from CSV file. You can import contact data, company data and deal data by using it. However, it has one limitation -- you can not associate objects with that. This is where this script shines. HubSpot CRM Importer script imports data from CSV to your HubSpot portal with beautiful relationship. :)

## Requirements

- Python 3+

## Getting Started

1.Clone the repository.

    $ git clone https://github.com/shinobukawano/hubspot_crm_importer

2.Install [Requests](http://docs.python-requests.org/en/master/) library.

    $ pip install requests

3.Add your HubSpot API Key in `main.py`, line 15.

    API_KEY = '246b....'

## Example

You can run this script with [sample import files from HubSpot Academy](https://knowledge.hubspot.com/articles/kcs_article/contacts/sample-import-files).

Open your terminal, and execute `python main.py` command. It loads those files from `csv` directory  and creates contacts, companies, and deals records into your HubSpot portal.

<img src="assets/3.gif" width="500"/>

## How does the script relate objects?

`company_id` and `contact_id` columns in csv files is the secret of it. The script associates objects based on values of them.

<img src="assets/1.png" width="700"/>

You can also set the owner of objects using `hubspot_owner_email` column. It finds HubSpot user by given email address and assign it to objects.

<img src="assets/2.png" width="300"/>

## License

This software is licensed under the MIT License.

