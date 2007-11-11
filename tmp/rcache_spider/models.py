## # This is an auto-generated Django model module.
## # You'll have to do the following manually to clean this up:
## #     * Rearrange models' order
## #     * Make sure each model has one field with primary_key=True
## # Feel free to rename the models, but don't rename db_table values or field names.
## #
## # Also note: You'll have to insert the output of 'django-admin.py sqlinitialdata [appname]'
## # into your database.

## from django.db import models

## class User(models.Model):
##     id = models.IntegerField(primary_key=True)
##     company_id = models.IntegerField(null=True, blank=True)
##     first_name = models.CharField(blank=True, maxlength=300)
##     last_name = models.CharField(blank=True, maxlength=300)
##     email = models.CharField(maxlength=300)
##     website = models.CharField(blank=True, maxlength=300)
##     blogurl = models.CharField(blank=True, maxlength=300)
##     login = models.CharField(unique=True, maxlength=60)
##     password = models.CharField(blank=True, maxlength=120)
##     date_created = models.DateTimeField(null=True, blank=True)
##     last_contact = models.DateTimeField(null=True, blank=True)
##     active = models.IntegerField(null=True, blank=True)
##     def __str__(self):
##         return "%s, %s" % (self.last_name, self.first_name)
##     class Meta:
##         db_table = '_user'
##     class Admin:
##         pass

## class BetaUser(models.Model):
##     id = models.IntegerField(primary_key=True)
##     email = models.CharField(unique=True, maxlength=300)
##     date_created = models.DateTimeField(null=True, blank=True)
##     reason_for_use = models.TextField(blank=True)
##     class Meta:
##         db_table = 'beta_user'
##     class Admin:
##         pass

## class CatwalkStateTable(models.Model):
##     id = models.IntegerField(primary_key=True)
##     state = models.TextField(blank=True)
##     class Meta:
##         db_table = 'catwalk_state_table'

## class Company(models.Model):
##     id = models.IntegerField(primary_key=True)
##     company_name = models.CharField(blank=True, maxlength=300)
##     description = models.CharField(blank=True, maxlength=765)
##     date_created = models.DateTimeField(null=True, blank=True)
##     class Meta:
##         db_table = 'company'
##     class Admin:
##         pass

## class Entry(models.Model):
##     id = models.IntegerField(primary_key=True)
##     user_id = models.IntegerField(null=True, blank=True)
##     url = models.CharField(blank=True, maxlength=765)
##     entry_name = models.CharField(blank=True, maxlength=765)
##     description = models.CharField(blank=True, maxlength=765)
##     text_content = models.TextField(blank=True)
##     html_content = models.TextField(blank=True)
##     date_created = models.DateTimeField(null=True, blank=True)
##     last_access = models.DateTimeField(null=True, blank=True)
##     summary = models.TextField(blank=True)
##     class Meta:
##         db_table = 'entry'
##     class Admin:
##         list_display = ('entry_name','url', 'date_created')
##         search_fields = ['url','entry_name']
    
## class EntryTag(models.Model):
##     entry_id = models.IntegerField()
##     tag_id = models.IntegerField()
##     class Meta:
##         db_table = 'entry_tag'
##     class Admin:
##         pass
    
## class EntryUrl(models.Model):
##     id = models.IntegerField(primary_key=True)
##     user_id = models.IntegerField(null=True, blank=True)
##     url = models.CharField(blank=True, maxlength=765)
##     date_created = models.DateTimeField(null=True, blank=True)
##     entry_id = models.IntegerField()
##     class Meta:
##         db_table = 'entry_url'
##     class Admin:
##         list_display = ('url', 'date_created')
##         search_fields = ['url']
    
## class Media(models.Model):
##     id = models.IntegerField(primary_key=True)
##     entry_id = models.IntegerField(null=True, blank=True)
##     path = models.CharField(blank=True, maxlength=765)
##     date_created = models.DateTimeField(null=True, blank=True)
##     last_access = models.DateTimeField(null=True, blank=True)
##     original_file = models.TextField(blank=True)
##     class Meta:
##         db_table = 'media'
##     class Admin:
##         pass
    
## class Snippet(models.Model):
##     id = models.IntegerField(primary_key=True)
##     user_id = models.IntegerField(null=True, blank=True)
##     entry_id = models.IntegerField(null=True, blank=True)
##     date_created = models.DateTimeField(null=True, blank=True)
##     active = models.IntegerField(null=True, blank=True)
##     snippet = models.TextField(blank=True)
##     class Meta:
##         db_table = 'snippet'
##     class Admin:
##         pass
    
## class SqlobjectDbVersion(models.Model):
##     id = models.IntegerField(primary_key=True)
##     version = models.TextField(blank=True)
##     updated = models.DateTimeField(null=True, blank=True)
##     class Meta:
##         db_table = 'sqlobject_db_version'

## class Tag(models.Model):
##     id = models.IntegerField(primary_key=True)
##     tag = models.CharField(blank=True, maxlength=300)
##     user_id = models.IntegerField()
##     tag_count = models.IntegerField(null=True, blank=True)
##     class Meta:
##         db_table = 'tag'
##     class Admin:
##         list_display = ('tag','tag_count')
##         search_fields = ['tag']
    
## class TagGroup(models.Model):
##     id = models.IntegerField(primary_key=True)
##     tag_id = models.IntegerField(null=True, blank=True)
##     group_name = models.CharField(blank=True, maxlength=300)
##     class Meta:
##         db_table = 'tag_group'
##     class Admin:
##         pass
    
## class Url(models.Model):
##     id = models.IntegerField(primary_key=True)
##     user_id = models.IntegerField()
##     url = models.CharField(blank=True, maxlength=765)
##     tags = models.CharField(blank=True, maxlength=765)
##     date_attempted = models.DateTimeField()
##     entry = models.IntegerField(null=True, blank=True)
##     class Meta:
##         db_table = 'url'
##     class Admin:
##         pass
