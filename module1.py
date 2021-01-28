import ldap
import ldap.modlist as modlist
def update_ldap(ldap_client, searchScope, retrieveAttributes, obj, level1,baseDN):
    if level1 == True:
        searchFilter = "sAMAccountName=*%(login)s*" % obj
    else:
        searchFilter = "(&(sAMAccountName=*%(login)s*) (givenName=*%(prenom)s*))" % obj
    try:
        results = ldap_client.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)
        for dn,entry in results:
            print (dn)
        #results = [(dn,entry) for dn,entry in results if dn <> None ]
    except Exception as e :
        raise "%s %s %s" % (obj['login'], obj['prenom'], parser.error(e))
    #if len(results) == 0:
       # raise Exception ("%(login)s %(prenom)s does not exist" % obj)
   # if len(results) == 1:
      #  dn,entry = results[0]
       # for i in obj.keys():
           # if i not in ('login','prenom'):
               # old = {i:entry.get(i,'')}
                #new = {i:obj[i]}
               # ldif = modlist.modifyModlist(old,new)
               #ldap_client.modify_s(dn,ldif)
    #if len(results) > 1:
       # if level1 == True:
       #    # update_ldap(ldap_client, searchScope, retrieveAttributes, obj, False)
        #else:
           # raise Exception ("multi result for %(sn)s %(givenName)s" % obj)


try:

        ldap_client = ldap.initialize("ldap://127.0.0.1")
        ldap_client.set_option(ldap.OPT_REFERRALS,0)
        ldap_client.simple_bind_s(user, password)
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        baseDN = "CN=Users,DC=P6,DC=local"
        obj= {'login':'t.dupont','prenon':'toto'}
        level1 = true
        update_ldap(ldap_client, searchScope, retrieveAttributes, obj, level1,baseDN)
except Exception as e :
    print (parser.error(e))



