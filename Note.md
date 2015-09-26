###Code Organization

- /main.py
	- urlmapping
- /handlers.py
	- blog handler
	- ascii chan handler
	- wiki handler
- /lib
	- /db/models.py
		- Post
		- User
		- Art
		- Page
	- utils.py
 		- handy functions
- /static
	- css
	- js
	- img
- /templates 


###Hosting
- Local
	- fine for single user
	- not always on
	- not always accessible
	- IP always change
- Co-locate
	- control the machines
	- pay rent, power, bandwidth
	- high work
- Managed hosting
	- rent machines
		- AWS
		- Rackspare
		- Linode
	- medium sys-admin
- GAE / Heroku
	- no machine, no os
	- zero sys-admin
	- difficult customization


###Framework
- Important Features
	- base HTTP
	- direct GET / POST 
	- request
	- headers access
- non-important
	- sessions
	- caching
	- forms
	- DB-ORM
	- 'magic things' etc.
- templates
	- seprate code from templates
	- keep code in templates in minimum


###Early Reddit Architecture
- lisp -> python
- [linux supervise](http://cr.yp.to/daemontools.html)
- [slony](http://slony.info/)
- Spread -> memcached
- lots of joins, painful to add new features, big migrations
- ThingDB
- Sharding too late
- web.py
- hacked up version of Pylons
- precomputed cache
	- every time a vote come in, put it in a job queue
	- precomputed servers take jobs off the queue
	- touch precomputed database
	- store results to memcached

####Load balancer
- CDN Akamai: for logged out users only
- HA proxy

####App Server Architecture
- Pylons
- S3 for static content(js, css, img...)
- Nginx for static content

####Database Architecture
- split apart the data types
	- links, users
	- votes
	- comments, subreddits
- don't do joins
- replicate
	- Londiste
		- when write to master
		- hit trigger insert same querys into a queue
		- then replicated to all slaves

####Cache Architecture
- render cache on the server
- memcaches
	- avoid replication lag
- precomputed cache
	- mirror database as precompute cluster
	- put compute data in memcache DB(persist)


###Morden Reddit Architecture
- replace memcachedb with Cassandra for precomputed cache
	- replication factor of 3
	- sharding ring
- memcache locking problem
	- lose single memcache node is painful
- consistent hashing
	- 10 nodes, 1 node down, 1/10 keys get redistributed, instead of 9/10
- Zookeeper
	- avoid single node failing
	- Q: ```deploying a new configuration, 
		   once you have more than a couple app servers,
                  often deploys take time, all of a sudden, you've got 
                  half app servers with diff configuration.``` 
	- memcache is all queries are initiated from the apps
	- zookeeper will push
- memcache ejection
	- not use the bad node until the locking is gone, it'll auto heal itself
	- so you can add more memcache, but even consistent hashing, it got problem sometime
- precompute architecture
	- lots of precompute queries can mutates in place by using Cassandra
	- so mirror database as precompute cluster never need anymore
	- Q: ```top links of this hour?```  using mapreduce
- MapReduce
	- dump every submit links last hour, groups them up, overwrites every 10-15 mins
	- one slave for links dedicated, running mapreduce jobs, then stored in Cassandra
- Hadoop
	- Pig
	- Amazon EMR
- Search indexing
	- build a whole separate infrastructure just for Google
	- so separate from users
- Queue
	- AMQP (now)
	- RabbitMQ (early)
- Lock contention
	- get rid of locking in Cassandra by using queue processors 
	- enough queue processors to handle the depth of the queue
	- but if you have many, they spend too much time fighting each other
	-  Python threads locking
	- make python single threaded
	- only handle one request at the same time
	- rarely use threaded processes
	- lots of separate processes 1 machine, os can task switching for you
