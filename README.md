# Azure HTTP Function - from locally test to deploy

This project will show you how to test and deploy your first Azure HTTP Function using Python. Awesome right?
If you want to see the result, jump to the end of the document. There I explain how to see our output.

For this project, we just need to get the UK's list of bank holidays and export the response as a CSV file.

**Bank Holidays:** https://www.api.gov.uk/gds/bank-holidays/#bank-holidays
**Expected technology:** Azure Function with HTTP trigger
**Input:** year
**Output:** CSV file


### Rules

1. The csv file must export only bank holidays of the year set as parameter when calling the Azure Function
2. Bank Holidays should be exported in desc order
3. Only Bank Holidays of “england-and-wales” should be present on the CSV file

Let's get going. 

## Set up

1. First things first: Sing up to an Azure account. Done? Cool.

2. Download the VScode. <https://code.visualstudio.com/>

3. In your VScode, follow the steps in the link <https://docs.microsoft.com/pt-br/azure/azure-functions/create-first-function-vs-code-python>. 
**3a**.This link will show how to set up your environment. It is pretty easy. Follow the instructions and go to the next step. <br>
**3b**. Note: Notice that this environment will give you this code:
```Python
import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400
        )
```

Cool. Now, **let's code**.

## Coding

Here, I will explain the code blocks and what each one of them do.

### Imports

The following list of imports is what is necessary to work on our code.
It is important to highlight 2 of those imports. **requests** and **from io import StringIO**. The first will allow you to consume an API. The second is an in-memory file-like object, which means, in our case, that this object will write our csv before downloading.

Note: `request` must be installed. `pip install requests` - after this, don't forget to insert `request` in your requeirements.txt.
Otherwise, when you deploy your project, it won't work. That's because you have to "advise" Azure that it needs to include something you have installed locally.

```Python

import logging
import azure.functions as func
import requests
import json
import csv
from io import StringIO

```

### creating function and calling the API

```Python

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request...')

    r = requests.get('https://www.gov.uk/bank-holidays.json').json()

```

### Defining date as parameter

```Python

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

```
### Organizing the data in a desc order

```python

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

```

### writing and downloading the CSV

```python 

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
```

## Cream on top (deploying, testing, and generating link)

Now, deploy your function to Azure. 
There you should access the function.
Go to *Code + test* -> *test/run*

In HTTP method, chose GET
Key, leave as master (host key)

in body, you should write:
{
  "date": "<*an year you'd like to check - i.e.:2020*>"
}

After testing and running successfully, click ***Get function URL***

# Output

This link should look like this: https://httpfunction-challenge.azurewebsites.net/api/HttpTrigger1
https://(project_name).azurewebsites.net/api/(function_name)

To make it work, you must parse the parameters: **?date=year**

and DONE!

I hope you enjoyed your time!

## Note

The way it was presented here, the code is one block in a function. It would be nice to modulate it or to create the functions for every task separately.


