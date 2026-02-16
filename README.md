# Creador de Cronogrames Digitals

Generador de cronogrames digitals parametritzable útil per a il·lustrar exàmens, apunts o documentació tècnica de **Sistemes Digitals**.

El programa genera una imatge amb línies digitals (0/1), indeterminacions (X), alta impedància (Z), intervals sense valor (B), i un rellotge mestre que defineix el ritme i les línies de referència verticals.

Permet crear cronogrames complexos de forma ràpida i automàtica a partir de paràmetres donats per línia de comandes.

![Exemple de cronograma](./exemple.png)

## Autor

**Angel Galindo Muñoz + Copilot**  
Febrer 2026

## Característiques principals

- ✔ Generació d’un o més senyals digitals al llarg d’un nombre arbitrari de cicles  
- ✔ Un **rellotge mestre** obligatori que marca els flancs de pujada  
- ✔ Suport per quatre tipus de senyal:
  - **rellotge** → 50% de duty (primera meitat alt, segona baix)
  - **estable** → transicions al·leatòriament entre 0.2 i 0.5 cicles abans del flanc de pujada
  - **complet** → canvis exactes a cada inici de cicle
  - **custom** → transicions definides manualment (per exemple "0.25;0.5;0.75" per transicions a un quart, mig i tres quarts de cicle)
- ✔ Suport per valors especials:
  - **0 / 1** → valors digitals estàndard
  - **X** → indeterminació (patró diagonal)
  - **Z** → alta impedància (patró textual repetit “Z Z Z Z …”)
  - **B** → sense valor (no es pinta res)
- ✔ Representació visual clara i coherent
- ✔ Línies verticals puntejades en tots els senyals a cada **flanc de pujada** del rellotge mestre
- ✔ El cronograma abasta **exactament t = 0 fins t = cicles**
- ✔ Exportació opcional a PNG

## Exemple d'ús

Aquesta comanda ha generat la imatge d'exemple:
```
python3 ./cronogrames.py --titol "Cronograma purament demostratiu" \
        --cicles 5   --nom "Clk" --tipus rellotge \
        --nom "D[2]" --tipus estable --valors "0010Z" \
        --nom "D[1]" --tipus estable --valors "1101Z" \
        --nom "D[0]" --tipus estable --valors "10101" \
        --nom "E"    --tipus estable --valors "XX101" \
        --nom "Q[2]" --tipus estable --valors "BBBBB" \
        --nom "Q[1]" --tipus estable --valors "BBBBB" \
        --nom "Q[0]" --tipus estable --valors "BBBBB" \
        --sortida exemple.png
```

## Ajuda

```
usage: cronogrames.py [-h] --titol TITOL --cicles CICLES [--sortida SORTIDA] [--nom NOM] [--tipus TIPUS]
                      [--valors VALORS] [--transicio TRANSICIO]

Generador de cronogrames digitals parametritzable.

Notes sobre longitud de valors per a 'custom' i 'estable':
  - La longitud de la cadena de valors pot ser igual a N (= --cicles)
    o igual a N+1.
  - Si és N: l’últim interval es manté estable (sense transicions internes).
  - Si és N+1: el valor extra permet una transició dins de l’últim interval
    (entre N-1 i N), igual que a la resta d’intervals. El cronograma no
    s’allarga i acaba a t = N.
  - Per al tipus 'custom', el nombre de transicions ha de ser len(valors)-1.
    Cada transició és un nombre en [0,1), separat per ';', i representa el
    moment relatiu dins de cada interval i→i+1.

options:
  -h, --help            show this help message and exit
  --titol TITOL         Títol del cronograma
  --cicles CICLES       Nombre de cicles (N)
  --sortida SORTIDA     Ruta per guardar la imatge generada
  --nom NOM             Nom de la senyal
  --tipus TIPUS         Tipus: rellotge, complet, custom, estable
  --valors VALORS       Cadena de bits per la senyal (0,1,X,Z,B)
  --transicio TRANSICIO
                        Transicions separades per ';' per tipus custom (valors en [0,1))

Exemple d'ús:
  programa.py --titol "Cronograma EP/SP" --cicles 5 \
    --nom "Clk" --tipus rellotge \
    --nom "D[2]" --tipus estable --valors 0X1Z0 \
    --nom "D[1]" --tipus estable --valors 1B110 \
    --nom "D[0]" --tipus custom  --valors 010100 --transicio 0.4;0.6;0.3;0.7;0.25 \
    --sortida sortida.png

En l'exemple, D[0] té 6 valors amb --cicles 5: la darrera transició ocorre
dins de l'últim interval (entre 4 i 5) sense allargar el cronograma.
```

### Longitud de valors (custom i estable)

Per als tipus `custom` i `estable`, la longitud de la cadena de valors pot ser:

- Igual al nombre de cicles (`--cicles N`)
- Igual a `N + 1`

**Cas 1: N valors**
El senyal es manté estable a l’últim interval.

**Cas 2: N + 1 valors**
El valor extra permet una transició dins de l’últim interval
(del temps N−1 al temps N), sense allargar la durada total del waveform.

## Creació d'entorn virtual amb biblioteques

```
python3 -m venv venv
source venv/bin/activate
pip install matplotlib numpy
```
