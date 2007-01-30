from django.db import models


class Company(models.Model):
    company_name = models.CharField(blank=True, maxlength=300)
    description = models.CharField(blank=True, maxlength=765)
    date_created = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.company_name
    class Meta:
        db_table = 'company'
    class Admin:
        list_display = ('company_name', 'description')
        
class User(models.Model):
    company = models.ForeignKey(Company)
    first_name = models.CharField(blank=True, maxlength=300)
    last_name = models.CharField(blank=True, maxlength=300)
    email = models.CharField(unique=True,maxlength=64)
    website = models.CharField(blank=True, maxlength=300)
    blogurl = models.CharField(blank=True, maxlength=300)
    login = models.CharField(unique=True, maxlength=64)
    password = models.CharField(maxlength=64)
    date_created = models.DateTimeField(auto_now_add=True)
    last_contact = models.DateTimeField(auto_now_add=True)
    active = models.IntegerField(default=0)
    user_url = models.CharField(blank=True, maxlength=255)
    def __str__(self):
        return "%s : %s %s %s" %(self.id,self.login, self.first_name, self.last_name)
    class Meta:
        db_table = '_user'
    class Admin:
        list_display = ('email','login','first_name', 'last_name')
    
class BetaUser(models.Model):
    email = models.CharField(unique=True, maxlength=300)
    date_created = models.DateTimeField(null=True, blank=True)
    reason_for_use = models.TextField(blank=True)
    def __str__(self):
        return "%s" %(self.email)
    class Meta:
        db_table = 'beta_user'
    class Admin:
        list_display = ('email','date_created')
    
class Tag(models.Model):
    tag = models.CharField(blank=True, maxlength=300)
    user = models.ForeignKey(User)
    tag_count = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.tag

    def tag_list(self,_user,which_q='default'):
        from django.db import connection
        cursor = connection.cursor()
        q = """SELECT DISTINCT tag, tag_count FROM tag WHERE user_id = %s
        ORDER BY tag_count DESC LIMIT 200"""
        if which_q == 'alpha':
            q = """SELECT DISTINCT tag,tag_count FROM tag WHERE user_id = %s
            ORDER BY tag"""
        if which_q == 'all':
            q = """SELECT DISTINCT tag,tag_count FROM tag WHERE user_id = %s
            ORDER BY tag_count DESC"""
            
        cursor.execute(q,[_user.id])
        rows = cursor.fetchall()
        return rows

    def normalize_tags(_user):
        """get all tags loop through them sorted by tag, tag_count"""
        pass
        
    class Meta:
        db_table = 'tag'
    class Admin:
        list_display = ('tag','user','tag_count')       
    
class Entry(models.Model):
    user = models.ForeignKey(User)
    entry_url = models.CharField(blank=True, maxlength=765)
    #alter db on turbogears side
    entry_domain = models.CharField(blank=True, maxlength=200)
    entry_name = models.CharField(blank=True, maxlength=765)
    description = models.CharField(blank=True, maxlength=765)
    text_content = models.TextField(blank=True)
    html_content = models.TextField(blank=True)
    date_created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True,auto_now=True)
    summary = models.TextField(blank=True)
    tag = models.ManyToManyField(Tag)
    
    def __str__(self):
        return self.entry_name

    def fulltxt(self,_user,kw):
        """Fulltext search on Entries sorted by relevence"""
        from django.db import connection
        cursor = connection.cursor()
        
        q = """SELECT id,entry_url, entry_name, date_created,
        MATCH(text_content) AGAINST (%s) AS score
        FROM entry
        WHERE MATCH (text_content) AGAINST (%s)
        AND user_id = %s"""
            
        cursor.execute(q,[kw,kw,_user.id])
        rows = cursor.fetchall()
        return rows

    def domain_list(self,_user):
        from django.db import connection
        cursor = connection.cursor()
        q = """SELECT DISTINCT entry_domain FROM entry WHERE user_id = %s
        ORDER BY entry_domain"""
            
        cursor.execute(q,[_user.id])
        rows = cursor.fetchall()
        return rows
    
    class Meta:
        db_table = 'entry'
    class Admin:
        list_display = ('entry_url','user','entry_name','description')  

class EntryUrl(models.Model):
    url = models.CharField(maxlength=765)
    date_created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    entry = models.ForeignKey(Entry)
    user = models.ForeignKey(User)
    
    class Meta:
        db_table = 'entry_url'
    class Admin:
        list_display = ('url','user','date_created',)
        search_fields =['url',]

class Url(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(blank=True, maxlength=765)
    tags = models.CharField(blank=True, maxlength=765)
    date_attempted = models.DateTimeField()
    entry = models.ForeignKey(Entry)
    def __str__(self):
        return self.url

    class Meta:
        db_table = 'url'
    class Admin:
        list_display = ('url','user','tags','date_attempted') 

## class EntryTag(models.Model):
##     entry_id = models.IntegerField()
##     tag_id = models.IntegerField()
##     class Meta:
##         db_table = 'entry_tag'

## class EntryUrl(models.Model):
##     user = models.ForeignKey(User)
##     url = models.CharField(blank=True, maxlength=765)
##     date_created = models.DateTimeField(null=True, blank=True)
##     entry = models.ForeignKey(Entry)
##     class Meta:
##         db_table = 'entry_url'

class Media(models.Model):
    entry = models.ForeignKey(Entry)
    path = models.CharField(blank=True, maxlength=765)
    date_created = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True)
    #fixme: need to download and encode - store string here 
    original_file = models.TextField(blank=True)
    class Meta:
        db_table = 'media'
    class Admin:
        list_display = ('entry','path','date_created')  
    
class Snippet(models.Model):
    user = models.ForeignKey(User)
    entry = models.ForeignKey(Entry)
    date_created = models.DateTimeField(null=True, blank=True)
    active = models.IntegerField(null=True, blank=True)
    snippet = models.TextField(blank=True)
    def __str__(self):
        return self.snippet
    class Meta:
        db_table = 'snippet'
    class Admin:
        list_display = ('snippet','user','entry')
    
class TagGroup(models.Model):
    tag = models.ForeignKey(Tag)
    group_name = models.CharField(blank=True, maxlength=300)
    class Meta:
        db_table = 'tag_group'
    class Admin:
        pass

class EntryDictionary(models.Model):
    #need to add all stemmed words here
    #need to look up exisitng dictionary entry b4 adding a new one, perhaps also have an index that ties fk user to stemmed_word??
    pass
