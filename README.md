# Tsoha Book List

Sovellus, jossa käyttäjät voivat pitää kirjalistaa ja jakaa tietoja kirjoista.

## Toiminnot

- Käyttäjät voivat **luoda tunnuksen ja kirjautua sisään**.
- Jokaisella käyttäjällä on oma näkymänsä, jossa näkyvät **hänen omat lisäämänsä kirjat**.
- Käyttäjät voivat **lisätä, muokata ja poistaa** vain omia kirjalistauksiaan.
- Käyttäjät voivat tarkastella myös **muiden käyttäjien lisäämiä kirjoja**.
- Käyttäjät voivat hakea kirjoja **nimen tai kirjailijan perusteella**.
- Kirjoihin liittyy perustiedot (nimi, kirjailija, genre, vuosi, kieli, kommentti, arvio).

## Kehityksessä

- Käyttäjä voi lisätä muiden kirjoihin **arvostelun (1–5)** tai **kommentin**.
- Kirjat voidaan luokitella **genreittäin** ja niitä voidaan selata kategorioiden kautta.
- Tulevaisuudessa käyttöliittymää selkeytetään ja lisätään tarkempi käyttäjäsivu.

## Sovelluksen asennus

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
