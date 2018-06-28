import os
import sys

__all__ = (
    "Crawlpage",
    "Keyword",
    "Webpage",
)

import django

pwd = os.path.dirname(os.path.abspath(__file__))
project = os.path.abspath(os.path.join(pwd, '../../cspider'))
#print(project)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspider.settings")
if project in sys.path:
    PROJECT_EXISTS = True
else:
    sys.path.append(project)
    PROJECT_EXISTS = False

django.setup()
from m.models import Crawlpage, Keyword, Webpage

if PROJECT_EXISTS:
    sys.path.remove(project)
