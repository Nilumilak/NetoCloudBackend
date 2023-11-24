![CI](https://github.com/Nilumilak/NetoCloudBackend/actions/workflows/cicd.yml/badge.svg)

![Alt text](assets/NetoCloudLogo.png)
# NetoCloud
## Description
Cloud storage where you can store your files, download and use their links to put in other 
services.

Backend - https://github.com/Nilumilak/NetoCloudBackend<br />
Frontend - https://github.com/Nilumilak/NetoCloudFrontend

- File managing:
  - Save files in current location or into a folder.
  - Add notes.
  - Change file name, notes.
  - Download file.
  - Copy permalink.
- User profile:
  - Create new profile.
  - Delete profile.
  - Change Username, Full Name, Email, Password.
  - Track files count and total space.
- Storage max size is 2Gb for each user.
- Admin profile:
  - List of all active users (without current user).
  - Manage other users:
    - Change other user admin status.
    - Delete other user account.
  - Manage other users storage:
    - List of all user files.
    - Delete file.
    - Change file name, notes.
    - Download file.

## Toolset
- Django
- Django Rest Framework
- Simple JWT
- Postgresql
- Pytest
- GitHub Actions

## API
User:
- GET "api/v1/users/" --> list of users
  - admin token required
- POST "api/v1/users/" --> create new user
  - required fields: username, full_name, email, password, repeat_password
- GET "api/v1/users/\<pk>/" --> get user
  - token required
- PUT, PATCH "api/v1/users/update/\<pk>/" --> update user
  - token required
  - fields: username, full_name, email
  - password change required fields: current_password, password, repeat_password
- DELETE "api/v1/users/delete/\<pk>/" --> delete user
  - token required
  - fields: username, full_name, email
  - password change required fields: current_password, password, repeat_password

Token:
- POST "api/v1/token/" --> get new access and refresh token
  - required fields: username, password
- POST "api/v1/token/refresh/" --> get new access token
  - required fields: refresh
- POST "api/v1/token/verify/" --> verify access token
  - required fields: token

Storage:
- GET "api/v1/storages/" --> list of storages
  - admin token required
- GET "api/v1/storages/\<pk>/" --> get storage
  - token required

File:
- POST "api/v1/files/" --> create new file
  - token required
  - required fields: file_data, name
  - optional fields: path, note
- PUT, PATCH "api/v1/files/update/\<pk>/" --> update file
  - token required
  - fields: name, note
- DELETE "api/v1/files/delete/\<pk>/" --> delete file
  - token required

## Deployment
- Get a domain
- Connect to the server through ssh
- Create new user:
  - adduser \<username>
  - usermod \<username> -aG sudo
  - su \<username>
- Install programs:
  - sudo apt update
  - sudo apt install python3-pip python3-venv postgresql expect -y
- Postgres settings
  - sudo su postgres
  - psql
  - CREATE USER \<username> WITH SUPERUSER;
  - ALTER USER \<username> WITH PASSWORD '\<password>';
  - CREATE DATABASE \<username>;
  - exit
  - su \<username>
  - psql
  - CREATE DATABASE \<db_name>;
  - exit
- Clone the project:
  - cd /home/\<username>
  - git clone https://github.com/Nilumilak/NetoCloudBackend.git
- Configure .env file
  - cd NetoCloudBackend
  - create .env file
  - Configure variables:
    - SECRET_KEY=
    - DEBUG=0
    - ALLOWED_HOSTS=\<server ip address>
    - ALLOWED_CORS_ORIGINS=http://\<server ip address>,https://\<server ip address>
    - DB_ENGINE=django.db.backends.postgresql
    - DB_NAME=\<db_name>
    - DB_HOST=localhost
    - DB_PORT=5432
    - DB_USER=\<username>
    - DB_PASSWORD=\<password>
- Create virtual environment
  - python3 -m venv venv
  - source venv/bin/activate
- Install Dependencies
  - pip install -r requirements.txt
- Run migrations
  - python manage.py makemigrations
  - python manage.py makemigrations user
  - python manage.py makemigrations storage
  - python manage.py makemigrations files
  - python manage.py migrate
- Create admin user for app
  - python manage.py createsuperuser
- Configure NGINX
  - sudo apt install nginx -y
  - sudo systemctl start nginx
  - sudo systemctl enable nginx
  - create config file in /etc/nginx/sites-available/project (replace \<server ip address> \<username> with created username)
  ```
  server {
          listen 80;
          server_name <server ip address>;

          root  /usr/share/nginx/html;
          index index.html;

          location / {
                  try_files $uri /index.html;
  }

          location ~  \.(js|css)$ {
                  rewrite ^.+?(/assets/.*) $1 break;
  }

          location /backend/ {
                  include proxy_params;
                  rewrite ^/backend(.*) $1 break;
                  proxy_pass http://unix:/home/<username>/NetoCloudBackend/NetoCloud/project.sock;
          }
  }
  ```
  - sudo ln -s /etc/nginx/sites-available/project /etc/nginx/sites-enabled/
  - sudo systemctl restart nginx

- Configure gunicorn
  - sudo apt install gunicorn -y
  - pip install gunicorn
  - create config file in /etc/systemd/system/gunicorn.service (replace \<username> with created username)
  ```
  [Unit]
  Description=service for gunicorn
  After=network.target

  [Service]
  User=<username>
  Group=www-data
  WorkingDirectory=/home/<username>/NetoCloudBackend
  ExecStart=/home/<username>/NetoCloudBackend/venv/bin/gunicorn --access-logfile - --workers 3 -b unix:/home/<username>/NetoCloudBackend/NetoCloud/project.sock NetoCloud.wsgi:application

  [Install]
  WantedBy=multi-user.target
  ```
  - sudo systemctl start gunicorn
  - sudo systemctl enable gunicorn
  - sudo systemctl daemon-reload
  - sudo systemctl restart gunicorn
- Deploy Frontend https://github.com/Nilumilak/NetoCloudFrontend
