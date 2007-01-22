--Entry: entry_url = models.CharField(blank=True, maxlength=765)

ALTER TABLE entry ADD COLUMN entry_domain varchar(200) NOT NULL;
