import streamlit as st
import pandas as pd

# Configurare pagină
st.set_page_config(
    page_title="Verificare Loterie",
    page_icon="🎰",
    layout="wide"
)

# Titlu principal
st.title("🎰 Verificare Variante Loterie")
st.divider()

# ==============================
# SPEED FUNCTIONS
# ==============================

@st.cache_data(show_spinner=False)
def parse_runde_bulk(text):
    runde = []
    for linie in text.splitlines():
        if not linie:
            continue
        nums = [int(n) for n in linie.split(',') if n.strip().isdigit()]
        if nums:
            runde.append(nums)
    return runde


@st.cache_data(show_spinner=False)
def parse_variante_bulk(text):
    variante = []
    for linie in text.splitlines():
        if ',' not in linie:
            continue
        id_var, rest = linie.split(',', 1)
        nums = [int(n) for n in rest.split() if n.strip().isdigit()]
        if nums:
            variante.append({
                "id": id_var.strip(),
                "numere": nums
            })
    return variante


@st.cache_data(show_spinner=False)
def precompute_sets(runde, variante):
    runde_sets = [set(r) for r in runde]
    variante_sets = [
        {"id": v["id"], "set": set(v["numere"])}
        for v in variante
    ]
    return runde_sets, variante_sets


@st.cache_data(show_spinner=False)
def calculeaza_rezultate(runde_sets, variante_sets, minim):
    rezultate = []
    total = 0

    for i, runda_set in enumerate(runde_sets, 1):
        castiguri = 0
        for var in variante_sets:
            if len(var["set"] & runda_set) >= minim:
                castiguri += 1
                total += 1
        rezultate.append((i, castiguri))

    return rezultate, total


# ==============================
# SESSION STATE
# ==============================

if 'runde' not in st.session_state:
    st.session_state.runde = []
if 'variante' not in st.session_state:
    st.session_state.variante = []


def verifica_varianta(varianta, runda):
    return len(set(varianta) & set(runda))


# ==============================
# INPUT
# ==============================

col1, col2 = st.columns(2)

with col1:
    st.header("📋 Runde")
    text_runde = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        key="input_runde_bulk"
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Adaugă", type="primary", use_container_width=True):
            r = parse_runde_bulk(text_runde)
            if r:
                st.session_state.runde.extend(r)
                st.rerun()

    with c2:
        if st.button("Șterge", use_container_width=True):
            st.session_state.runde = []
            st.rerun()

    if st.session_state.runde:
        st.caption(f"Total: {len(st.session_state.runde)} runde")
        with st.container(height=250):
            for i, r in enumerate(st.session_state.runde, 1):
                st.text(f"{i}. {','.join(map(str, r))}")

with col2:
    st.header("🎲 Variante")
    text_variante = st.text_area(
        "Format: 1, 6 7 5 77",
        height=150,
        key="input_variante_bulk"
    )

    c3, c4 = st.columns(2)
    with c3:
        if st.button("Adaugă", type="primary", use_container_width=True):
            v = parse_variante_bulk(text_variante)
            if v:
                st.session_state.variante.extend(v)
                st.rerun()

    with c4:
        if st.button("Șterge", use_container_width=True):
            st.session_state.variante = []
            st.rerun()

    if st.session_state.variante:
        st.caption(f"Total: {len(st.session_state.variante)} variante")
        with st.container(height=250):
            for v in st.session_state.variante:
                st.text(f"ID {v['id']}: {' '.join(map(str, v['numere']))}")


# ==============================
# REZULTATE
# ==============================

st.divider()
st.header("🏆 Rezultate")

if st.session_state.runde and st.session_state.variante:

    minim = st.slider("Numere minime potrivite:", 2, 10, 4)

    runde_sets, variante_sets = precompute_sets(
        st.session_state.runde,
        st.session_state.variante
    )

    rezultate, total_castiguri = calculeaza_rezultate(
        runde_sets, variante_sets, minim
    )

    winning_ids = set()
    for runda in runde_sets:
        for v in variante_sets:
            if len(v["set"] & runda) >= minim:
                winning_ids.add(v["id"])

    winning_variants = [
        f"{v['id']}, {' '.join(map(str, v['numere']))}"
        for v in st.session_state.variante if v["id"] in winning_ids
    ]

    losing_variants = [
        f"{v['id']}, {' '.join(map(str, v['numere']))}"
        for v in st.session_state.variante if v["id"] not in winning_ids
    ]

    winning_variants_unique = sorted(set(winning_variants))
    losing_variants_unique = sorted(set(losing_variants))

    winning_runde = [
        r for r, c in rezultate if c > 0
    ]
    losing_runde = [
        r for r, c in rezultate if c == 0
    ]

    winning_runde_lines = [str(r) for r in winning_runde]
    losing_runde_lines = [str(r) for r in losing_runde]

    winning_runde_unique = sorted(set(winning_runde_lines))
    losing_runde_unique = sorted(set(losing_runde_lines))

    # ================== DESCĂRCARE ==================
    st.divider()
    st.caption("⬇️ Descărcare rezultate")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        if winning_variants:
            st.download_button(
                "Variante câștigătoare",
                "\n".join(winning_variants),
                "variante_castigatoare.txt"
            )
            st.download_button(
                "Variante câștigătoare (unice)",
                "\n".join(winning_variants_unique),
                "variante_castigatoare_unice.txt"
            )

        if losing_variants:
            st.download_button(
                "Variante necâștigătoare",
                "\n".join(losing_variants),
                "variante_necastigatoare.txt"
            )
            st.download_button(
                "Variante necâștigătoare (unice)",
                "\n".join(losing_variants_unique),
                "variante_necastigatoare_unice.txt"
            )

    with col_d2:
        if winning_runde_lines:
            st.download_button(
                "Runde câștigătoare",
                "\n".join(winning_runde_lines),
                "runde_castigatoare.txt"
            )
            st.download_button(
                "Runde câștigătoare (unice)",
                "\n".join(winning_runde_unique),
                "runde_castigatoare_unice.txt"
            )

        if losing_runde_lines:
            st.download_button(
                "Runde necâștigătoare",
                "\n".join(losing_runde_lines),
                "runde_necastigatoare.txt"
            )
            st.download_button(
                "Runde necâștigătoare (unice)",
                "\n".join(losing_runde_unique),
                "runde_necastigatoare_unice.txt"
            )

else:
    st.info("Adaugă runde și variante pentru verificare")
