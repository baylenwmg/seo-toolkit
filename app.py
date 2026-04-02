import streamlit as st
import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

# ─── CONFIG ─────────────────────────────
st.set_page_config(
    page_title="SEO Toolkit",
    page_icon="🔍",
    layout="wide"
)

# ─── CACHE FETCH ────────────────────────
@st.cache_data(ttl=3600)
def fetch_sitemap(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.content, None

    except requests.exceptions.HTTPError as e:
        return None, f"HTTP Error: {e}"

    except Exception as e:
        return None, f"Error: {e}"

# ─── PARSER ─────────────────────────────
def parse_sitemap_xml(content):
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(content)

    # Index sitemap
    sitemaps = root.findall("sm:sitemap", ns)
    if sitemaps:
        links = [s.find("sm:loc", ns).text for s in sitemaps if s.find("sm:loc", ns) is not None]
        return None, links, "index"

    # Normal sitemap
    urls = []
    for elem in root.findall("sm:url", ns):
        loc = elem.find("sm:loc", ns)
        if loc is not None and loc.text:
            lm = elem.find("sm:lastmod", ns)
            cf = elem.find("sm:changefreq", ns)
            pr = elem.find("sm:priority", ns)

            urls.append({
                "URL": loc.text,
                "Path": urlparse(loc.text).path,
                "Last Modified": lm.text if lm is not None else "N/A",
                "Change Frequency": cf.text.capitalize() if (cf is not None and cf.text) else "N/A",
                "Priority": pr.text if pr is not None else "N/A",
            })

    return urls, [], "sitemap"

# ─── DISPLAY SCHEMA ─────────────────────
def display_schema(schema):
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    html = f'<script type="application/ld+json">\n{schema_json}\n</script>'

    st.success("✅ Schema Generated!")

    tab1, tab2 = st.tabs(["HTML", "Preview"])

    with tab1:
        st.code(html, language="html")
        st.download_button("Download JSON", schema_json, "schema.json")
    with tab2:
        st.json(schema)

# ─── SIDEBAR ────────────────────────────
tool = st.sidebar.radio(
    "Select Tool",
    ["Sitemap Parser", "Schema Generator"]
)

# ════════════════════════════════════════
# 🗺️ SITEMAP PARSER
# ════════════════════════════════════════
if tool == "Sitemap Parser":

    st.title("🗺️ Sitemap Parser")

    sitemap_url = st.text_input("Enter Sitemap URL")

    if st.button("Parse Sitemap"):

        if not sitemap_url.startswith("http"):
            st.error("Enter valid URL")
        else:
            with st.spinner("Processing..."):
                content, error = fetch_sitemap(sitemap_url)

            if error:
                st.error(error)
            else:
                urls, sub_sitemaps, typ = parse_sitemap_xml(content)

                if typ == "index":
                    st.warning("Sitemap Index Found")
                    for s in sub_sitemaps:
                        st.code(s)

                elif urls:
                    MAX_URLS = 500
                    if len(urls) > MAX_URLS:
                        st.warning("Showing first 500 URLs only")
                        urls = urls[:MAX_URLS]

                    df = pd.DataFrame(urls)

                    st.write(f"Total URLs: {len(df)}")
                    st.dataframe(df)

                    st.download_button(
                        "Download CSV",
                        df.to_csv(index=False),
                        "sitemap.csv"
                    )
                else:
                    st.warning("No URLs found")

# ════════════════════════════════════════
# 🧩 SCHEMA GENERATOR
# ════════════════════════════════════════
elif tool == "Schema Generator":

    st.title("🧩 Schema Generator")

    schema_type = st.selectbox(
        "Select Type",
        ["Local Business", "Product", "FAQ"]
    )

    # ─── LOCAL BUSINESS ───
    if schema_type == "Local Business":

        name = st.text_input("Business Name")
        phone = st.text_input("Phone")
        city = st.text_input("City")

        if st.button("Generate", key="local"):
            schema = {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": name,
                "telephone": phone,
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": city
                }
            }
            display_schema(schema)

    # ─── PRODUCT ───
    elif schema_type == "Product":

        name = st.text_input("Product Name")
        price = st.text_input("Price")

        if st.button("Generate", key="product"):
            schema = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": name,
                "offers": {
                    "@type": "Offer",
                    "price": price,
                    "priceCurrency": "INR"
                }
            }
            display_schema(schema)

    # ─── FAQ ───
    elif schema_type == "FAQ":

        q = st.text_input("Question")
        a = st.text_input("Answer")

        if st.button("Generate", key="faq"):
            schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [{
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                }]
            }
            display_schema(schema)
