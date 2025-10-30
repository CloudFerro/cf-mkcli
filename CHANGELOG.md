Changelog
=========

0.6.1 (16/09/2025)
------------------
1. fix initialisation of new session when API key not set as ENV neither by auth init prompt
1. fix calling wrong backend address when using dev env
1. allow setting empty API key why initialising context (auth init)
1. fix versioning pipeline

0.6.0 (12/09/2025)
------------------
1. update Cluster model validation after mk8s-api changed with v0.6.0
1. add setting and clearing api key
1. keep api keys in context data
1. make api key default auth method
1. add more unit test to be sure that both auth mechanisms are changes resiliant

0.5.1 (09/09/2025)
------------------
move MK8S api url out of app settings (add mapping between realm name and API url)

0.5.0 (08/09/2025)
------------------
add auto versioning

list (05/09/2025)
-----------------
add support for API tokens

0.2.0 (19/08/2025)
------------------
added unit tests, versioning, better error management, using many realms
