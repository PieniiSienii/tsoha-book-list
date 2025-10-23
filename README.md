# Tsoha Book List

Sovellus, jossa käyttäjät voivat pitää kirjalistaa ja jakaa tietoja kirjoista.

## Arvioijalle tiedoksi:
Tein puolivälissä projektia dev branchin, jossa kokeilin tiettyjä toiminnallisuuksia ja jotka oli tarkoitettu vain testausta varten. Mergesin branchin mainiin, joten commit viestit ovat sen takia epäselviä ja vajaita (tein niitä dev branchissa vaan huviksi, en hyödyksi). En tajunnut, että ne näkyvät lopullisessa työssä.

## Toteutettu

- Käyttäjät voivat **luoda tunnuksen ja kirjautua sisään**.
- Jokaisella käyttäjällä on oma näkymänsä, jossa näkyvät **hänen omat lisäämänsä kirjat**.
- Käyttäjät voivat **lisätä, muokata ja poistaa** vain omia kirjalistauksiaan.
- Käyttäjät voivat tarkastella myös **muiden käyttäjien lisäämiä kirjoja**.
- Käyttäjät voivat hakea kirjoja **nimen tai kirjailijan perusteella**.
- Kirjoihin liittyy perustiedot (nimi, kirjailija, genre, vuosi, kieli, kommentti, arvio).
- Käyttäjä voi lisätä muiden kirjoihin **arvostelun (1–5)** tai **kommentin**.
- Kirjat voidaan luokitella **genreittäin** tai **arvostelun** perusteella, ja niitä voidaan selata kategorioiden kautta.
- Käyttäjillä on omat käyttäjäsivut, joissa on tilastoja
- Käyttöliittymää on selkeytetty ja siihen on lisätty tyyliasetuksia

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
