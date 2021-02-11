
import getpass
import csv
import random
import datetime
import ldap


dataCsvFile = "csvp6.csv"

LDAP_HOST = "ldap://localhost"
LDAP_BASE_DN = "ou=Users,dc=P6,dc=local"
LDAP_ADMIN_DN = "cn=Administrateur,dc=P6,dc=local"
logDir=""
logFile="logP6_"
logFileExt=".log"
userDir=""
userFile="UserP6_"
userFileExt=".txt"

#
# log
#
# création d'un fichier de Log
# @param string level,msg
#
def log(level,msg):
    now = datetime.datetime.now()
    line = now.strftime("%Y%m%d %H%M%S") + " ["+level+"] " + msg
    print(line)
    dateYYYYMMDD = now.strftime("%Y%m%d")
    logAbsPath = logDir + logFile + dateYYYYMMDD + logFileExt
    try:
        fd = open(logAbsPath, "a")
        fd.write(line + "\n")
        fd.close()
    except Exception as err:
        print(" erreur : " + format(err) + "\n")
#
#  logExit
#
# implémentation du fichier de log avec les différentes alerte
# @param string level,msg
#
def logExit(level,msg):
    log(level,msg)
    if(level=="ERROR"):
        exit(2)
    elif(level=="WARNING"):
        exit(1)
    else:
        exit(0)
#
#
# input_ldap_pass
#
# Demande du mot de passe admin Ldap
#
#
def input_ldap_pass():
    try:
        return getpass.getpass("Enter LDAP manager password:")
    except getpass.GetPassWarning:
        logExit("ERROR", "erreur de saisie de mot de passe")
        return ''
#
#
# try_ldap_bind
#
# Connexion au serveur Ldap
# @param string admin_pass
#
#
def try_ldap_bind(admin_pass):
    try:
        ldap_conn = ldap.initialize(LDAP_HOST)
        ldap_conn.simple_bind_s(LDAP_ADMIN_DN, admin_pass)
    except ldap.SERVER_DOWN:
        logExit("ERROR", "Can't contact LDAP server")
    except ldap.INVALID_CREDENTIALS:
        logExit("ERROR", "This password is incorrect!")
    log("INFO", "Authentication successful")

#
# read_csv
#
# lecture du fichier csv
# @param string file_csv chemin du fichier csv
# @return arrey liste des enregistrements csv
#
def read_csv(file_csv):
    data = []
    objs = []
    reader = csv.reader(open(file_csv, "r"), delimiter=';')
    for row in reader:
        data.append(row)
    for i in data[1:]:
        obj = {}
        for j in range(0, len(data[0])):
            obj[data[0][j]] = i[j]
        objs.append(obj)
    return objs

#
# createPwd
#
# génération mot de passe authomatique par rapport au NiveauMDP
# @param string pwdLevel Nom de la valeur NiveauMDP
# @return arrey Mot de passe
#
def createPwd(pwdLevel):
    element = "abcdefghijklmnopkrstuvwxyzABCDEFGHIJKLMNOPKRSTUVWYYZ1234567890-*/~$%&.:?!"
    if pwdLevel == "D1":
        nbCars = 8
    elif pwdLevel == "D2":
        nbCars = 10
    else:
        nbCars = 12
    pwd = ""
    for i in range(nbCars): pwd = pwd + element[random.randint(0, len(element) - 1)]

    return pwd
def addUser(surname,name,login,pwdLevel):
    pwd = createPwd(pwdLevel)
    print (name+" "+surname+" "+pwd)
    dn = login + ',' + LDAP_BASE_DN
    fullname = surname + ' ' + name
    entry = []
    entry.extend([
        ('objectClass',["person".encode('utf-8'), "organizationalPerson".encode('utf-8'), "inetOrgPerson".encode('utf-8'), "posixAccount".encode('utf-8'), "top".encode('utf-8'), "shadowAccount".encode('utf-8'), "hostObject".encode('utf-8')]),
        ("uid", [login.encode("utf-8")]),
        ('cn', [fullname("utf-8")]),
        ('givenname', [surname("utf-8")]),
        ('sn', [name("utf-8")] ),
        ('userPassword', [pwd("utf-8")])
    ])
    ldap_conn = ldap.initialize(LDAP_HOST)
    ldap_conn.simple_bind_s(LDAP_ADMIN_DN, ldapPwd)

    try:
        ldap_conn.add_s(dn, entry)
    finally:
        ldap_conn.unbind_s()
    #raise Exception ("erreur Ldap")
    return pwd
#
# doInscription
#
# Ajout d'un utilisteur dans un LDAP
# @param string listCSV,output
#
#
def doInscription(listCSV):
    nbEnrgs = len(listCSV)
    nbError = 0
    for i in range (nbEnrgs):
        enrg=listCSV[i]
        try :
            #raise Exception ("gros problème")
            pwd = addUser(enrg["Nom"],enrg["Prenom"],enrg["NomUtilisateur"],enrg["NiveauMDP"])
            storePwd(enrg["NomUtilisateur"],pwd)
        except Exception as err:
            log("ERROR", "erreur durant l'inscription de " + enrg["NomUtilisateur"] + " erreur : " + format(err) + "\n")
            nbError = nbError+1
        else :
            log("INFO", "inscription de " + enrg["NomUtilisateur"] + " : OK\n")
    return nbError
#
#
#
#
#
def storePwd(nomUtilisateur,pwd):
    now = datetime.datetime.now()
    line = now.strftime("%Y%m%d %H%M%S") + "inscription de " + nomUtilisateur + " " + pwd + "\n"
    dateYYYYMMDD = now.strftime("%Y%m%d")
    userAbsPath = userDir + userFile + dateYYYYMMDD + userFileExt
    try:
        fd = open(userAbsPath, "a")
        fd.write(line + "\n")
        fd.close()
    except Exception as err:
        print(" erreur : l'utilisateur " + nomUtilisateur + " n'a pas été créé " + "\n")


ldapPwd = input_ldap_pass()
try_ldap_bind(ldapPwd)

dataCsv = read_csv (dataCsvFile)
doInscription(dataCsv)