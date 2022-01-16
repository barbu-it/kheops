* 104: Best practices
  - Going into IaC
    + Use git to track your tree
    - D.R.Y.
      + Things are quite easily moving
  - Code structure
    + Profile and Class
      * Role and profiles key lookup
    + Hierarchies
      * Foreman
    + Use environnements, site, locatation ...
    + Common keys vs dedicated keys
      * The profile key, default placeholder
    + The resource modele
      * It's like a puppet resource, a catalog of items to apply
      * It's possible to use this model with ansible, and it change radically the way Ansible can be used then. See integration.
  - Debugging
    + Use the explain mode
      * And trace mode
    + Use GNU tools
      * tree
      * grep -Rw <key> .
      * git status -sb
  - With ansible.
    + Use a strict naming scheme, apply your Ansible usual name schema into Albero
    + You can put some jinja variable into Albero, Ansible will be able to replace and understand them during the runtime
    + Dynamic inventories and ENC
    + Apply products
    + Apply roles/profiles pattern
    + Use resource based roles => See my collection, it just works
