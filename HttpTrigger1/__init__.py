import logging
from typing import final
import azure.functions as func
import requests
import json
import csv


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request...')

    r = requests.get('https://www.gov.uk/bank-holidays.json').json()

    date = req.params.get('date')
    if not date:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            date = req_body.get('date')
    final_data = []
    if date:
        for (k, i) in r.items():
            if k == "england-and-wales":
                for d in i['events']:
                    if date in d['date']:
                        final_data.append(d)
    else:
        return func.HttpResponse(
            "Please pass a date on the query string or in the request body",
            status_code=400)

    desc_resp = {
        'events': sorted(final_data, key=lambda o: o['date'], reverse=True)
    }

    header = []
    csv_data = []

    with open('england-and-wales_bank_holidays.csv', 'w',
              encoding='UTF-8') as file:
        writer = csv.writer(file)

        writer.writerow(header)
        writer.writerow(csv_data)

    print(desc_resp)

    return func.HttpResponse(json.dumps(desc_resp))
