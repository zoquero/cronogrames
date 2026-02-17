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
python3 ./cronogrames.py --titol "Cronograma demostratiu"  \
  --cicles 3 --sortida "/tmp/exemple.png"                         \
  --nom "Tipus Clk"       --tipus "rellotge"                      \
  --nom "Tipus constant " --tipus "complet"  --valors "X01"       \
  --nom "Tipus estable"   --tipus "estable"  --valors "Z1B0"      \
  --nom "Tipus custom_1"  --tipus "custom_1" --valors "0101"      \
        --transicio "0.2;0.3;0.4"                                 \
  --nom "Tipus custom_n"  --tipus "custom_n" --valors "0101X1Z10" \
        --transicio "0.05;0.95;1.05;1.333;1.666;2;2.45;2.55;"
```

## Ajuda

```
$ python3 ./cronogrames.py --help
usage: cronogrames.py [-h] --titol TITOL --cicles CICLES [--sortida SORTIDA] [--nom NOM] [--tipus TIPUS]
                      [--valors VALORS] [--transicio TRANSICIO]

Generador de cronogrames digitals parametritzable.

Tipus de senyal admesos:
  - rellotge   : alternança 1/0 cada meitat de període.
  - complet    : canvis només a frontera de cicle si el valor canvia.
  - estable    : canvis situats 'prop' (al·leatòriament)
                 del final de cada interval, si el valor canvia.
                 Accepta len(valors)=N o N+1.
  - custom_1   : Una transició per interval i→i+1,
                 transicions RELATIVES dins l’interval, en [0,1).
                 Requereix paràmetre --transicio
                 definint els instants de les transicions.
                 Requereix len(valors)=N o N+1.
  - custom_n   : senyal totalment a mida, longitud arbitrària.
                 Les transicions són EN TEMPS ABSOLUT, una per canvi de
                 valor, definides des de t=0. No hi ha periodicitat.

Valors del senyal (caràcter per mostra):
  0 / 1  : nivells digitals.
  X      : indeterminat (hachurat).
  Z      : alta impedància (patró 'Z' repetit).
  B      : buit (no es dibuixa res).

Longitud de valors (custom_1 i estable):
  - Si la longitud és N (= --cicles), l’últim interval resta estable.
  - Si és N+1, el valor extra permet una transició dins de l’últim
    interval, sense allargar el cronograma.

Transicions:
  - custom_1 → transicions relatives dins de cada interval (0 ≤ τ < 1).
  - custom_n → transicions absolutes des de t=0 (N-1 transicions per N valors).

Durada i eix temporal:
  - L’eix X va de 0 a N, sent N els cicles indicats.
  - Els senyals es retallen sempre a t = N.
  - Període fix d’1.0 unitat.

Requisits:
  - Cal que hi hagi almenys un senyal de tipus 'rellotge'.
  - Cada bloc de --nom ha de portar el seu --tipus.

options:
  -h, --help            show this help message and exit
  --titol TITOL         Títol del cronograma.
  --cicles CICLES       Nombre de cicles (N).
  --sortida SORTIDA     Fitxer de sortida (PNG, SVG, etc.).
  --nom NOM             Nom de la senyal (es pot repetir).
  --tipus TIPUS         Tipus: rellotge, complet, custom_1, custom_n, estable.
  --valors VALORS       Cadena de valors (0,1,X,Z,B).
  --transicio TRANSICIO
                        Transicions separades per ';'. RELATIUS per custom_1, ABSOLUTS per custom_n.

Exemples:

  # Ex. amb custom_1 (relatiu)
  programa.py --titol "Demo" --cicles 5 \
    --nom "Clk" --tipus rellotge \
    --nom "D0" --tipus custom_1 --valors 010100 \
    --transicio "0.4;0.6;0.3;0.7;0.25" \
    --sortida out1.png

  # Ex. amb custom_n (absolut, no cíclic)
  programa.py --titol "Senyal a mida" --cicles 3 \
    --nom "Clk" --tipus rellotge \
    --nom "S" --tipus custom_n --valors "0101010" \
    --transicio "0.2;0.7;1.2;1.7;2.2;2.7" \
    --sortida out2.png

  # Ex. complet i estable
  programa.py --titol "EP/SP" --cicles 5 \
    --nom "Clk" --tipus rellotge \
    --nom "D2" --tipus estable --valors 0X1Z0 \
    --nom "D1" --tipus complet --valors 1B110 \
    --sortida out3.png
```

### Aclariment sobre la longitud de valors

Per als tipus `estable`, `custom_1` i `custom_n` la longitud de la cadena de valors pot ser:

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
