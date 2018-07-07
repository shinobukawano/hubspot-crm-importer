# -*- coding: utf-8 -*-
"""
HubSpot CRM Importer
~~~~~~~~~~~~
:copyright: (c) 2018 by Shinobu Kawano.
"""
import csv
import requests
import logging

from datetime import datetime

""" Global Variables
"""
API_KEY = ''

owners = []
companies = []
contacts = []
deals = []
pipelines = []

""" Logging
"""
logger = logging.getLogger('CRM Importer')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('import.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def hs_timestamp(date):
    """ date value should be Y/m/d format.
    """
    if date is '':
        return None

    try:
        d = datetime.strptime(date, '%Y/%m/%d').strftime('%s')
        return int(d) * 1000

    except Exception as e:
        logger.info(e.args)
        return None


def load_owners_from_hs():
    global owners
    logger.info('Load HubSpot Owners from HubSpot.')

    url = 'http://api.hubapi.com/owners/v2/owners?hapikey=' + API_KEY
    r = requests.get(url)

    owners = r.json()


def get_owner(email):
    global owners

    result = [ r for r in owners if r.get('email') == email ]

    if len(result) != 0:
        return result[0]
    else:
        return {}


def load_companies_from_csv():
    global owners
    global companies
    logger.info('Load Companies from CSV file.')

    with open('csv/companies.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            owner_email = row.get('hubspot_owner_email','')
            owner = get_owner(owner_email)

            companies.append({
                "company_id": row.get('company_id',''),
                "name": row.get('Name',''),
                "properties": [
                    {
                      "name": "name",
                      "value": row.get('Name','')
                    },
                    {
                      "name": "hubspot_owner_id",
                      "value": owner.get('ownerId')
                    }
                ]
            })


def create_companies_to_hs():
    global companies
    logger.info('Create Companies to HubSpot.')

    url = 'https://api.hubapi.com/companies/v2/companies?hapikey=' + API_KEY

    for company in companies:
        try:
            r = requests.post(url, json=company)

            name = company.get('name')
            status_code = r.status_code
            logger.info(str(status_code) + ' - Company: '+ name)

            if status_code != 200:
                logger.info(r.json())

            company['id'] = r.json().get('companyId')

        except Exception as e:
            logger.info(e.args)
            pass


def get_company(id):
    global companies

    result = [ r for r in companies if r.get('company_id') == id ]

    if len(result) != 0:
        return result[0]
    else:
        return {}


def load_contacts_from_csv():
    global owners
    global contacts
    logger.info('Load Contacts from CSV file.')

    with open('csv/contacts_sample_import-1.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            owner_email = row.get('hubspot_owner_email','')
            owner = get_owner(owner_email)

            company_id = row.get('company_id','')
            company = get_company(company_id)

            contacts.append({
                "contact_id": row.get('contact_id',''),
                "email" : row.get('Email',''),
                "name": row.get('First Name','') + ' ' + row.get('Last Name',''),
                "properties": [
                    {
                        "property": "firstname",
                        "value": row.get('First Name','')
                    },
                    {
                        "property": "lastname",
                        "value": row.get('Last Name','')
                    },
                    {
                        "property": "company",
                        "value": company.get('company_name','')
                    },
                    {
                        "property": "associatedcompanyid",
                        "value": company.get('id','')
                    },
                    {
                      "property": "hubspot_owner_id",
                      "value": owner.get('ownerId')
                    }
                ]
            })


def create_contacts_to_hs():
    global contacts
    logger.info('Create Contacts to HubSpot.')

    for contact in contacts:
        try:
            email = contact.get('email')
            url = f"https://api.hubapi.com/contacts/v1/contact/createOrUpdate/email/{email}/?hapikey=" + API_KEY

            r = requests.post(url, json=contact)

            name = contact.get('name')
            status_code = r.status_code
            logger.info(str(status_code) + ' - Contact: '+ name)

            if status_code != 200:
                logger.info(r.json())

            contact['vid'] = r.json().get('vid')

        except Exception as e:
            logger.info(e.args)
            pass


def get_contact(id):
    global contacts

    result = [ r for r in contacts if r.get('contact_id') == id ]

    if len(result) != 0:
        return result[0]
    else:
        return None


def load_deal_pipelines_from_hs():
    global pipelines
    logger.info('Load Deal Pipelines from HubSpot.')

    url = 'https://api.hubapi.com/deals/v1/pipelines?hapikey=' + API_KEY

    r = requests.get(url)
    pipelines = r.json()


def get_pipeline(pipeline):
    global pipelines

    result = [ r for r in pipelines if r.get('pipelineId') == pipeline ]

    if len(result) != 0:
        return result[0]
    else:
        return None


def load_deals_from_csv():
    global owners
    global deals
    global pipelines
    logger.info('Load Deals from CSV file.')

    with open('csv/Sample_Deal_Import-1.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Owner
            owner_email = row.get('hubspot_owner_email','')
            owner = get_owner(owner_email)

            # Companies
            company_id = row.get('company_id','')
            company = get_company(company_id)

            associatedCompanyIds = []
            if company is not None:
                associatedCompanyIds.append(company.get('id'))

            # Contacts
            contact_id = row['contact_id']
            contact = get_contact(contact_id)

            associatedVids = []
            associatedVids.append(contact.get('vid'))

            # Pipelines
            pipeline = row.get('Pipeline', 'default')
            dealstage = row.get('Deal Stage', '')

            p = get_pipeline(pipeline)

            if p is None:
                # Use default pipeline
                pipeline = 'default'
                p = pipelines[0]

            stages = [ r for r in p.get('stages', '') if r['label'] == dealstage ]
            if len(stages) > 0:
                dealstage = stages[0].get('stageId')

            # Close Date
            closedate = hs_timestamp(row.get('Close Date','1/1/1970'))

            deals.append({
                "name": row.get('Deal Name',''),
                "associations": {
                    "associatedCompanyIds": associatedCompanyIds,
                    "associatedVids": associatedVids
                },
                "dealname" : row.get('Deal Name',''),
                "properties": [
                    {
                      "name": "dealname",
                      "value": row.get('Deal Name','')
                    },
                    {
                      "name": "amount",
                      "value": row.get('Amount','')
                    },
                    {
                        "name": "pipeline",
                        "value": pipeline
                    },
                    {
                        "name": "dealstage",
                        "value": dealstage
                    },
                    {
                        "name": "closedate",
                        "value": closedate
                    },
                    {
                      "name": "hubspot_owner_id",
                      "value": owner.get('ownerId')
                    }
                ]
            })


def create_deals_to_hs():
    global deals
    logger.info('Create Deals to HubSpot.')

    url = 'https://api.hubapi.com/deals/v1/deal?hapikey=' + API_KEY

    for deal in deals:
        try:
            r = requests.post(url, json=deal)

            name = deal.get('name')
            status_code = r.status_code
            logger.info(str(status_code) + ' - Deal: '+ name)

            if status_code != 200:
                logger.info(r.json())

        except Exception as e:
            logger.info(e.args)
            pass


if __name__ == "__main__":
    # Users
    load_owners_from_hs()

    # Companies
    load_companies_from_csv()
    create_companies_to_hs()

    # Contacts
    load_contacts_from_csv()
    create_contacts_to_hs()

    # Deals
    load_deal_pipelines_from_hs()
    load_deals_from_csv()
    create_deals_to_hs()

    logger.info("Congratulations! Your data migration is completed. :)")

