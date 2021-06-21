import boto3
import botocore.exceptions
import os
from logging import INFO
from string import Template
from requests_html import HTMLSession
from chalice import Chalice, Cron


app = Chalice(app_name="chase_the_show")
app.log.setLevel(INFO)


def get_show_info():
    # returns err, description, link
    try:
        err = 0
        session = HTMLSession()
        r = session.get(os.environ["SHOW_URL"])
        sel = os.environ["SHOW_SELECTOR"]
        show = r.html.find(sel, first=True)
        description = show.text.split(sep="\n")[0]
        link = show.links.pop()
        return err, description, link
    except Exception as e:
        err = 1
        print(e)
        return err, "Parsing failed", e


def parse_template(filename, description, snippet):
    with open(filename) as f:
        tpl = ''.join(f.readlines())
    template = Template(tpl)
    body = template.substitute(description=description, snippet=snippet)
    return body


def send_email(recipient, text_body, html_body):
    aws_region = os.environ["EMAIL_REGION"]
    charset = os.environ["EMAIL_ENCODING"]
    sender = os.environ["EMAIL_SENDER"]
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
        app.log.info(f"email sent to {recipient}")
    except Exception as e:
        print(e)


@app.schedule(Cron(10, 6, '?', '*', 'TUE-SAT', '*'))
def deliver_it(event):
    err, description, snippet = get_show_info()
    if err == 0:
        text_body = parse_template(os.environ["TEXT_TEMPLATE"], description, snippet)
        html_body = parse_template(os.environ["HTML_TEMPLATE"], description, snippet)
    else:
        text_body = parse_template(os.environ["ERR_TEXT_TEMPLATE"], description, snippet)
        html_body = parse_template(os.environ["ERR_HTML_TEMPLATE"], description, snippet)
    send_email(os.environ["EMAIL_RECIPIENT"], text_body, html_body)
