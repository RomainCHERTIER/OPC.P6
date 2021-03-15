###############################################################################
#MIT License

#Copyright (c) 2021 Romain CHERTIER
#opensource.org/licenses/mit-license.php

###############################################################################
#
#                    Script for creating user accounts
#
# This script adds users to an LDAP from the information contained in a csv file.
#
#
# @author Romain CHERTIER<romain.chertier@sfr.fr>
# @version 1.1
# @date 2021-03-01
#

import getpass
import csv
import random
import datetime
import ldap
from ldap3 import *


################################   Constants   ################################

dataCsvFile = "csvp6.csv"

LDAP_HOST = "ldap://localhost"
LDAP_BASE_DN = "cn=Users,dc=P6,dc=local"
LDAP_ADMIN_DN = "cn=Administrateur,cn=Users,dc=P6,dc=local"

domain = 'P6.local'
logAdmin = 'Administrateur'

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
def addUser(surname, name, login, pwdLevel, domain):
    pwd = createPwd(pwdLevel)
    print(name + " " + surname + " " + pwd)
    fullname = surname + " " + name
    dn = "cn=" + fullname + "," + LDAP_BASE_DN
    upn = login + "@" + domain
    try:
        # connect - specifying port 636 is only for reference as it's inferred
        s = Server('ldaps://localhost:636', connect_timeout=5)
        c = Connection(s, user='{}\{}'.format(domain, logAdmin), password=ldapPwd, authentication="NTLM")

        if not c.bind():
            exit(c.result)
        else :
            # create user
            c.add(dn, attributes={
                'objectClass': ['organizationalPerson', 'person', 'top', 'user'],
                'sAMAccountName': login,
                'userPrincipalName': "{}@{}".format(login, domain),
                'displayName': login
            })
            # set password - must be done before enabling user
            # you must connect with SSL to set the password
            c.extend.microsoft.modify_password(dn, pwd)

            # enable user (after password set)
            c.modify(dn, {'userAccountControl': [('MODIFY_REPLACE', 512)]})
            return pwd

    except Exception as err:
        log("ERROR", "adUser:" + login + " erreur : " + format(err))
        return None


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
            pwd = addUser(enrg["Nom"], enrg["Prenom"], enrg["NomUtilisateur"], enrg["NiveauMDP"], enrg["Domaine"])
            if pwd is None:
               raise Exception("Erreur lors de l'inscription")
            storePwd(enrg["NomUtilisateur"], pwd)
        except Exception as err:
            log("ERROR", "erreur durant l'inscription de " + enrg["NomUtilisateur"] + " erreur : " + format(err))
            nbError = nbError + 1
        else:
            log("INFO", "inscription de " + enrg["NomUtilisateur"] + " : OK")
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
    line = now.strftime("%Y%m%d %H%M%S") + " inscription de " + nomUtilisateur + " " + pwd + "\n"
    dateYYYYMMDD = now.strftime("%Y%m%d")
    userAbsPath = userDir + userFile + dateYYYYMMDD + userFileExt
    try:
        fd = open(userAbsPath, "a")
        fd.write(line + "\n")
        fd.close()
    except Exception as err:
        log("ERROR", "l'utilisateur" + nomUtilisateur + "n'a pas été créé")


##################################   Main   ###################################

ldapPwd = input_ldap_pass()
try_ldap_bind(ldapPwd)

dataCsv = read_csv(dataCsvFile)
doInscription(dataCsv)
