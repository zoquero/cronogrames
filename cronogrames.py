#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Creador de cronogrames
#
# Angel Galindo Muñoz + Copilot
# 20260216 (modificat: custom → custom_1, afegit custom_n)
#

import argparse
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# UTILITATS
# ---------------------------------------------------------------------

def parse_valors(bits: str):
    bits = bits.strip()
    if any(c not in "01XxZzBb" for c in bits):
        raise ValueError(f"Valors invàlids: {bits}")
    return [c.upper() for c in bits]


def parse_transicions(txt: str):
    return [float(p.strip()) for p in txt.split(";") if p.strip() != ""]


def events_to_steps(initial, events, t_end):
    ordered = sorted(events, key=lambda e: e[0])

    x = [0.0]
    y = [initial]
    cur = initial

    for t, val in ordered:
        if t < 0 or t > t_end:
            continue
        x.append(t)
        y.append(cur)
        cur = val
        x.append(t)
        y.append(cur)

    if x[-1] < t_end:
        x.append(t_end)
        y.append(cur)

    return x, y


# ---------------------------------------------------------------------
# GENERACIÓ DE SENYALS
# ---------------------------------------------------------------------

def senyal_rellotge(ncicles, periode=1.0):
    events = []
    cur = 1
    t = 0.5 * periode

    for _ in range(2 * ncicles):
        cur = 1 - cur
        events.append((t, cur))
        t += 0.5 * periode

    return events_to_steps(1, events, ncicles * periode)


def senyal_complet(valors, ncicles, periode=1.0):
    maxc = min(ncicles, len(valors))
    events = []
    for i in range(1, maxc):
        if valors[i] != valors[i - 1]:
            events.append((i * periode, valors[i]))
    return events_to_steps(valors[0], events, maxc * periode)


def _valida_llargada_valors(ncicles: int, valors: list, tipus: str):
    n = len(valors)
    if n not in (ncicles, ncicles + 1):
        raise ValueError(
            f"[{tipus}] Longitud de valors incompatible: "
            f"len(valors)={n}, cal que sigui {ncicles} o {ncicles + 1}."
        )


def senyal_custom_1(valors, transicions, ncicles, periode=1.0):
    """
    Antic 'custom'.
    """
    _valida_llargada_valors(ncicles, valors, "custom_1")

    n_val = len(valors)
    intervals = min(ncicles, n_val - 1)
    esperades = n_val - 1

    if len(transicions) != esperades:
        raise ValueError(
            f"[custom_1] Nombre de transicions incorrecte. Rebudes {len(transicions)}, esperades {esperades}."
        )

    for i in range(intervals):
        tau = transicions[i]
        if not (0.0 <= tau < 1.0):
            raise ValueError(
                f"[custom_1] Transició {i} fora de rang: {tau}. Cal 0 ≤ τ < 1."
            )

    t_end = ncicles * periode
    events = []

    for i in range(intervals):
        t0 = i * periode
        tau = transicions[i]
        t = min(t0 + tau * periode, t_end)
        events.append((t, valors[i + 1]))

    return events_to_steps(valors[0], events, t_end)


def senyal_custom_n(valors, transicions, ncicles, periode=1.0):
    """
    CUSTOM_N:
    - valors = qualsevol longitud >= 1
    - transicions = N-1, temps absoluts
    - t_end = ncicles * periode
    """
    n_val = len(valors)
    esperades = n_val - 1

    if len(transicions) != esperades:
        raise ValueError(
            f"[custom_n] Nombre de transicions incorrecte. Rebudes {len(transicions)}, esperades {esperades}."
        )

    t_end = ncicles * periode
    events = []

    for i in range(esperades):
        t = float(transicions[i])
        t = max(0, min(t, t_end))
        events.append((t, valors[i + 1]))

    return events_to_steps(valors[0], events, t_end)


