import streamlit as st

# ==============================
# CONFIGURARE PAGINĂ
# ==============================

st.set_page_config(
    page_title="Verificare Loterie",
    page_icon="🎰",
    layout="wide"
)

st.title("🎰 Verificare Variante Loterie")
st.divider()

# ==============================
# FUNCȚII
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
        {"id": v["id"], "set": set(v["numere"]), "numere": v["numere"]}
        for v in variante
    ]
    return runde_sets, variante_sets


# ==============================
# SESSION STATE
# ==============================

st.session_state.setdefault("runde", [])
st.session_state.setdefault("variante", [])

# ==============================
# INPUT
# ==============================

col1, col2 = st.columns(2)

# RUNDE
with col1:
    st.header("📋 Runde")

    text_runde = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde"
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde"):
            r = parse_runde_bulk(text_runde)
            if r:
                st.session_state.runde.extend(r)
                st.rerun()

    with col_b:
        if st.button("Șterge", use_container_width=True, key="del_runde"):
            st.session_state.runde = []
            st.rerun()

    if st.session_state.runde:
        st.caption(f"Total: {len(st.session_state.runde)} runde")
        with st.container(height=250):
            for i, r in enumerate(st.session_state.runde, 1):
                st.text(f"{i}. {','.join(map(str, r))}")

# VARIANTE
with col2:
    st.header("🎲 Variante")

    text_variante = st.text_area(
        "Format: 1, 6 7 5 77",
        height=150,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante"
    )

    col_c, col_d = st.columns(2)

    with col_c:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_variante"):
            v = parse_variante_bulk(text_variante)
            if v:
                st.session_state.variante.extend(v)
                st.rerun()

    with col_d:
        if st.button("Șterge", use_container_width=True, key="del_variante"):
            st.session_state.variante = []
            st.rerun()

    if st.session_state.variante:
        st.caption(f"Total: {len(st.session_state.variante)} variante")
        with st.container(height=250):
            for v in st.session_state.variante:
                st.text(f"{v['id']}, {' '.join(map(str, v['numere']))}")

# ==============================
# REZULTATE
# ==============================

st.divider()
st.header("🏆 Rezultate")

if st.session_state.runde and st.session_state.variante:

    minim = st.slider(
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

    # COLECTARE CÂȘTIGURI
    castiguri_totale = []   # cu duplicate
    castiguri_unice = {}    # id -> varianta

    for runda_set in runde_sets:
        for v in variante_sets:
            if len(v["set"] & runda_set) >= minim:
                castiguri_totale.append(v)
                castiguri_unice[v["id"]] = v

    # AFIȘARE PE RUNDE (nemodificat)
    with st.container(height=300):
        for idx, runda_set in enumerate(runde_sets, 1):
            cnt = sum(
                1 for v in variante_sets
                if len(v["set"] & runda_set) >= minim
            )
            st.text(f"Runda {idx} - {cnt} variante câștigătoare")

    st.divider()
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    # RUNDE
    col_s1.metric("Runde", len(st.session_state.runde))
    col_s1.download_button(
        "⬇️ Download",
        data="\n".join(",".join(map(str, r)) for r in st.session_state.runde),
        file_name="runde.txt",
        key="dl_runde"
    )

    # VARIANTE
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

    # CÂȘTIGURI TOTALE (VARIANTE, CU DUPLICATE)
    col_s3.metric("Câștiguri", len(castiguri_totale))
    col_s3.download_button(
        "⬇️ Download",
        data="\n".join(
            f"{v['id']}, {' '.join(map(str, v['numere']))}"
            for v in castiguri_totale
        ),
        file_name="castiguri_totale.txt",
        key="dl_castiguri_totale"
    )

    # CÂȘTIGURI UNICE (VARIANTE UNICE)
    col_s4.metric("Câștiguri unice", len(castiguri_unice))
    col_s4.download_button(
        "⬇️ Download",
        data=(
            "\n".join(
                f"{v['id']}, {' '.join(map(str, v['numere']))}"
                for v in castiguri_unice.values()
            )
            + f"\n\nTotal variante câștigătoare unice: {len(castiguri_unice)}"
        ),
        file_name="castiguri_unice.txt",
        key="dl_castiguri_unice"
    )

else:
    st.info("Adaugă runde și variante pentru verificare")
