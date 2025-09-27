import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Dictionary Category Comparator")

# Sidebar: CSV loader
st.sidebar.header("Load Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    # Load CSV
    df = pd.read_csv(uploaded_file)

    # Clean columns
    df["dictionary"] = df["dictionary"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["extension"] = df["extension"].fillna("").astype(str)
    df["specificity"] = df["specificity"].astype(str).str.strip()

    # Remove fake 'nan'
    df = df[df["dictionary"].str.lower() != "nan"]

    # Dictionaries list
    dictionaries = sorted(df["dictionary"].unique().tolist())

    # --- Top Summary ---
    st.subheader("Dictionary Summary")

    summary_data = []
    for dic in dictionaries:
        subset = df[df["dictionary"] == dic]
        categories = subset["category"].nunique()
        all_words = [w.strip() for ext in subset["extension"] for w in str(ext).split(",") if w.strip()]
        tokens = len(all_words)
        types = len(set(all_words))
        summary_data.append({"Dictionary": dic, "Categories": categories, "Word tokens": tokens, "Word types": types})

    st.table(pd.DataFrame(summary_data))

    # Example redundant categories (you could compute this dynamically)
    st.markdown("### Redundant categories (safe to drop)")
    redundant = pd.DataFrame({
        "Connectives_category": ["all-demonstratives", "conjunctions", "determiners", "disjunctions"],
        "LexGram_category": ["demdet", "coord.conj", "det", "coord.conj"],
        "Connectives_n_words": [4, 2, 7, 1],
        "LexGram_n_words": [4, 6, 51, 6],
        "Shared_words": ["that, these, this, those", "and, but", "a, an, that, the, these, this, those", "or"]
    })
    st.dataframe(redundant)

    st.markdown("### Remaining categories (to keep, assign later)")
    remaining = df[(df["dictionary"] == "connective") & (~df["category"].isin(redundant["Connectives_category"]))]
    st.table(remaining[["category", "n_words"]].drop_duplicates())

    st.markdown("---")

    # --- UI Layout ---
    col1, col2 = st.columns(2)

    with col1:
        st.header("Dictionary 1")
        dict1 = st.selectbox("Select first dictionary", dictionaries, key="dict1")

        if dict1 == "LexGram":
            specificity_options = sorted(df["specificity"].unique().tolist())
            selected_specificities1 = st.multiselect("Filter by specificity (LexGram only)", specificity_options, default=specificity_options, key="spec1")
            categories1 = sorted(df.loc[(df["dictionary"] == dict1) & (df["specificity"].isin(selected_specificities1)), "category"].unique().tolist())
        else:
            categories1 = sorted(df.loc[df["dictionary"] == dict1, "category"].unique().tolist())

        cat1 = st.selectbox(f"Select category from {dict1}", categories1, key="cat1")

    with col2:
        st.header("Dictionary 2")
        dict2 = st.selectbox("Select second dictionary", dictionaries, key="dict2")

        if dict2 == "LexGram":
            specificity_options = sorted(df["specificity"].unique().tolist())
            selected_specificities2 = st.multiselect("Filter by specificity (LexGram only)", specificity_options, default=specificity_options, key="spec2")
            categories2 = sorted(df.loc[(df["dictionary"] == dict2) & (df["specificity"].isin(selected_specificities2)), "category"].unique().tolist())
        else:
            categories2 = sorted(df.loc[df["dictionary"] == dict2, "category"].unique().tolist())

        cat2 = st.selectbox(f"Select category from {dict2}", categories2, key="cat2")

    # --- Comparison ---
    if cat1 and cat2:
        words1 = set(w.strip() for w in df.loc[df["category"] == cat1, "extension"].iloc[0].split(",") if w.strip())
        words2 = set(w.strip() for w in df.loc[df["category"] == cat2, "extension"].iloc[0].split(",") if w.strip())
        shared = words1 & words2

        # Shared summary at top of block
        st.markdown("## Shared Words")
        st.write(f"**Count:** {len(shared)}")
        if shared:
            st.markdown(
                "<div style='border:1px solid #ddd; border-radius:5px; padding:10px; background-color:#fffbe6;'>"
                + ", ".join(sorted(shared))
                + "</div>",
                unsafe_allow_html=True,
            )

        # Show side-by-side word lists
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{cat1} ({dict1})")
            st.write(f"**Total words:** {len(words1)}")
            st.markdown(
                "<div style='border:1px solid #ddd; border-radius:5px; padding:10px; background-color:#f9f9f9;'>"
                + "<br>".join([f"<span style='color: {'red' if w in shared else 'black'}'>{w}</span>" for w in sorted(words1)])
                + "</div>",
                unsafe_allow_html=True,
            )

        with col2:
            st.subheader(f"{cat2} ({dict2})")
            st.write(f"**Total words:** {len(words2)}")
            st.markdown(
                "<div style='border:1px solid #ddd; border-radius:5px; padding:10px; background-color:#f9f9f9;'>"
                + "<br>".join([f"<span style='color: {'red' if w in shared else 'black'}'>{w}</span>" for w in sorted(words2)])
                + "</div>",
                unsafe_allow_html=True,
            )

else:
    st.info("Upload a CSV file in the sidebar to get started.")