def senyal_estable(valors, ncicles, periode=1.0, rng=None):
    if rng is None:
        rng = np.random.default_rng()

    _valida_llargada_valors(ncicles, valors, "estable")

    n_val = len(valors)
    intervals = min(ncicles, n_val - 1)
    t_end = ncicles * periode
    events = []

    for i in range(intervals):
        if valors[i] != valors[i + 1]:
            t1 = (i + 1) * periode
            delta = rng.uniform(0.2, 0.5) * periode
            t = max(i * periode, t1 - delta)
            t = min(t, t1)
            t = min(t, t_end)
            events.append((t, valors[i + 1]))

    return events_to_steps(valors[0], events, t_end)


# ---------------------------------------------------------------------
# AJUDA / VALORS ESPECIALS
# ---------------------------------------------------------------------

def _is_X(v): return isinstance(v, str) and v == "X"
def _is_Z(v): return isinstance(v, str) and v == "Z"
def _is_B(v): return isinstance(v, str) and v == "B"

def _is_num(v):
    if isinstance(v, int):
        return v in (0, 1)
    if isinstance(v, str):
        return v in ("0", "1")
    return False

def _to_num(v):
    return int(v) if isinstance(v, str) else v


# ---------------------------------------------------------------------
# GRÀFIC
# ---------------------------------------------------------------------

