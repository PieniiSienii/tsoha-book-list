# tsoha-book-list

## Tehty
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisälle sovellukseen ✅
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan lukemiaan kirjoja ✅
- Käyttäjä näkee omat ja muiden lisäämät kirjat ✅
- Käyttäjä pystyy hakemaan kirjoja nimellä/ kirjailijalla✅

## Toteutettavana
- Käyttäjä pystyy lisäämään muiden lukemiin kirjoihin arvostelun (1-5) tai kommentin 


##Sovelluksen asennus

Asenna flask-kirjasto:
```bash
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:
```bash
$ sqlite3 database.db < schema.sql
```
Voit käynnistää sovelluksen näin:
```bash
$ flask run
```
