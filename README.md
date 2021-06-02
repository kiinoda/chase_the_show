# What's this?

This project uses Lambda and SES to retrieve the most recent episode of a show from a URL and send it via email. I created this so I would no longer need to chase the show on TV, this program sends me an email link to it on a daily basis.

## Credentials

AWS credentials are required. If you have a user set up, skip to next section. If you don't already have one, create an AWS IAM User with proper admin rights which will then take care of the necessary role and permissions for the Lambda when deploying.

```
mkdir ~/.aws
cat >> ~/.aws/config
[default]
aws_access_key_id=YOUR_ACCESS_KEY_HERE
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
region=eu-west-1
```

## Deployment

This project uses Chalice to handle deploying to AWS Lambda.

Once you clone the repo, run the following to create a deploy environment.

```
cd chase_the_show
python3 -m venv venv
. venv/bin/activate
python3 -m pip install -r requirements.txt
```

Copy `.chalice/config.json.sample` to `.chalice/config.json`, tailor to your specific environment and run the following to deploy.

```
chalice deploy
```

If you want to clean up, run the following.

```
chalice delete
```
