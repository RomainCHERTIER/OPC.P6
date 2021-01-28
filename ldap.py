
# Creates new entry in LDAP for given user
def create_user(user, admin_pass):
    dn = 'uid=' + user['username'] + ',' + LDAP_BASE_DN
    fullname = user['firstname'] + ' ' + user['lastname']
   # home_dir = HOME_BASE + '/' + user['username']
    #gid = find_gid(user['group'])
    #lastchange = int(math.floor(time() / 86400))

    entry = []
    entry.extend([
        ('objectClass', ["person", "organizationalPerson", "inetOrgPerson", "posixAccount", "top", "shadowAccount", "hostObject"]),
        #('uid', user['username']),
        ('cn', fullname),
        ('givenname', user['firstname']),
        ('sn', user['lastname']),
       #('mail', user['email']),
        #('uidNumber', str(user['uid'])),
        #('gidNumber', str(gid)),
       #('loginShell', user['shell']),
        #('homeDirectory', home_dir),
        #('shadowMax', "99999"),
        #('shadowWarning', "7"),
        #('shadowLastChange', str(lastchange)),
        ('userPassword', user['password'])
    ])
    if (len(user['hosts'])):
        entry.append( ('host', user['hosts']) )

    ldap_conn = ldap.initialize(LDAP_HOST)
    ldap_conn.simple_bind_s(LDAP_ADMIN_DN, admin_pass)

    try:
        ldap_conn.add_s(dn, entry)
    finally:
        ldap_conn.unbind_s()
