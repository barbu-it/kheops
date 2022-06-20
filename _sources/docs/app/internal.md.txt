
# Internals


* 101: TECHINICAL How works a hierarchical data lookup? 
  - Query a key
    + Can be a simple string or complex data
    + Can be anything in json compatible
  - Kheops will resolve query in 2 parts:
    + It will first look in different locations the key. It is usually files, but it can also be an url or anything. The queried data must be a valid json data type (TOFIX: So it works also for yaml, toml .... it supports [anyconfig](https://github.com/ssato/python-anyconfig) )
      * Example: The `path` strategy will allow you to target 
    + Then it will process all results and load a strategy to resolve which results to keep. 
      Example: The `last` strategy consists in keeping always the last result while the `merge` strategy consists in merging inteligentelly data. This is quite useful for dict or lists.
    + 
  - Lookup data in a tree of files
    + Goes sequentially according the backends list
      * Backend/Engine list is modular
      * Engine Plugin: Jerakia/HIera/Ansible/Curl
      * Backend Plugin: loop/hier
    + All result are returned, and then the rules are applied
    + Rules match to a key and apply a strategy (essentially determine if and how the different value are merged or replaced). It can also apply filter to the result and modify its content (future).
      * This is modular
      * Strategy: last/schema
        - Last will always take the last found value, whatever what it previously found. 
        - schema: It will take into account the strucutre of the data and try to merge them intelligentelly. See more on 
    + Then it returns the result
  - Use cases
    + Ansible integration
    + Generic SOT
    + Rest API (Future)
    + More !!!!
    


