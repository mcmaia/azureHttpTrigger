import logging
from typing import final
import azure.functions as func
import requests
import json
import csv
from io import StringIO


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

    desc_resp = sorted(final_data, key=lambda o: o['date'], reverse=True)

    header = []
    csv_data = []

    for k in desc_resp:
        for h in k:
            if h not in header:
                header.append(h)

    for i in desc_resp:
        for b in i.values():
            csv_data.append(b)

    n = len(header)
    content = [csv_data[i:i + n] for i in range(0, len(csv_data), n)]
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for row in content:
        writer.writerow(row)

    csv_output = output.getvalue().strip("\r\n")

    headers = {}
    headers['content-type'] = 'text/csv'
    headers[
        'Content-Disposition'] = 'attachment;filename="england-and-wales_bank_holidays.csv"'

    return func.HttpResponse(body=csv_output, status_code=200, headers=headers)