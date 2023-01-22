# Asynchronous uploading task with Django and Celery in Docker based

# Asynchronous uploading task
***
1. [General Info](#general-info)
2. [Database Architecture](#database-architecture)
3. [Execution Description](#execution-description)
4. [Launch Instructions](#launch-instructions)
5. [Uploading Task Guide](#uploading_task_guide)

## General Info
***
Upload an excel file with a list of contacts.
When processing the list of contacts, the same email address or phone number cannot
uploaded in a time window of 3 minutes. After 3 minutes have passed, contact with
that email or phone number uploaded.
The original excel file stored in S3.

## Database Architecture
***
Excel file upload app database architecture shown below:

Created 4 tables `Users`, `FileMetadata`, `Contacts` and `UnprocessedContacts`.

## Execution Description
***
The file is stored only in the S3 bucket, storing that file also in the local db is not a good approach I guess.
I have created a `FileMetadata` table where I have stored all information about the specific user upload.
User contacts `Name, Phone Number, Email Address` stored in database (`Contacts` table).
For good approach I deside to create one more table (`UnprocessedContacts`) for caching the contacts, 
when contacts have the same `Phone Number` or `Email Address`.

When a user uploads the excel file for example with 1000 records/contacts, but from there we have only 10 
records/contacts with the same `Phone Number` or `Email Address` that contacts stored in `UnprocessedContacts` table.
After storing 990 contacts to `Contacts` table, the application starts the Celery async tasks 
(time duration up to 3 minutes) for 10 contacts that were stored in `UnprocessedContacts` and delete it after completion.

## Launch Instructions
***

**Please install [git](https://github.com/git-guides/install-git) , [docker](https://docs.docker.com/engine/install/ubuntu/) and [postman](https://www.postman.com/downloads/) at your machine before lunch the application.**

1. [Git](#git)
2. [Docker](#docker)
3. [Postman](#postman)
4. [AWS](#aws)

### Git

Clone the git repository with below command:
git clone https://github.com/karbag89/django_celery_project

### Docker

**Run the below docker command:**

```
(app) $ docker-compose up -d --build
```

**The result of docker-compose up -d --build shown below:**

```
Creating django_celery_project_redis_1 ... done
Creating django_celery_project_app_1 ... done
Creating django_celery_project_celery_1 ... done
```
To confirm that everything is up and running one can check using standard
Docker commands.

**To see running containers:**

```
$ docker ps
CONTAINER ID        IMAGE                          COMMAND                  CREATED              STATUS              PORTS                    NAMES
9d08fcdb3a78        django_celery_project_celery   "/usr/src/app/entryp…"   About a minute ago   Up About a minute                            django_celery_project_celery_1
27b36a17dfec        django_celery_project_app      "/usr/src/app/entryp…"   About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp   django_celery_project_app_1
15b991d0fd70        redis:7-alpine                 "docker-entrypoint.s…"   About an hour ago    Up About a minute   6379/tcp                 django_celery_project_redis_1

```

**To stop the running services:**

```
$ docker-compose stop
Stopping django_celery_project_celery_1 ... done
Stopping django_celery_project_app_1    ... done
Stopping django_celery_project_redis_1  ... done
```

**To destroy all the infrastructure that Docker brought up:**

```
$ docker-compose down
Stopping django_celery_project_celery_1 ... done
Stopping django_celery_project_app_1    ... done
Stopping django_celery_project_redis_1  ... done
Removing django_celery_project_celery_1 ... done
Removing django_celery_project_app_1    ... done
Removing django_celery_project_redis_1  ... done
Removing network django_celery_project_default
```

### Postman

Please import **`Upload_API.postman_collection.json`** in your postman collections.

**Note: After uploading you can fined examples for API endpoints call.**

### AWS

AWS S3 bucket configuration.
Please create your AWS S3 bucket and inside the policy set below json information with your user credentials data.
```
{
    "Version": "2012-10-17",
    "Id": "Your_Policy_ID",
    "Statement": [
        {
            "Sid": "Stmt1674076233251",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::bucket_name/*"
        }
    ]
}
```

After creation of AWS S3 bucket, copy your AWS credentials to project/celery_project/setting.py

**NOTE: YOU MUST WRITE YOUR AWS CREDENTIALS ON SETTING.PY FILE.**

```
**AWS_ACCESS_KEY_ID = "<YOUR_AWS_ACCESS_KEY_ID>"**
**AWS_SECRET_ACCESS_KEY = "<YOUR_AWS_SECRET_ACCESS_KEY>"**
**AWS_STORAGE_BUCKET_NAME = "<YOUR_AWS_STORAGE_BUCKET_NAME>"**
```

## Uploading Task Guide
***
* After Docker command `docker-compose up -d --build` successful run 
go to _(http://localhost:8000/admin)_ panel and login with **`username=admin`** and **`password=admin`**.
You can see database tables available there.

* Then open your **Postman** program and from imported collections open/click **`Register`** `POST` command/endpoint.
Type new username and password (on POST command JSON body) to register new user by clicking `send` button_(see example)_. 

* After that, open/click **`Login`** `POST` command/endpoint to login the newly created user
(type new user credentials on POST command JSON body) by clicking the `send` button _(see example)_.

**Note: I guess the JWT tokens must be saved in the front end side, not in backend side.**

* Then open/click **`Upload`** `POST` command/endpoint to upload the Excel file _(see example)_.
**Excel file must have only 3 columns Name, Phone Number, Email Address**
After uploading a completed open ADMIN panel and in the database you can see uploaded file 
contacts info in the `Contacs` table.

* To see the original excel file on S3 bucket, please open/click **`User Uploaded Files`** `GET` command/endpoint 
and put the username in the path variable _(see example)_ then click the `send` button on Postman.
In response you can see the original excel file location path on your S3 bucket.
By clicking on that url you can find your original file on S3 bucket.

* For logout the user from application open/click **`Logout`** command/endpoint by clicking the 
`send` button _(see example)_.

Enjoy asynchronous uploading task with Django and Celery in Docker based application.