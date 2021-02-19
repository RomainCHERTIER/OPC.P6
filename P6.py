import getpass
import csv
import random
import datetime
import ldap


################################   Constants   ################################

dataCsvFile = "csvp6.csv"

LDAP_HOST = "ldap://localhost"
LDAP_BASE_DN = "cn=Users,dc=P6,dc=local"
LDAP_ADMIN_DN = "cn=Administrateur,cn=Users,dc=P6,dc=local"

logDir = ""
logFile = "logP6_"
logFileExt = ".log"

userDir = ""
userFile = "UserP6_"
userFileExt = ".txt"


################################   Functions   ################################

#
# log
#
# creation of a log file
# @param string level,msg
#
#
def log(level, msg):
    now = datetime.datetime.now()
    line = now.strftime("%Y%m%d %H%M%S") + " [" + level + "] " + msg
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
# Implementation of the log file with the different alerts
# @param string level,msg
#
#
def logExit(level, msg):
    log(level, msg)
    if (level == "ERROR"):
        exit(2)
    elif (level == "WARNING"):
        exit(1)
    else:
        exit(0)


#
#
# input_ldap_pass
# LDAP administrator password request
#
#
def input_ldap_pass():
    try:
        return getpass.getpass("Enter LDAP manager password:")
    except getpass.GetPassWarning:
        logExit("ERROR", "erreur de saisie de mot de passe")
        return ""


#
#
# try_ldap_bind
#
# Connection to LDAP server
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
# Reading csv file
# @param string file_csv csv file path
# @return arrey list of csv records
#
#
def read_csv(file_csv):
    data = []
    objs = []
    reader = csv.reader(open(file_csv, "r"), delimiter=";")
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
# Automatic password generation in relation to password level
# @param string pwdLevel Value Name NiveauMDP
# @return arrey Password
#
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


#
# addUser
#
# Adding a user to an LDAP
# @param string surname,name,login,pwdLevel Table value
# @return arrey pwd
#
#
def addUser(surname, name, login, pwdLevel):
    pwd = createPwd(pwdLevel)
    print(name + " " + surname + " " + pwd)
    fullname = surname + " " + name
    dn = "cn=" + fullname + "," + LDAP_BASE_DN
    entry = [
        ("objectClass", ["person".encode("utf-8"),
                         "organizationalPerson".encode("utf-8"),
                         "user".encode("utf-8"),
                         "posixAccount".encode("utf-8"),
                         "top".encode("utf-8"),
                         ]),
        ("uid", login.encode("utf-8")),
        ("cn", fullname.encode("utf-8")),
        ("givenname", surname.encode("utf-8")),
        ("sn", name.encode("utf-8")),
        ("userPassword", pwd.encode("utf-8"))
    ]
    try:
        ldap_conn = ldap.initialize(LDAP_HOST)
        ldap_conn.simple_bind_s(LDAP_ADMIN_DN, ldapPwd)
        ldap_conn.add_s(dn, entry)
    except Exception as err:
        log("ERROR", "adUser:" + login + " erreur : " + format(err) + "\n")
    finally:
        ldap_conn.unbind_s()
    return pwd


#
# doInscription
#
# Adding a user to an LDAP
# @param string listCSV,output
#
#
def doInscription(listCSV):
    nbEnrgs = len(listCSV)
    nbError = 0
    for i in range(nbEnrgs):
        enrg = listCSV[i]
        try:
            pwd = addUser(enrg["Nom"], enrg["Prenom"], enrg["NomUtilisateur"], enrg["NiveauMDP"])
            storePwd(enrg["NomUtilisateur"], pwd)
        except Exception as err:
            log("ERROR", "erreur durant l'inscription de " + enrg["NomUtilisateur"] + " erreur : " + format(err) + "\n")
            nbError = nbError + 1
        else:
            log("INFO", "inscription de " + enrg["NomUtilisateur"] + " : OK\n")
    return nbError


#
# storePwd
#
# Creation of a log file to store the password
# @param string nomUtilisateur,pwd
#
#
def storePwd(nomUtilisateur, pwd):
    now = datetime.datetime.now()
    line = now.strftime("%Y%m%d %H%M%S") + "inscription de " + nomUtilisateur + " " + pwd + "\n"
    dateYYYYMMDD = now.strftime("%Y%m%d")
    userAbsPath = userDir + userFile + dateYYYYMMDD + userFileExt
    try:
        fd = open(userAbsPath, "a")
        fd.write(line + "\n")
        fd.close()
    except Exception as err:
        print(" ERROR : l'utilisateur " + nomUtilisateur + " n'a pas été créé " + "\n")


##################################   Main   ###################################

ldapPwd = input_ldap_pass()
try_ldap_bind(ldapPwd)

dataCsv = read_csv(dataCsvFile)
doInscription(dataCsv)
