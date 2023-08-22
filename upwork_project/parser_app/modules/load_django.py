import sys
import os
import django

sys.path.append(os.path.abspath("upwork_project"))
os.environ['DJANGO_SETTINGS_MODULE'] = 'upwork_project.settings'
django.setup()
