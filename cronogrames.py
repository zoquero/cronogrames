#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Creador de cronogrames
#
# Angel Galindo Muñoz + Copilot
# 20260216
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
    # Normalitzem a majúscules: "0","1","X","Z","B"
    return [c.upper() for c in bits]


def parse_transicions(txt: str):
    # Retorna llista de floats a partir d'una cadena "a;b;c"
    return [float(p.strip()) for p in txt.split(";") if p.strip() != ""]


def events_to_steps(initial, events, t_end):
    """
    Construeix vectors per dibuix "steps-post".
    - initial: valor inicial
    - events: llista de tuples (t, nou_valor)
    - t_end: temps final de la seqüència (no es dibuixa més enllà)
    """
    # Ordenem esdeveniments per temps
    ordered = sorted(events, key=lambda e: e[0])

    # Construcció dels vectors x/y
    x = [0.0]
    y = [initial]
    cur = initial

    for t, val in ordered:
        if t < 0 or t > t_end:
            # Ignorem esdeveniments fora de la finestra
            continue
        # mantenim el valor vigent fins a "t"
        x.append(t)
        y.append(cur)
        # canviem a "val" a l'instant "t"
        cur = val
        x.append(t)
        y.append(cur)

    # Tanquem fins a t_end si cal
    if x[-1] < t_end:
        x.append(t_end)
        y.append(cur)

    return x, y


# ---------------------------------------------------------------------
# GENERACIÓ DE SENYALS
# ---------------------------------------------------------------------

def senyal_rellotge(ncicles, periode=1.0):
    """
    Clock correcte:
    - Primera meitat ALT
    - Segona meitat BAIX
    """
    events = []
    cur = 1   # Comença ALT
    t = 0.5 * periode

    for _ in range(2 * ncicles):
        cur = 1 - cur
        events.append((t, cur))
        t += 0.5 * periode

    return events_to_steps(1, events, ncicles * periode)


def senyal_complet(valors, ncicles, periode=1.0):
    """
    Comportament actual (sense canvis):
    - Intervals a frontera de cicle (canvi a i*periode si el valor a i difereix del valor a i-1)
    - No s'implanta cap transició interna especial a l’últim interval.
    """
    maxc = min(ncicles, len(valors))
    events = []
    for i in range(1, maxc):
        if valors[i] != valors[i - 1]:
            events.append((i * periode, valors[i]))
    return events_to_steps(valors[0], events, maxc * periode)


def _valida_llargada_valors(ncicles: int, valors: list, tipus: str):
    """
    Per als tipus 'custom' i 'estable', acceptem len(valors) == ncicles o == ncicles+1.
    Si no, llencem error clar.
    """
    n = len(valors)
    if n not in (ncicles, ncicles + 1):
        raise ValueError(
            f"[{tipus}] Longitud de valors incompatible: "
            f"len(valors)={n}, cal que sigui {ncicles} o {ncicles + 1}."
        )


def senyal_custom(valors, transicions, ncicles, periode=1.0):
    """
    CUSTOM:
    - Accepta len(valors) == ncicles  o  ncicles+1.
    - El nombre de transicions requerides és len(valors) - 1:
        * si len(valors) == ncicles     → transicions = ncicles-1
        * si len(valors) == ncicles + 1 → transicions = ncicles
    - Cada transició és relativa dins l'interval i→i+1 i ha d'estar dins [0,1).
    - El waveform s'acaba a t_end = ncicles * periode (no s'allarga).
    """
    _valida_llargada_valors(ncicles, valors, "custom")

    n_val = len(valors)
    # intervals reals en base a valors: len(valors) - 1
    intervals = min(ncicles, n_val - 1)  # mai més intervals que ncicles
    esperades = n_val - 1

    if len(transicions) != esperades:
        raise ValueError(
            f"[custom] Nombre de transicions incorrecte. "
            f"Rebudes: {len(transicions)}; Esperades: {esperades} "
            f"(sempre len(valors)-1)."
        )

    # Validació de rang [0,1) per a totes les transicions utilitzades
    for i in range(intervals):
        tau = transicions[i]
        if not (0.0 <= tau < 1.0):
            raise ValueError(
                f"[custom] Transició {i} fora de rang: {tau}. "
                f"Cal 0 ≤ τ < 1 dins l'interval {i}→{i+1}."
            )

    t_end = ncicles * periode
    events = []

    for i in range(intervals):
        t0 = i * periode
        tau = transicions[i]
        t = t0 + tau * periode
        # Clamp perquè no superi el final de l'interval ni el final global
        t = min(t, (i + 1) * periode)
        t = min(t, t_end)
        # Afegim el nou valor (post-transició) del punt i+1
        events.append((t, valors[i + 1]))

    return events_to_steps(valors[0], events, t_end)


