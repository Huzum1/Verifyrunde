import streamlit as st
import pandas as pd
import numpy as np

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Verificare Loterie",
    page_icon="🎰",
    layout="wide"
)

# ---------- CACHE ----------
@st.cache_data(show_spinner=False)
def _parse_runde(text: str):
    return [np.array([int(n.strip()) for n in lin.split(',') if n.strip()])
            for lin in text.strip().splitlines() if lin.strip()]

@st.cache_data(show_spinner=False)
def _parse_variante(text: str):
    out = []
    for lin in text.strip().splitlines():
        if ',' not in lin: 
            continue
        id_part, nums_part = lin.split(',', 1)
        nums = np.array([int(n.strip()) for n in nums_part.split() if n.strip()])
        if nums.size:
            out.append({'id': id_part.strip(), 'numere': nums})
    return out

@st.cache_data(show_spinner=False)
def verifica_varianta(varianta, runda):
    """Returnează numărul de numere comune (aceeași semnatură)"""
    return len(np.intersect1d(varianta, runda, assume_unique=True))

# ---------- SESSION ----------
if 'runde' not in st.session_state:
    st.session_state.runde = []
if 'variante' not in st.session_state:
    st.session_state.variante = []

# ---------- UI (identic) ----------
st.title("🎰 Verificare Variante Loterie")
st.divider()

col1, col2 = st.columns(2)

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
        if st.button("Adaugă", type="primary", use_container_width=True):
            if text_runde.strip():
                parsed = _parse_runde(text_runde)
                if parsed:
                    st.session_state.runde.extend(parsed)
                    st.success(f"✅ {len(parsed)} runde")
                    st.rerun()
    with col_btn2:
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
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_bulk"
    )
    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var"):
            if text_variante.strip():
                parsed = _parse_variante(text_variante)
                if parsed:
                    st.session_state.variante.extend(parsed)
                    st.success(f"✅ {len(parsed)} variante")
                    st.rerun()
    with col_btn4:
        if st.button("Șterge", use_container_width=True, key="del_var"):
            st.session_state.variante = []
            st.rerun()
    if st.session_state.variante:
        st.caption(f"Total: {len(st.session_state.variante)} variante")
        with st.container(height=250):
            for v in st.session_state.variante:
                st.text(f"ID {v['id']}: {' '.join(map(str, v['numere']))}")

# ---------- REZULTATE (identic) ----------
st.divider()
st.header("🏆 Rezultate")

if st.session_state.runde and st.session_state.variante:
    numar_minim = st.slider("Numere minime potrivite:", min_value=2, max_value=10, value=4)
    st.divider()
    with st.container(height=300):
        for i, r in enumerate(st.session_state.runde, 1):
            castiguri = sum(verifica_varianta(v['numere'], r) >= numar_minim for v in st.session_state.variante)
            st.text(f"Runda {i} - {castiguri} variante câștigătoare")
    st.divider()
    total_castiguri = sum(verifica_varianta(v['numere'], r) >= numar_minim
                          for r in st.session_state.runde
                          for v in st.session_state.variante)
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Runde", len(st.session_state.runde))
    col_s2.metric("Variante", len(st.session_state.variante))
    col_s3.metric("Câștiguri", total_castiguri)
else:
    st.info("Adaugă runde și variante pentru verificare")
