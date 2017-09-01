import random
import string
import sys
import os

PROJECT_PATH = 'djangofiles'
SETTINGS_FILE = 'server.settings'

sys.path.append(PROJECT_PATH)
sys.path.append(os.path.basename(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)
import django

django.setup()

ranks = ["Klipsu I", "Klipsu II", "Klipsu III", "Klipsu IV", "Klipsu Mestari", "Klipsu Eliitti Mestari",
         "Kultapossu I", "Kultapossu II", "Kultapossu III", "Kultapossu Mestari", "Mestari Heittäjä I",
         "Mestari Heittäjä II", "Mestari Heittäjä Eliitti", "Arvostettu Jallu Mestari", "Legendaarinen Nalle",
         "Legendaarinen Nalle Mestari", "Korkein Ykkösluokan Mestari", "Urheileva Alkoholisti"]

from frisbeer.models import Rank, Player
from frisbeer.signals import calculate_ranks

Rank.objects.all().delete()

i = len(ranks) + 1
for r in ranks:
    i -= 1
    rank = Rank(name=r, image_url="ranks/{}.png".format(r.replace(" ", "-")), numerical_value=i)
    rank.save()

calculate_ranks(Player.objects.all().values_list('id', flat=True))

from django.contrib.auth.models import User

password = ''.join(random.choices(string.punctuation + string.ascii_letters + string.digits, k=10))
u, created = User.objects.get_or_create(username="admin")
if created:
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.is_active = True
    u.save()
    print(password)