def senyal_estable(valors, ncicles, periode=1.0, rng=None):
    """
    ESTABLE:
    - Accepta len(valors) == ncicles  o  ncicles+1.
    - Genera canvis 'estables' (lleugerament abans del flanc del següent interval)
      només quan el valor canvia entre v[i] i v[i+1].
    - Si hi ha valor extra (ncicles+1), també pot haver-hi canvi dins l’últim interval.
    - El waveform s'acaba a t_end = ncicles * periode (no s'allarga).
    """
    if rng is None:
        rng = np.random.default_rng()

    _valida_llargada_valors(ncicles, valors, "estable")

    n_val = len(valors)
    intervals = min(ncicles, n_val - 1)
    t_end = ncicles * periode
    events = []

    for i in range(intervals):
        if valors[i] != valors[i + 1]:
            # situem el canvi 'abans' del límit de l'interval
            t1 = (i + 1) * periode
            # delta en [0.2, 0.5] del periode, però assegurem no trepitjar t0
            delta = rng.uniform(0.2, 0.5) * periode
            t = max(i * periode, t1 - delta)
            t = min(t, t1)     # clamp dins de l’interval
            t = min(t, t_end)  # i dins del temps global
            events.append((t, valors[i + 1]))

    return events_to_steps(valors[0], events, t_end)


# ---------------------------------------------------------------------
# AJUDA / ÚTILS
# ---------------------------------------------------------------------

def _is_X(v):
    return isinstance(v, str) and v == "X"

def _is_Z(v):
    return isinstance(v, str) and v == "Z"

def _is_B(v):
    return isinstance(v, str) and v == "B"

def _is_num(v):
    # Considerem numèrics només 0 i 1 (admesos com "0"/"1" o enters)
    if isinstance(v, int):
        return v in (0, 1)
    if isinstance(v, str):
        return v in ("0", "1")
    return False

def _to_num(v):
    # Converteix "0"/"1" a int; es crida només si _is_num(v) és True
    return int(v) if isinstance(v, str) else v


# ---------------------------------------------------------------------
# GRÀFIC
# ---------------------------------------------------------------------

