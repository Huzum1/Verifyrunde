import streamlit as st
import pandas as pd

# Configurare pagină
st.set_page_config(
    page_title="Verificare Loterie",
    page_icon="🎰",
    layout="wide"
)

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
            variante.append({"id": id_var.strip(), "numere": nums})
    return variante


@st.cache_data(show_spinner=False)
def precompute_sets(runde, variante):
    runde_sets = [set(r) for r in runde]
    variante_sets = [{"id": v["id"], "set": set(v["numere"])} for v in variante]
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
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde"):
            r = parse_runde_bulk(text_runde)
            if r:
                st.session_state.runde.extend(r)
                st.rerun()

    with c2:
        if st.button("Șterge", use_container_width=True, key="del_runde"):
            st.session_state.runde = []
            st.rerun()

with col2:
    st.header("🎲 Variante")

    text_variante = st.text_area(
        "Format: 1, 6 7 5 77",
        height=150,
        key="input_variante_bulk"
    )

    c3, c4 = st.columns(2)
    with c3:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var"):
            v = parse_variante_bulk(text_variante)
            if v:
                st.session_state.variante.extend(v)
                st.rerun()

    with c4:
        if st.button("Șterge", use_container_width=True, key="del_var"):
            st.session_state.variante = []
            st.rerun()


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

    # ==============================
    # LOGICĂ CORECTĂ PENTRU UNICE
    # ==============================

    castiguri_per_varianta = {v["id"]: 0 for v in st.session_state.variante}

    for runda_set in runde_sets:
        for v in variante_sets:
            if len(v["set"] & runda_set) >= minim:
                castiguri_per_varianta[v["id"]] += 1

    variante_castigatoare = [
        f"{v['id']}, {' '.join(map(str, v['numere']))}"
        for v in st.session_state.variante
        if castiguri_per_varianta[v["id"]] > 0
    ]

    variante_castigatoare_unice = [
        f"{v['id']}, {' '.join(map(str, v['numere']))}"
        for v in st.session_state.variante
        if castiguri_per_varianta[v["id"]] == 1
    ]

    variante_necastigatoare = [
        f"{v['id']}, {' '.join(map(str, v['numere']))}"
        for v in st.session_state.variante
        if castiguri_per_varianta[v["id"]] == 0
    ]

    # ==============================
    # STATISTICI (PĂSTRATE)
    # ==============================

    castiguri_unice = sum(1 for v in castiguri_per_varianta.values() if v == 1)

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runde", len(st.session_state.runde))
    c2.metric("Variante", len(st.session_state.variante))
    c3.metric("Câștiguri totale", total_castiguri)
    c4.metric("Variante cu 1 câștig", castiguri_unice)

    # ================== DESCĂRCARE ==================
    st.divider()
    st.caption("⬇️ Descărcare rezultate")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        if variante_castigatoare:
            st.download_button(
                "Variante câștigătoare",
                "\n".join(variante_castigatoare),
                "variante_castigatoare.txt"
            )

        if variante_castigatoare_unice:
            st.download_button(
                "Variante câștigătoare UNICE",
                "\n".join(variante_castigatoare_unice),
                "variante_castigatoare_unice.txt"
            )

        if variante_necastigatoare:
            st.download_button(
                "Variante necâștigătoare",
                "\n".join(variante_necastigatoare),
                "variante_necastigatoare.txt"
            )

else:
    st.info("Adaugă runde și variante pentru verificare")
