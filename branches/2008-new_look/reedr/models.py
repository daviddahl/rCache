import os

from django.db import models
from django.db import connection

from rcache.models import User

#from rcache.hyper.client import HyperClient as h


class Category(models.Model):
    """
    feed categories
    """
    category = models.CharField(maxlength=255)
    user = models.ForeignKey(User)

    class Admin:
        pass


class Feed(models.Model):
    """
    an rss feed
    """
    url = models.CharField(maxlength=255)
    title = models.CharField(maxlength=255)
    description = models.CharField(maxlength=1024)
    user = models.ForeignKey(User)

    class Admin:
        pass

# build up a history of all feeds read by the rss reader in a Hyperestraier index