def dibuixa(waves, titol, ncicles, periode=1.0, output=None, tipus_originals=None):
    fig, axes = plt.subplots(len(waves), 1, sharex=True, figsize=(11, 6))

    if len(waves) == 1:
        axes = [axes]

    fig.suptitle(titol, fontsize=14)

    for ax, (nom, x, y) in zip(axes, waves):
        n = len(y)

        for i in range(n - 1):
            t0, t1 = x[i], x[i + 1]
            v = y[i]

            if _is_B(v):
                continue

            if _is_X(v):
                ax.fill_between(
                    [t0, t1],
                    1.2, -0.2,
                    facecolor="none",
                    hatch="///",
                    edgecolor="gray",
                    linewidth=0.0,
                    alpha=0.4
                )
                continue

            if _is_Z(v):
                base_fs = plt.rcParams.get("font.size", 10.0)
                fs = base_fs * 1.8
                pattern = " Z"
                repeated = pattern * 200

                clip_rect = plt.Rectangle(
                    (t0, -0.2),
                    t1 - t0,
                    1.4,
                    transform=ax.transData
                )
                ax.add_patch(clip_rect)
                clip_rect.set_visible(False)

                txt = ax.text(
                    (t0 + t1) / 2,
                    0.5,
                    repeated,
                    ha="center",
                    va="center",
                    color="gray",
                    fontsize=fs,
                    alpha=0.95,
                    clip_on=True
                )
                txt.set_clip_path(clip_rect)
                continue

            if _is_num(v):
                val = _to_num(v)
                ax.plot(
                    [t0, t1],
                    [val, val],
                    drawstyle="steps-post",
                    linewidth=2,
                    color='C0'
                )
                continue

        for i in range(1, n):
            v_prev, v_cur = y[i - 1], y[i]
            if _is_num(v_prev) and _is_num(v_cur) and (_to_num(v_prev) != _to_num(v_cur)):
                t = x[i]
                y0, y1 = sorted([_to_num(v_prev), _to_num(v_cur)])
                ax.vlines(t, y0, y1, colors='C0', linewidth=2)

        ax.set_ylabel(nom, rotation=0, labelpad=30, va='center')
        ax.set_yticks([0, 1])
        ax.set_ylim(-0.4, 1.4)
        ax.grid(True, axis="y", linestyle=":", alpha=0.5)

    axes[-1].set_xlabel("Temps (cicles)")
    ticks = np.arange(0, ncicles + 1, 1)
    axes[-1].set_xticks(ticks)
    axes[-1].set_xticklabels([str(t) for t in ticks])

    for ax in axes:
        ax.set_xlim(0, ncicles)

    rellotge_x = None
    rellotge_y = None

    for i, tipus in enumerate(tipus_originals):
        if tipus.lower() == "rellotge":
            rellotge_x, rellotge_y = waves[i][1], waves[i][2]
            break

    if rellotge_x is not None:
        flancs = []
        for i in range(1, len(rellotge_y)):
            if _is_num(rellotge_y[i - 1]) and _is_num(rellotge_y[i]) \
               and _to_num(rellotge_y[i - 1]) == 0 and _to_num(rellotge_y[i]) == 1:
                flancs.append(rellotge_x[i])

        for t in flancs:
            for ax in axes:
                ax.axvline(t, color="gray", linestyle="--", linewidth=0.5, alpha=0.4)

    plt.tight_layout(rect=(0, 0, 1, 0.95))

    if output:
        plt.savefig(output, dpi=300)
        print(f"[OK] Imatge guardada a: {output}")
    else:
        plt.show()


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generador de cronogrames digitals parametritzable.\n\n"
            "Tipus de senyal admesos:\n"
            "  - rellotge   : alternança 1/0 cada meitat de període.\n"
            "  - complet    : canvis només a frontera de cicle si el valor canvia.\n"
            "  - estable    : canvis situats 'prop' (al·leatòriament)\n"
            "                 del final de cada interval, si el valor canvia.\n"
            "                 Accepta len(valors)=N o N+1.\n"
            "  - custom_1   : Una transició per interval i→i+1,\n"
            "                 transicions RELATIVES dins l’interval, en [0,1).\n"
            "                 Requereix paràmetre --transicio\n"
            "                 definint els instants de les transicions.\n"
            "                 Requereix len(valors)=N o N+1.\n"
            "  - custom_n   : senyal totalment a mida, longitud arbitrària.\n"
            "                 Les transicions són EN TEMPS ABSOLUT, una per canvi de\n"
            "                 valor, definides des de t=0. No hi ha periodicitat.\n\n"
            "Valors del senyal (caràcter per mostra):\n"
            "  0 / 1  : nivells digitals.\n"
            "  X      : indeterminat (hachurat).\n"
            "  Z      : alta impedància (patró 'Z' repetit).\n"
            "  B      : buit (no es dibuixa res).\n\n"
            "Longitud de valors (custom_1 i estable):\n"
            "  - Si la longitud és N (= --cicles), l’últim interval resta estable.\n"
            "  - Si és N+1, el valor extra permet una transició dins de l’últim\n"
            "    interval, sense allargar el cronograma.\n\n"
            "Transicions:\n"
            "  - custom_1 → transicions relatives dins de cada interval (0 ≤ τ < 1).\n"
            "  - custom_n → transicions absolutes des de t=0 (N-1 transicions per N valors).\n\n"
            "Durada i eix temporal:\n"
            "  - L’eix X va de 0 a N, sent N els cicles indicats.\n"
            "  - Els senyals es retallen sempre a t = N.\n"
            "  - Període fix d’1.0 unitat.\n\n"
            "Requisits:\n"
            "  - Cal que hi hagi almenys un senyal de tipus 'rellotge'.\n"
            "  - Cada bloc de --nom ha de portar el seu --tipus.\n"
        ),
        epilog=(
            "Exemples:\n\n"
            "  # Ex. amb custom_1 (relatiu)\n"
            "  programa.py --titol \"Demo\" --cicles 5 \\\n"
            "    --nom \"Clk\" --tipus rellotge \\\n"
            "    --nom \"D0\" --tipus custom_1 --valors 010100 \\\n"
            "    --transicio \"0.4;0.6;0.3;0.7;0.25\" \\\n"
            "    --sortida out1.png\n\n"
            "  # Ex. amb custom_n (absolut, no cíclic)\n"
            "  programa.py --titol \"Senyal a mida\" --cicles 3 \\\n"
            "    --nom \"Clk\" --tipus rellotge \\\n"
            "    --nom \"S\" --tipus custom_n --valors \"0101010\" \\\n"
            "    --transicio \"0.2;0.7;1.2;1.7;2.2;2.7\" \\\n"
            "    --sortida out2.png\n\n"
            "  # Ex. complet i estable\n"
            "  programa.py --titol \"EP/SP\" --cicles 5 \\\n"
            "    --nom \"Clk\" --tipus rellotge \\\n"
            "    --nom \"D2\" --tipus estable --valors 0X1Z0 \\\n"
            "    --nom \"D1\" --tipus complet --valors 1B110 \\\n"
            "    --sortida out3.png\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--titol", required=True, help="Títol del cronograma.")
    parser.add_argument("--cicles", type=int, required=True, help="Nombre de cicles (N).")
    parser.add_argument("--sortida", help="Fitxer de sortida (PNG, SVG, etc.).")

    parser.add_argument("--nom", action="append", help="Nom de la senyal (es pot repetir).")
    parser.add_argument("--tipus", action="append", help="Tipus: rellotge, complet, custom_1, custom_n, estable.")
    parser.add_argument("--valors", action="append", help="Cadena de valors (0,1,X,Z,B).")
    parser.add_argument(
        "--transicio",
        action="append",
        help="Transicions separades per ';'. RELATIUS per custom_1, ABSOLUTS per custom_n."
    )

    args = parser.parse_args()

    if not args.nom or not args.tipus:
        parser.error("Cal indicar almenys un bloc --nom --tipus ...")

    if "rellotge" not in [t.lower() for t in args.tipus]:
        parser.error("Cal definir almenys un senyal de tipus 'rellotge'.")

    tipus_originals = args.tipus.copy()

    nsenyals = len(args.nom)
    if len(args.tipus) != nsenyals:
        parser.error("Cada --nom ha de tenir un --tipus corresponent")

    waves = []
    periode = 1.0
    rng = np.random.default_rng()

    idx_valors = 0
    idx_trans = 0

    for i in range(nsenyals):
        nom = args.nom[i]
        tipus = args.tipus[i].lower()

        if tipus == "rellotge":
            x, y = senyal_rellotge(args.cicles, periode)

        elif tipus == "complet":
            if idx_valors >= len(args.valors):
                parser.error(f"[{nom}] Falta --valors per al tipus 'complet'.")
            val = parse_valors(args.valors[idx_valors])
            idx_valors += 1
            x, y = senyal_complet(val, args.cicles, periode)

        elif tipus == "custom_1":
            if idx_valors >= len(args.valors):
                parser.error(f"[{nom}] Falta --valors per al tipus 'custom_1'.")
            if idx_trans >= len(args.transicio):
                parser.error(f"[{nom}] Falta --transicio per al tipus 'custom_1'.")
            val = parse_valors(args.valors[idx_valors])
            trans = parse_transicions(args.transicio[idx_trans])
            idx_valors += 1
            idx_trans += 1
            x, y = senyal_custom_1(val, trans, args.cicles, periode)

        elif tipus == "custom_n":
            if idx_valors >= len(args.valors):
                parser.error(f"[{nom}] Falta --valors per al tipus 'custom_n'.")
            if idx_trans >= len(args.transicio):
                parser.error(f"[{nom}] Falta --transicio per al tipus 'custom_n'.")
            val = parse_valors(args.valors[idx_valors])
            trans = parse_transicions(args.transicio[idx_trans])
            idx_valors += 1
            idx_trans += 1
            x, y = senyal_custom_n(val, trans, args.cicles, periode)

        elif tipus == "estable":
            if idx_valors >= len(args.valors):
                parser.error(f"[{nom}] Falta --valors per al tipus 'estable'.")
            val = parse_valors(args.valors[idx_valors])
            idx_valors += 1
            x, y = senyal_estable(val, args.cicles, periode, rng)

        else:
            raise ValueError(f"Tipus desconegut: {tipus}")

        waves.append((nom, x, y))

    dibuixa(
        waves,
        args.titol,
        args.cicles,
        periode,
        output=args.sortida,
        tipus_originals=tipus_originals
    )


if __name__ == "__main__":
    main()