def dibuixa(waves, titol, ncicles, periode=1.0, output=None, tipus_originals=None):
    fig, axes = plt.subplots(len(waves), 1, sharex=True, figsize=(11, 6))

    if len(waves) == 1:
        axes = [axes]

    fig.suptitle(titol, fontsize=14)

    # Pintar senyals (interval a interval)
    for ax, (nom, x, y) in zip(axes, waves):
        n = len(y)

        for i in range(n - 1):
            t0, t1 = x[i], x[i + 1]
            v = y[i]

            if _is_B(v):
                # "B" → cap valor: NO pintar res
                continue

            if _is_X(v):
                # "X" → indeterminació: hatching amb /// (diagonal cap a dreta)
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
                # "Z" → alta impedància:
                # Mostrar una seqüència contínua " - - Z - - Z - - Z ..."
                # durant tota la durada del tram, centrada i retallada.

                base_fs = plt.rcParams.get("font.size", 10.0)
                fs = base_fs * 1.8   # +80% mida de font

                # Patró repetit llarg
                pattern = " Z"
                repeated = pattern * 200   # suficient per omplir qualsevol tram

                # Clip rectangle: EXACTE als límits del tram Z
                clip_rect = plt.Rectangle(
                    (t0, -0.2),
                    t1 - t0,
                    1.4,
                    transform=ax.transData
                )
                ax.add_patch(clip_rect)
                clip_rect.set_visible(False)

                # Text centrat
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

                # Aplicar clip perquè no es surtin caràcters de l'interval
                txt.set_clip_path(clip_rect)

                continue

            if _is_num(v):
                # 0/1 → línia blava
                val = _to_num(v)
                ax.plot(
                    [t0, t1],
                    [val, val],
                    drawstyle="steps-post",
                    linewidth=2,
                    color='C0'
                )
                continue

            # Si arribem aquí, és un valor no previst (no hauria de passar)
            # Ens assegurem de no dibuixar res.
            continue

        # Línia vertical de transició per a canvis 0 <-> 1 (només quan tots dos són numèrics)
        for i in range(1, n):
            v_prev, v_cur = y[i - 1], y[i]
            if _is_num(v_prev) and _is_num(v_cur) and (_to_num(v_prev) != _to_num(v_cur)):
                t = x[i]
                y0, y1 = min(_to_num(v_prev), _to_num(v_cur)), max(_to_num(v_prev), _to_num(v_cur))
                ax.vlines(t, y0, y1, colors='C0', linewidth=2)

        # Ajustos visuals del panell
        ax.set_ylabel(nom, rotation=0, labelpad=30, va='center')
        ax.set_yticks([0, 1])
        ax.set_ylim(-0.4, 1.4)
        ax.grid(True, axis="y", linestyle=":", alpha=0.5)

    axes[-1].set_xlabel("Temps (cicles)")

    ticks = np.arange(0, ncicles + 1, 1)
    axes[-1].set_xticks(ticks)
    axes[-1].set_xticklabels([str(t) for t in ticks])

    # Límits exactes del cronograma (sense marges)
    for ax in axes:
        ax.set_xlim(0, ncicles)

    # Línies verticals de flanc de pujada del rellotge mestre
    rellotge_x = None
    rellotge_y = None

    for i, tipus in enumerate(tipus_originals):
        if tipus.lower() == "rellotge":
            rellotge_x, rellotge_y = waves[i][1], waves[i][2]
            break

    if rellotge_x is not None:
        flancs_pujada = []
        for i in range(1, len(rellotge_y)):
            if _is_num(rellotge_y[i - 1]) and _is_num(rellotge_y[i]) and (_to_num(rellotge_y[i - 1]) == 0 and _to_num(rellotge_y[i]) == 1):
                flancs_pujada.append(rellotge_x[i])

        for t in flancs_pujada:
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
            "Notes sobre longitud de valors per a 'custom' i 'estable':\n"
            "  - La longitud de la cadena de valors pot ser igual a N (= --cicles)\n"
            "    o igual a N+1.\n"
            "  - Si és N: l’últim interval es manté estable (sense transicions internes).\n"
            "  - Si és N+1: el valor extra permet una transició dins de l’últim interval\n"
            "    (entre N-1 i N), igual que a la resta d’intervals. El cronograma no\n"
            "    s’allarga i acaba a t = N.\n"
            "  - Per al tipus 'custom', el nombre de transicions ha de ser len(valors)-1.\n"
            "    Cada transició és un nombre en [0,1), separat per ';', i representa el\n"
            "    moment relatiu dins de cada interval i→i+1."
        ),
        epilog=(
            "Exemple d'ús:\n"
            "  programa.py --titol \"Cronograma EP/SP\" --cicles 5 \\\n"
            "    --nom \"Clk\" --tipus rellotge \\\n"
            "    --nom \"D[2]\" --tipus estable --valors 0X1Z0 \\\n"
            "    --nom \"D[1]\" --tipus estable --valors 1B110 \\\n"
            "    --nom \"D[0]\" --tipus custom  --valors 010100 --transicio 0.4;0.6;0.3;0.7;0.25 \\\n"
            "    --sortida sortida.png\n\n"
            "En l'exemple, D[0] té 6 valors amb --cicles 5: la darrera transició ocorre\n"
            "dins de l'últim interval (entre 4 i 5) sense allargar el cronograma."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--titol", required=True, help="Títol del cronograma")
    parser.add_argument("--cicles", type=int, required=True, help="Nombre de cicles (N)")
    parser.add_argument("--sortida", help="Ruta per guardar la imatge generada")

    parser.add_argument("--nom", action="append", help="Nom de la senyal")
    parser.add_argument("--tipus", action="append", help="Tipus: rellotge, complet, custom, estable")
    parser.add_argument("--valors", action="append", help="Cadena de bits per la senyal (0,1,X,Z,B)")
    parser.add_argument("--transicio", action="append", help="Transicions separades per ';' per tipus custom (valors en [0,1))")

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
            if not args.valors or idx_valors >= len(args.valors):
                parser.error(f"[{nom}] Falta --valors per al tipus 'complet'.")
            val = parse_valors(args.valors[idx_valors])
            idx_valors += 1
            x, y = senyal_complet(val, args.cicles, periode)

        elif tipus == "custom":
            if not args.valors or idx_valors >= len(args.valors):
                parser.error(f"[{nom}] Falta --valors per al tipus 'custom'.")
            if not args.transicio or idx_trans >= len(args.transicio):
                parser.error(f"[{nom}] Falta --transicio per al tipus 'custom'.")

            val = parse_valors(args.valors[idx_valors])
            trans = parse_transicions(args.transicio[idx_trans])

            idx_valors += 1
            idx_trans += 1

            x, y = senyal_custom(val, trans, args.cicles, periode)

        elif tipus == "estable":
            if not args.valors or idx_valors >= len(args.valors):
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
