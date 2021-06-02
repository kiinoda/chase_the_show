import boto3
import botocore.exceptions
import os
from string import Template
from requests_html import HTMLSession
from chalice import Chalice, Cron


app = Chalice(app_name="chase_the_show")


def get_show_info():
    try:
        session = HTMLSession()
        r = session.get(os.environ["SHOW_URL"])
        sel = os.environ["SHOW_SELECTOR"]
        show = r.html.find(sel, first=True)
        description = show.text.split(sep="\n")[0]
        link = show.links.pop()
        return description, link
    except Exception as e:
        print(e)


def parse_template(filename, description, link):
    with open(filename) as f:
        tpl = ''.join(f.readlines())
    template = Template(tpl)
    body = template.substitute(description=description, link=link)
    return body


def send_email(recipient):
    aws_region = os.environ["EMAIL_REGION"]
    charset = os.environ["EMAIL_ENCODING"]
    sender = os.environ["EMAIL_SENDER"]
    description, link = get_show_info()
    text_body = parse_template(os.environ["TEXT_TEMPLATE"], description, link)
    html_body = parse_template(os.environ["HTML_TEMPLATE"], description, link)
    subject = description
    client = boto3.client('ses', region_name=aws_region)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [ recipient ]
            },
            Message={
                'Body': {
                    'Html': { 'Charset': charset, 'Data': html_body},
                    'Text': { 'Charset': charset, 'Data': text_body}
                },
                'Subject': { 'Charset': charset, 'Data': subject }
            },
            Source=sender
        )
    except Exception as e:
        print(e)


@app.schedule(Cron(10, 6, '?', '*', 'TUE-SAT', '*'))
def deliver_it(event):
    send_email(os.environ["EMAIL_RECIPIENT"])
