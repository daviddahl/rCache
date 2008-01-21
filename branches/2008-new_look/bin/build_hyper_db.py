#initially all data must be moved from the old MySQL to the new and convert all tables to utf-8


from rcache.hyper import util
util.create()
util.load()

# this creates a 'casket' at /var/hyper/casket

# must move /var/hyper/casket  to /var/hyper/_node/rcache
# must chown -R root:rcache /var/hyper/_node/rcache
# must chmod -R 775 /var/hyper/_node/rcache
