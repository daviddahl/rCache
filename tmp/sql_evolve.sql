--Entry: entry_url = models.CharField(blank=True, maxlength=765)

ALTER TABLE entry ADD COLUMN entry_domain varchar(200) NOT NULL;

-- add extra index for tag maint. script
CREATE index tag_id_idx ON entry_tag (tag_id);
