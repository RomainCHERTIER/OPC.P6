# OPC.P6
Ce projet a été conçu pour automatiser l'ajout de compte utilisateur dans un LDAP.
Le script ajoutera les utilisateurs présent dans un fichier CSV.
Le mot de passe de chaque utilisateur sera généré par ce même script selon le niveau de difficulté indique dans ce même fichier CSV.

## Pour commencer

Préparé votre fichier CSV comme celui présent dans le dossier.
Vérifier que les informations présentent dans le script correspondes à votre serveur Ldap(admin Ldap, adresse du serveur ...)

### Pré-requis

- Serveur LDAP avec accès SSL

## Démarrage

Afin d'utiliser le script, il vous faudra modifier les constantes avec les valeurs correspondantes avec votre infrastructure.
Vous aurez besoin de créer un fichier CSV. (Cf [csvp6.csv](csvp6.csv))


## Fabriqué avec

* Pycharm - environnement de développement

## Versions

**Dernière version stable :** 1

## Auteurs

* **Romain CHERTIER** _alias_ [@RomainCHERTIER](https://github.com/RomainCHERTIER)

## License

Ce projet est sous licence ``MIT`` - voir le fichier [LICENSE.md](LICENSE.md) pour plus d'informations

