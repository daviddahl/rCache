from django.db import models
from django.db import connection

from rcache.hyper.client import HyperClient as h


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
        return "%s : %s %s %s" \
               % (self.id,self.login, self.first_name, self.last_name)
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

    def empty_tags(self,_user):
        """Get empty tags - tags that are not attached to an Entry """
        q = """SELECT tag.tag,tag.id,entry_tag.tag_id FROM
               tag left join entry_tag ON entry_tag.tag_id = tag.id
               WHERE entry_tag.tag_id is NULL AND tag.user_id = %s"""
        cursor = connection.cursor()
        cursor.execute(q,[_user.id])
        rows = cursor.fetchall()
        return rows

    def kill_tags(self,_user,tag_list):
        """remove tags in list of ids"""
        for tag in tag_list:
            try:
                t = Tag.objects.filter(user=_user.id,id=tag['id'])
                t[0].delete()
            except Exception, e:
                print str(e)
                pass

    def normalize_tags(self,_user):
        """get all tags loop through them sorted by tag, tag_count"""
        pass
        
    def existing_tags(self,entry_id):
        cursor = connection.cursor()
        q = """SELECT et.id,et.tag_id,et.entry_id,t.tag
        FROM entry_tag et, tag t where et.entry_id = %s
        AND t.id = et.tag_id"""
        cursor.execute(q,[entry_id,])
        rows = cursor.fetchall()
        return rows

    def remove_tag(self,tag_id):
        try:
            cursor = connection.cursor()
            q = """DELETE FROM entry_tag WHERE id = %s"""
            cursor.execute(q,[tag_id,])
            return True
        except:
            return False

    def add_a_tag(self,entry,tag):
        try:
            entry.tag.add(tag)
            return True
        except:
            return False
        

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

    def entry_count(self,user_id):
        cursor = connection.cursor()
        q = """SELECT COUNT(id) FROM entry WHERE user_id = %s"""
        cursor.execute(q,[user_id,])
        row = cursor.fetchone()
        return row[0]
    
    def __str__(self):
        return self.entry_name

    def get_absolute_url(self):
        return "/detail/%s/" % self.id
    
    def hypersearch(self,query,user):
        """
        search the hyperestraier index via the p2p client
        """
        hyper = h()
        res = hyper.search(query)
        lst = hyper.id_lst()
        if len(lst) > 0:
            in_str = "id IN (%s)" % ",".join(lst)
            qs = Entry.objects.filter(user=user).extra(where=in_str)
        else:
            return []
        return qs

    def fulltxt(self,_user,kw):
        """Fulltext search on Entries sorted by relevence"""
        from django.db import connection
        cursor = connection.cursor()
        #fixme: look into these tweaks
        #WHERE MATCH (text_content) AGAINST (%s WITH QUERY EXPANSION)
        #ft_min_word_length 
        q = """SELECT id,entry_url, entry_name, date_created,
        MATCH(text_content) AGAINST (%s) AS score
        FROM entry
        WHERE MATCH (text_content) AGAINST (%s WITH QUERY EXPANSION)
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

class UserEvent(models.Model):
    """keep track of user signup, password change events, other events"""
    user = models.ForeignKey(User)
    hash_key = models.CharField(maxlength=120)
    event_date = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(maxlength=100)
    open = models.BooleanField(default=True)
    EVENT_CHOICES = ('Create Account','Accept Account',
                     'Password Change Request',
                     'Password Changed',
                     'Data Dump Request',
                     'Close Account',
                     'Create Colleague',
                     'Remove Colleague',
                     'Tech Support',)
    
    class Admin:
        list_display = ('user','hash_key','event_type','event_date','open',)
    
class Colleague(models.Model):
    """a user who is granted access to an rCache user's data"""
    colleague = models.ForeignKey(User) #colleague user obj
    user_id = models.IntegerField()     #currently logged in user id
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    tag_restrictions = models.BooleanField(default=True)
    tags_approved = models.TextField()
    search_restrictions = models.BooleanField(default=True)
    search_keywords_approved = models.TextField()
    commentary = models.BooleanField(default=True)

    def __str__(self):
        return self.colleague.login
    
    class Admin:
        pass

class ColleagueGroup(models.Model):
    """A group of Colleagues that a user can address with
    a single message or connection"""
    user = models.ForeignKey(User)
    group_name = models.CharField(maxlength=100)
    description = models.CharField(maxlength=255)
    colleague = models.ManyToManyField(Colleague)

    class Admin:
        pass
    
class Commentary(models.Model):
    """Commentary has a one to one relationship with Entry."""
    user = models.ForeignKey(User)
    entry = models.ForeignKey(Entry)
    title = models.CharField(maxlength=255,blank=True)
    summary = models.TextField(blank=True)

    class Admin:
        list_display = ('entry','title','user',)
 
class Snippet(models.Model):
    """A piece of text from an entry that a user comments on"""
    user = models.ForeignKey(User)
    entry = models.ForeignKey(Entry)
    commentary = models.ForeignKey(Commentary)
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.IntegerField()
    snippet = models.TextField()
    sortorder = models.IntegerField(blank=True)
    
    def __str__(self):
        return self.snippet

    class Admin:
        list_display = ('snippet','user','entry',) 
        
class Comment(models.Model):
    """Comments are related to commentary and Snippits"""
    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, related_name='child_set')
    snippet = models.ForeignKey(Snippet)
    comment = models.TextField()
    sortorder = models.IntegerField(blank=True)

    class Admin:
        list_display = ('user','comment',)

class Folio(models.Model):
    """A Folio is a bag of entries that are categorized in a larger scope"""
    user = models.ForeignKey(User)
    folio_name = models.CharField(maxlength=255)
    description = models.TextField(blank=True,null=True)
    entry = models.ManyToManyField(Entry)
    
    class Admin:
        list_display = ('folio_name','description','user',)
