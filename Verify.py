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
    return len(set(varianta).intersection(set(runda)))

# ==============================
# LAYOUT
# ==============================

col1, col2 = st.columns(2)

# ==============================
# RUNDE
# ==============================
with col1:
    st.header("📋 Runde")

    text_runde = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_bulk"
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(
            "Adaugă",
            type="primary",
            use_container_width=True,
            key="add_runde"
        ):
            if text_runde.strip():
                runde_noi = parse_runde_bulk(text_runde)
                if runde_noi:
                    st.session_state.runde.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde")
                    st.rerun()

    with col_btn2:
        if st.button(
            "Șterge",
            use_container_width=True,
            key="del_runde"
        ):
            st.session_state.runde = []
            st.rerun()

    if st.session_state.runde:
        st.caption(f"Total: {len(st.session_state.runde)} runde")
        container_runde = st.container(height=250)
        with container_runde:
            for i, runda in enumerate(st.session_state.runde, 1):
                st.text(f"{i}. {','.join(map(str, runda))}")

# ==============================
# VARIANTE
# ==============================
with col2:
    st.header("🎲 Variante")

    text_variante = st.text_area(
        "Format: 1, 6 7 5 77",
        height=150,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_bulk"
    )

    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button(
            "Adaugă",
            type="primary",
            use_container_width=True,
            key="add_variante"
        ):
            if text_variante.strip():
                variante_noi = parse_variante_bulk(text_variante)
                if variante_noi:
                    st.session_state.variante.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()

    with col_btn4:
        if st.button(
            "Șterge",
            use_container_width=True,
            key="del_variante"
        ):
            st.session_state.variante = []
            st.rerun()

    if st.session_state.variante:
        st.caption(f"Total: {len(st.session_state.variante)} variante")
        container_variante = st.container(height=250)
        with container_variante:
            for var in st.session_state.variante:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

# ==============================
# REZULTATE
# ==============================
st.divider()
st.header("🏆 Rezultate")

if st.session_state.runde and st.session_state.variante:

    numar_minim = st.slider(
        "Numere minime potrivite:",
        min_value=2,
        max_value=10,
        value=4,
        key="slider_minim"
    )

    runde_sets, variante_sets = precompute_sets(
        st.session_state.runde,
        st.session_state.variante
    )

    rezultate, total_castiguri = calculeaza_rezultate(
        runde_sets,
        variante_sets,
        numar_minim
    )

    castiguri_unice = sum(1 for _, c in rezultate if c > 0)

    rezultate_container = st.container(height=300)
    with rezultate_container:
        for i, castiguri in rezultate:
            st.text(f"Runda {i} - {castiguri} variante câștigătoare")

    st.divider()
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    col_s1.metric("Runde", len(st.session_state.runde))
    col_s1.download_button(
        "⬇️ Download",
        data="\n".join(",".join(map(str, r)) for r in st.session_state.runde),
        file_name="runde.txt",
        key="dl_runde"
    )

    col_s2.metric("Variante", len(st.session_state.variante))
    col_s2.download_button(
        "⬇️ Download",
        data="\n".join(
            f"{v['id']}, {' '.join(map(str, v['numere']))}"
            for v in st.session_state.variante
        ),
        file_name="variante.txt",
        key="dl_variante"
    )

    col_s3.metric("Câștiguri", total_castiguri)
    col_s3.download_button(
        "⬇️ Download",
        data="\n".join(f"Runda {i}: {c}" for i, c in rezultate),
        file_name="castiguri_totale.txt",
        key="dl_castiguri"
    )

    col_s4.metric("Câștiguri unice", castiguri_unice)
    col_s4.download_button(
        "⬇️ Download",
        data=(
            "\n".join(f"Runda {i}" for i, c in rezultate if c > 0)
            + f"\n\nTotal runde câștigătoare: {castiguri_unice}"
        ),
        file_name="castiguri_unice.txt",
        key="dl_castiguri_unice"
    )

else:
    st.info("Adaugă runde și variante pentru verificare")
