# Djangogramm

## Description
The project is designed as a training project to simulate an Instagram-like messaging service.

## Technologies used
`Django`, `PostgreSQL`, `Nginx`, `bootstrap`, `Ajax`, `jQuery`, `Django ORM`, `webpack`,  
`Django-allauth`, `cloudinary`, `unittest`



## Getting started

To make it easy for you to get started with Djangogramm, 
here's a list of recommended next steps.


## Download
Download the repository with this command: 
```bash
git clone https://github.com/Shtierlitz/Djangogramm.git
```

## Create Files
For the local server to work correctly, create your own file `local_settings.py` 
and place it in a folder next to the file `settings.py` of this Django project.
You will also need to create `.env` file and place it in the root of the project.

### Required contents of the local_settings.py file:
```python  
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


STATIC_ROOT = os.path.join(BASE_DIR, 'static')
WAGTAILADMIN_BASE_URL = 'http://127.0.0.1:8000/'
```

### Required contents of the .env file:
```python
WEATHER_API_KEY='<your OpenWeatherMap token>'  
WEATHER_BIT_KEY='<your WeatherBit token>'  
SECRET_KEY='<your SECRET key>'   

EMAIL_HOST_USER="<your email>"  
EMAIL_HOST_PASSWORD="<your google app password>"  
DEFAULT_FROM_EMAIL="<your email>"  
RECIPIENTS_EMAIL="<your email>"  

DB_NAME="<database name>"  
DB_USER="<database username>"  
DB_PASSWORD="<database password>"  
DB_HOST="localhost"

CLOUD_NAME="<your cloudinary name"
API_KEY="<your cloudinary api key"
API_SECRET="your cloudinary api secret key"
```

# Localhost development

## Django run
To run localhost server just get to the folder where `manage.py` is and then run the command:
```bash
python manage.py runserver
```
## Test 

To run tests from the localhost, type in the folder next to the file `manage.py`:  
```bash
python manage.py test djangogramm.tests
````


# Sources
Django https://docs.djangoproject.com/en/4.2/   
Ajax\jQuery https://api.jquery.com/category/ajax/  
Bootstrap https://getbootstrap.com/docs/5.0/getting-started/introduction/  
Django-allauth https://django-allauth.readthedocs.io/en/latest/   
DjangoSchool https://www.youtube.com/@DjangoSchool  