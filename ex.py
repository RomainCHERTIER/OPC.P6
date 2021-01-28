#!/usr/bin/env python
import glob

from optparse import OptionParser
import sys
import os, os.path

import ldap
import ldap.modlist as modlist
import csv



VERSION="0.1"
PROG="majldap"
DESCRIPTION="mise a jour ldap par fichier csv"
AUTHOR="Service Informatique Mysociety"


def read_csv(file_csv):
    data = []
    objs = []
    reader = csv.reader(open(file_csv, "rb"), delimiter=';')
    for row in reader:
        data.append(row)
    for i in data[1:]:
        obj = {}
        for j in range(0, len(data[0])):
            obj[data[0][j]] = i[j]
        objs.append(obj)
    return objs

def update_ldap(ldap_client, searchScope, retrieveAttributes, obj, level1):
    if level1 == True:
        searchFilter = "sn=*%(sn)s*" % obj
    else:
        searchFilter = "(&(sn=*%(sn)s*) (givenName=*%(givenName)s*))" % obj
    try:
        results = ldap_client.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)
        for dn,entry in results:
            print (dn)
        #results = [(dn,entry) for dn,entry in results if dn <> None ]
    except Exception, e:
        raise "%s %s %s" % (obj['sn'], obj['givenName'], parser.error(e))
    if len(results) == 0:
        raise Exception ("%(sn)s %(givenName)s does not exist" % obj)
    if len(results) == 1:
        dn,entry = results[0]
        for i in obj.keys():
            if i not in ('sn','givenName'):
                old = {i:entry.get(i,'')}
                new = {i:obj[i]}
                ldif = modlist.modifyModlist(old,new)
                ldap_client.modify_s(dn,ldif)
    if len(results) > 1:
        if level1 == True:
            update_ldap(ldap_client, searchScope, retrieveAttributes, obj, False)
        else:
            raise Exception ("multi result for %(sn)s %(givenName)s" % obj)

if __name__ == '__main__':
    parser = OptionParser(version="%s %s" % (PROG,VERSION))
    parser.description= DESCRIPTION
    parser.epilog = AUTHOR
    parser.add_option("-p", "--password",
        dest="password",
        help ="password pour connexion ldap",
        default="",
        type="string")
    parser.add_option("-u", "--user",
        dest="user",
        help ="user pour connexion ldap",
        default="",
        type="string")
    parser.add_option("-s", "--server",
        dest="server",
        help ="serveur ldap pour connexion ldap",
        default="ldap://myservdc1",
        type="string")
    parser.add_option("-f", "--file",
        dest="file",
        help ="fichier csv",
        default="",
        type="string")
    parser.add_option("-b", "--base-dn",
        dest="basdn",
        help ="baseDN",
        default="DC=Myprop,DC=fr",
        type="string")
    (options, args) = parser.parse_args()
    try:
        password = options.password
        user = options.user
        server = options.server
        csv_file = options.file
        baseDN = options.basdn
        objs = read_csv(csv_file)
        ldap_client = ldap.initialize(server)
        ldap_client.set_option(ldap.OPT_REFERRALS,0)
        ldap_client.simple_bind_s(user, password)
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        for obj in objs:
            try:
                print "TREATMENT %(sn)s %(givenName)s" % obj
                update_ldap(ldap_client, searchScope, retrieveAttributes, obj, True)
            except Exception, e:
                print e
    except Exception, e:
        print parser.error(e)
        parser.print_help()
        sys.exit(1)