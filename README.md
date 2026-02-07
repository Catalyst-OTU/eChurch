# PROJECT DESCRIPTION

## Ready to set up the project:
    git remote add origin https://github.com/Catalyst-OTU/eChurch.git




## NOTE
> The app will automatically create the database **e_church_db**


## Create Environment File
>  cp .env.example.env .env


## Installing Packages and STARTING APPLICATION ON Windows
- Run the following command in your terminal
    - cd app
    - python3 -m venv venv
    - ./venv/Script/activate
    - pip install -r requirements.txt
    - python main.py



## Create Environment File
>  cp .env.example.env .env


## Installing Packages and STARTING APPLICATION ON Linux, Ubuntu
- Run the following command in your terminal
    - cd app
    - python3 -m venv venv
    - source venv/bin/activate
    - pip install -r requirements.txt
    - python main.py




## RUNNING FASTAPI SERVICE ON DOCKER

## Create Environment File
>  cp .env.example.env .env


- Running FastAPI Service On Docker 
Run:
```
docker-compose --env-file ./.env up --build
```


Down containert with command:
```
docker-compose --env-file ./.env down
```


Setup environment variables; allowed environment variables `KEYWORDS`=`VALUES`:

| KEYWORDS | VALUES | DEFAULT VALUE | VALUE TYPE | 
| :------------ | :---------------------: | :------------------: | :------------------: |
| DB_TYPE | | postgresql | string 
| DB_NAME | | e_church_db | string 
| DB_SERVER | | localhost | string
| DB_USER | | postgres | string 
| DB_PASSWORD | | password | string 
| DB_PORT | | 5432 | integer 
| PGADMIN_DEFAULT_EMAIL | | admin@admin.com | string 
| PGADMIN_DEFAULT_PASSWORD | | openforme | string  
| BASE_URL | | http://localhost:8080/ | string  
| ADMIN_EMAIL | | superadmin@admin.com | string 
| ADMIN_PASSWORD | | openforme | string 
| EMAIL_CODE_DURATION_IN_MINUTES | | 15 | integer 
| ACCESS_TOKEN_DURATION_IN_MINUTES | | 60 | integer 
| REFRESH_TOKEN_DURATION_IN_MINUTES | | 600 | integer 
| PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES | | 15 | integer 
| ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES | | 15 | integer 
| MAIL_USERNAME | | | string 
| MAIL_PASSWORD | | | string 
| MAIL_FROM | | | string 
| MAIL_PORT | | | string 
| MAIL_SERVER | | | string 
| MAIL_FROM_NAME | | | string 
| MAIL_TLS |  boolean 
| MAIL_SSL | | false | boolean 
| USE_CREDENTIALS |  boolean 
| VALIDATE_CERTS |  boolean 
| DEFAULT_MAIL_SUBJECT | | | string 





For more info on Fastapi: [Click here](https://fastapi.tiangolo.com/)
