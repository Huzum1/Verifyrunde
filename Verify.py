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
        nums = [int(n) for n in linie.split(",") if n.strip().isdigit()]
        if nums:
            runde.append(nums)
    return runde


@st.cache_data(show_spinner=False)
def parse_variante_bulk(text):
    variante = []
    for linie in text.splitlines():
        if "," not in linie:
            continue
        idv, rest = linie.split(",", 1)
        nums = [int(n) for n in rest.split() if n.strip().isdigit()]
        if nums:
            variante.append({"id": idv.strip(), "numere": nums})
    return variante


# ==============================
# SESSION STATE
# ==============================

st.session_state.setdefault("runde", [])
st.session_state.setdefault("variante", [])

# ==============================
# INPUT
# ==============================

col1, col2 = st.columns(2)

with col1:
    st.header("📋 Runde")
    text_runde = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        key="input_runde"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde"):
            st.session_state.runde += parse_runde_bulk(text_runde)
            st.rerun()

    with col_b:
        if st.button("Șterge", use_container_width=True, key="del_runde"):
            st.session_state.runde = []
            st.rerun()

with col2:
    st.header("🎲 Variante")
    text_variante = st.text_area(
        "Format: 1, 6 7 5 77",
        height=150,
        key="input_variante"
    )

    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var"):
            st.session_state.variante += parse_variante_bulk(text_variante)
            st.rerun()

    with col_d:
        if st.button("Șterge", use_container_width=True, key="del_var"):
            st.session_state.variante = []
            st.rerun()

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

    castiguri_totale = []   # toate variantele câștigătoare
    castiguri_unice = []    # max 1 per rundă

    for runda in st.session_state.runde:
        rset = set(runda)
        castig_runda = False

        for v in st.session_state.variante:
            if len(set(v["numere"]) & rset) >= minim:
                castiguri_totale.append(v)

                if not castig_runda:
                    castiguri_unice.append(v)
                    castig_runda = True

    # ==============================
    # AFIȘARE PE RUNDE (nemodificat)
    # ==============================

    with st.container(height=300):
        for i, runda in enumerate(st.session_state.runde, 1):
            cnt = sum(
                1 for v in st.session_state.variante
                if len(set(v["numere"]) & set(runda)) >= minim
            )
            st.text(f"Runda {i} - {cnt} variante câștigătoare")

    # ==============================
    # METRICS + DOWNLOAD
    # ==============================

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    col_s1.metric("Runde", len(st.session_state.runde))
    col_s1.download_button(
        "⬇️ Download",
        "\n".join(",".join(map(str, r)) for r in st.session_state.runde),
        "runde.txt",
        key="dl_runde"
    )

    col_s2.metric("Variante", len(st.session_state.variante))
    col_s2.download_button(
        "⬇️ Download",
        "\n".join(
            f"{v['id']}, {' '.join(map(str, v['numere']))}"
            for v in st.session_state.variante
        ),
        "variante.txt",
        key="dl_variante"
    )

    col_s3.metric("Câștiguri", len(castiguri_totale))
    col_s3.download_button(
        "⬇️ Download",
        "\n".join(
            f"{v['id']}, {' '.join(map(str, v['numere']))}"
            for v in castiguri_totale
        ),
        "castiguri_totale.txt",
        key="dl_castiguri_totale"
    )

    col_s4.metric("Câștiguri unice", len(castiguri_unice))
    col_s4.download_button(
        "⬇️ Download",
        "\n".join(
            f"{v['id']}, {' '.join(map(str, v['numere']))}"
            for v in castiguri_unice
        ),
        "castiguri_unice.txt",
        key="dl_castiguri_unice"
    )

else:
    st.info("Adaugă runde și variante pentru verificare")
