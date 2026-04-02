import streamlit as st
import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Toolkit – Sitemap & Schema",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
        padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 2rem;
        color: white; text-align: center; border: 1px solid #334155;
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; color: #e2e8f0; }
    .main-header p { color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 1rem; }
    .stat-card {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 1.2rem; text-align: center;
    }
    .stat-number { font-size: 2rem; font-weight: 700; color: #0f172a; font-family: 'Space Grotesk', sans-serif; }
    .stat-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
    .success-banner {
        background: #dcfce7; border: 1px solid #86efac;
        border-radius: 10px; padding: 1rem 1.5rem; color: #166534; font-weight: 500;
    }
    .tip-box {
        background: #eff6ff; border-left: 4px solid #3b82f6;
        padding: 0.8rem 1rem; border-radius: 0 8px 8px 0;
        color: #1e40af; font-size: 0.9rem; margin: 1rem 0;
    }
    div[data-testid="stSidebar"] { background: #0f172a; }
    div[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white; border: none; border-radius: 8px; padding: 0.6rem 2rem;
        font-weight: 600; font-family: 'Space Grotesk', sans-serif;
        transition: all 0.2s; width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af);
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 600 !important; width: 100%;
    }
    .stTextInput > div > div > input { border-radius: 8px; border: 1.5px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] { font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─── HELPER: DISPLAY SCHEMA ────────────────────────────────────────────────────
def display_schema(schema):
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    html_code = f'<script type="application/ld+json">\n{schema_json}\n</script>'
    type_name = schema.get("@type", "schema").lower()
    ts = datetime.now().strftime('%Y%m%d%H%M')

    st.markdown("")
    st.markdown('<div class="success-banner">✅ Schema generated! Copy the HTML code below and paste it on your website.</div>', unsafe_allow_html=True)
    st.markdown("")

    tab_a, tab_b = st.tabs(["📋 HTML Code (paste on website)", "🔍 Preview"])
    with tab_a:
        st.code(html_code, language="html")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("⬇️ Download .json", json.dumps(schema, indent=2, ensure_ascii=False),
                f"schema_{type_name}_{ts}.json", "application/json", use_container_width=True)
        with d2:
            st.download_button("⬇️ Download .html", html_code,
                f"schema_{type_name}_{ts}.html", "text/html", use_container_width=True)
    with tab_b:
        st.json(schema)
        st.markdown("**Validate your schema:**  [Google Rich Results Test](https://search.google.com/test/rich-results)  |  [Schema.org Validator](https://validator.schema.org/)")


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 SEO Toolkit")
    st.markdown("---")
    tool = st.radio("Tool", ["🗺️ Sitemap Parser", "🧩 Schema Generator", "📋 How to Use"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Built for:** Internal Team Use")
    st.caption("All processing is in the backend. Your data is never stored.")

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔍 SEO Toolkit</h1>
    <p>Sitemap Parser & Schema Generator — Built for your team</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# 1. SITEMAP PARSER
# ════════════════════════════════════════════════════════════════════════════════
if tool == "🗺️ Sitemap Parser":
    st.header("🗺️ Sitemap Parser")
    st.markdown("Enter any website's sitemap URL to extract and analyse all its pages.")
    st.markdown('<div class="tip-box">💡 <b>Tip:</b> Most sitemaps are at <code>https://yourwebsite.com/sitemap.xml</code></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([4, 1])
    with c1:
        sitemap_url = st.text_input("URL", placeholder="https://example.com/sitemap.xml", label_visibility="collapsed")
    with c2:
        parse_btn = st.button("🔍 Parse", use_container_width=True)

    def fetch_sitemap(url):
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SEOToolkit/1.0)"}, timeout=15)
            r.raise_for_status()
            return r.content, None
        except requests.exceptions.ConnectionError:
            return None, "❌ Could not connect. Check the URL and your internet."
        except requests.exceptions.Timeout:
            return None, "❌ Request timed out. The server took too long."
        except requests.exceptions.HTTPError as e:
            return None, f"❌ HTTP Error: {e}"
        except Exception as e:
            return None, f"❌ Error: {e}"

    def parse_sitemap_xml(content):
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            return None, [], f"parse_error:{e}"

        sitemaps = root.findall("sm:sitemap", ns)
        if sitemaps:
            links = [s.find("sm:loc", ns).text for s in sitemaps if s.find("sm:loc", ns) is not None]
            return None, links, "index"

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
                    "Change Frequency": cf.text.capitalize() if cf is not None else "N/A",
                    "Priority": pr.text if pr is not None else "N/A",
                })
        return urls, [], "sitemap"

    if parse_btn:
        if not sitemap_url:
            st.warning("Please enter a sitemap URL.")
        elif not sitemap_url.startswith("http"):
            st.error("Please enter a valid URL starting with https://")
        else:
            with st.spinner("Fetching sitemap..."):
                content, error = fetch_sitemap(sitemap_url)
            if error:
                st.error(error)
            else:
                urls, sub_sitemaps, sitemap_type = parse_sitemap_xml(content)
                if sitemap_type == "index":
                    st.warning(f"🗂️ This is a **Sitemap Index** with **{len(sub_sitemaps)} sub-sitemaps**. Paste one below to parse its pages:")
                    for s in sub_sitemaps:
                        st.code(s)
                elif sitemap_type.startswith("parse_error"):
                    st.error(f"Could not read XML: {sitemap_type}")
                elif urls:
                    df = pd.DataFrame(urls)
                    domain = urlparse(sitemap_url).netloc
                    dated = (df["Last Modified"] != "N/A").sum()
                    try:
                        high_p = df["Priority"].apply(lambda x: float(x) >= 0.8 if x != "N/A" else False).sum()
                    except Exception:
                        high_p = 0

                    st.markdown(f'<div class="success-banner">✅ Found <b>{len(urls)} URLs</b> from <b>{domain}</b></div>', unsafe_allow_html=True)
                    st.markdown("")
                    for col, val, label in zip(
                        st.columns(4),
                        [len(urls), int(dated), int(high_p), df["Path"].nunique()],
                        ["Total URLs", "Have Date", "High Priority", "Unique Paths"]
                    ):
                        with col:
                            st.markdown(f'<div class="stat-card"><div class="stat-number">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

                    st.markdown("")
                    kw = st.text_input("🔎 Filter results", placeholder="Type keyword to filter...")
                    ddf = df[df["URL"].str.contains(kw, case=False, na=False)] if kw else df
                    if kw:
                        st.caption(f"Showing {len(ddf)} of {len(df)} results")
                    st.dataframe(ddf, use_container_width=True, height=420)

                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.download_button("⬇️ Download CSV", ddf.to_csv(index=False).encode(),
                            f"sitemap_{domain}_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
                    with dl2:
                        st.download_button("⬇️ Download URLs (.txt)", "\n".join(ddf["URL"].tolist()),
                            f"urls_{domain}.txt", "text/plain", use_container_width=True)
                else:
                    st.warning("No URLs found in this sitemap. It may be empty or non-standard.")


# ════════════════════════════════════════════════════════════════════════════════
# 2. SCHEMA GENERATOR
# ════════════════════════════════════════════════════════════════════════════════
elif tool == "🧩 Schema Generator":
    st.header("🧩 Schema Generator")
    st.markdown("Fill in your details to generate **Schema.org JSON-LD** — helps Google understand your website and show rich results.")

    schema_type = st.selectbox("Select Schema Type", [
        "🏢 Local Business", "🛍️ Product", "❓ FAQ Page",
        "⭐ Review", "👤 Person / Professional",
        "🌐 Organization / Company", "📰 Article / Blog Post",
    ])
    st.markdown("---")

    if schema_type == "🏢 Local Business":
        st.subheader("🏢 Local Business Details")
        c1, c2 = st.columns(2)
        with c1:
            biz_name    = st.text_input("Business Name *", placeholder="Raj Electronics")
            biz_type    = st.selectbox("Business Type", ["LocalBusiness","Restaurant","Store","MedicalBusiness","HealthAndBeautyBusiness","LegalService","FinancialService","AutoDealer","HotelOrMotel","RealEstateAgent"])
            phone       = st.text_input("Phone *", placeholder="+91 98765 43210")
            email       = st.text_input("Email", placeholder="info@business.com")
            website     = st.text_input("Website", placeholder="https://yourbusiness.com")
        with c2:
            street      = st.text_input("Street Address *", placeholder="123 MG Road")
            city        = st.text_input("City *", placeholder="Surat")
            state       = st.text_input("State", placeholder="Gujarat")
            pincode     = st.text_input("PIN Code", placeholder="395001")
            country     = st.text_input("Country", value="India")
        c3, c4 = st.columns(2)
        with c3:
            hours       = st.text_input("Opening Hours", placeholder="Mon-Sat 09:00-19:00")
            price_range = st.selectbox("Price Range", ["", "₹", "₹₹", "₹₹₹", "₹₹₹₹"])
        with c4:
            description = st.text_area("Description", placeholder="Short description...", height=100)
        c5, c6 = st.columns(2)
        with c5: lat = st.text_input("Latitude (optional)", placeholder="21.1702")
        with c6: lng = st.text_input("Longitude (optional)", placeholder="72.8311")

        if st.button("⚡ Generate Schema"):
            if not biz_name or not phone or not street or not city:
                st.error("Please fill in all required (*) fields.")
            else:
                schema = {
                    "@context": "https://schema.org", "@type": biz_type,
                    "name": biz_name, "description": description, "telephone": phone,
                    "address": {"@type": "PostalAddress", "streetAddress": street,
                        "addressLocality": city, "addressRegion": state,
                        "postalCode": pincode, "addressCountry": country}
                }
                if email: schema["email"] = email
                if website: schema["url"] = website
                if hours: schema["openingHours"] = hours
                if price_range: schema["priceRange"] = price_range
                if lat and lng: schema["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
                display_schema(schema)

    elif schema_type == "🛍️ Product":
        st.subheader("🛍️ Product Details")
        c1, c2 = st.columns(2)
        with c1:
            prod_name    = st.text_input("Product Name *", placeholder="Samsung Galaxy S24")
            brand        = st.text_input("Brand *", placeholder="Samsung")
            sku          = st.text_input("SKU / Model No.", placeholder="SM-S9210")
            price        = st.text_input("Price *", placeholder="79999")
            currency     = st.selectbox("Currency", ["INR","USD","EUR","GBP"])
        with c2:
            availability = st.selectbox("Availability", ["InStock","OutOfStock","PreOrder","Discontinued"])
            condition    = st.selectbox("Condition", ["NewCondition","UsedCondition","RefurbishedCondition"])
            prod_url     = st.text_input("Product URL", placeholder="https://store.com/product")
            image_url    = st.text_input("Product Image URL", placeholder="https://store.com/img.jpg")
        prod_desc = st.text_area("Description *", placeholder="Describe the product...", height=100)
        st.markdown("**Optional — Add a Review**")
        r1, r2, r3 = st.columns(3)
        with r1: reviewer  = st.text_input("Reviewer Name", placeholder="Priya Sharma")
        with r2: rev_score = st.slider("Rating", 1, 5, 5)
        with r3: rev_body  = st.text_input("Review Text", placeholder="Excellent product!")

        if st.button("⚡ Generate Schema"):
            if not prod_name or not brand or not price or not prod_desc:
                st.error("Please fill in all required (*) fields.")
            else:
                schema = {
                    "@context": "https://schema.org", "@type": "Product",
                    "name": prod_name, "description": prod_desc,
                    "brand": {"@type": "Brand", "name": brand},
                    "offers": {"@type": "Offer", "price": price, "priceCurrency": currency,
                        "availability": f"https://schema.org/{availability}",
                        "itemCondition": f"https://schema.org/{condition}"}
                }
                if sku: schema["sku"] = sku
                if prod_url: schema["url"] = prod_url
                if image_url: schema["image"] = image_url
                if reviewer:
                    schema["review"] = {"@type": "Review",
                        "author": {"@type": "Person", "name": reviewer},
                        "reviewRating": {"@type": "Rating", "ratingValue": rev_score, "bestRating": 5},
                        "reviewBody": rev_body}
                display_schema(schema)

    elif schema_type == "❓ FAQ Page":
        st.subheader("❓ FAQ Page Schema")
        st.info("These FAQs can appear directly inside Google search results!")
        num_faqs = st.number_input("Number of FAQs", min_value=1, max_value=20, value=3)
        faqs = []
        for i in range(int(num_faqs)):
            st.markdown(f"**FAQ {i+1}**")
            q = st.text_input(f"Question {i+1}", key=f"q{i}", placeholder="e.g. What are your working hours?")
            a = st.text_area(f"Answer {i+1}", key=f"a{i}", placeholder="We are open Mon–Sat 9am to 7pm.", height=80)
            if q and a:
                faqs.append({"q": q, "a": a})
            st.markdown("")

        if st.button("⚡ Generate Schema"):
            if not faqs:
                st.error("Please fill in at least one question and answer.")
            else:
                schema = {
                    "@context": "https://schema.org", "@type": "FAQPage",
                    "mainEntity": [{"@type": "Question", "name": f["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]
                }
                display_schema(schema)

    elif schema_type == "⭐ Review":
        st.subheader("⭐ Review Schema")
        c1, c2 = st.columns(2)
        with c1:
            item_name     = st.text_input("Item Reviewed *", placeholder="iPhone 15 Pro")
            item_type     = st.selectbox("Item Type", ["Product","LocalBusiness","Book","Movie","Software"])
            reviewer_name = st.text_input("Reviewer Name *", placeholder="Priya Sharma")
        with c2:
            rev_rating  = st.slider("Rating *", 1, 5, 5)
            best_rating = st.number_input("Best Possible Rating", value=5)
            pub_date    = st.date_input("Review Date")
        review_text = st.text_area("Review Text *", placeholder="Full review...", height=120)

        if st.button("⚡ Generate Schema"):
            if not item_name or not reviewer_name or not review_text:
                st.error("Please fill all required fields.")
            else:
                schema = {
                    "@context": "https://schema.org", "@type": "Review",
                    "itemReviewed": {"@type": item_type, "name": item_name},
                    "author": {"@type": "Person", "name": reviewer_name},
                    "reviewRating": {"@type": "Rating", "ratingValue": rev_rating, "bestRating": int(best_rating)},
                    "reviewBody": review_text, "datePublished": pub_date.strftime("%Y-%m-%d")
                }
                display_schema(schema)

    elif schema_type == "👤 Person / Professional":
        st.subheader("👤 Person / Professional Schema")
        c1, c2 = st.columns(2)
        with c1:
            person_name  = st.text_input("Full Name *", placeholder="Dr. Amit Patel")
            job_title    = st.text_input("Job Title *", placeholder="Cardiologist")
            org          = st.text_input("Organization", placeholder="Apollo Hospitals")
            person_email = st.text_input("Email", placeholder="dr.amit@hospital.com")
        with c2:
            person_url   = st.text_input("Profile URL", placeholder="https://website.com/about")
            person_img   = st.text_input("Photo URL", placeholder="https://website.com/photo.jpg")
            linkedin     = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/...")
        bio = st.text_area("Bio / Description", placeholder="Short professional bio...", height=100)

        if st.button("⚡ Generate Schema"):
            if not person_name or not job_title:
                st.error("Name and Job Title are required.")
            else:
                schema = {"@context": "https://schema.org", "@type": "Person",
                    "name": person_name, "jobTitle": job_title, "description": bio}
                if org: schema["worksFor"] = {"@type": "Organization", "name": org}
                if person_email: schema["email"] = person_email
                if person_url: schema["url"] = person_url
                if person_img: schema["image"] = person_img
                if linkedin: schema["sameAs"] = [linkedin]
                display_schema(schema)

    elif schema_type == "🌐 Organization / Company":
        st.subheader("🌐 Organization / Company Schema")
        c1, c2 = st.columns(2)
        with c1:
            org_name    = st.text_input("Organization Name *", placeholder="Tata Consultancy Services")
            org_type    = st.selectbox("Type", ["Organization","Corporation","NGO","EducationalOrganization","GovernmentOrganization"])
            org_url     = st.text_input("Website *", placeholder="https://yourcompany.com")
            org_email   = st.text_input("Email", placeholder="info@company.com")
            org_phone   = st.text_input("Phone", placeholder="+91 22 1234 5678")
        with c2:
            org_logo    = st.text_input("Logo URL", placeholder="https://company.com/logo.png")
            org_founded = st.text_input("Founding Year", placeholder="1995")
            social_fb   = st.text_input("Facebook URL", placeholder="https://facebook.com/...")
            social_tw   = st.text_input("Twitter URL", placeholder="https://twitter.com/...")
            social_li   = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/company/...")
        org_desc = st.text_area("Description *", placeholder="Describe your organization...", height=100)

        if st.button("⚡ Generate Schema"):
            if not org_name or not org_url or not org_desc:
                st.error("Name, Website and Description are required.")
            else:
                schema = {"@context": "https://schema.org", "@type": org_type,
                    "name": org_name, "url": org_url, "description": org_desc}
                if org_logo: schema["logo"] = org_logo
                if org_email: schema["email"] = org_email
                if org_phone: schema["telephone"] = org_phone
                if org_founded: schema["foundingDate"] = org_founded
                socials = [s for s in [social_fb, social_tw, social_li] if s]
                if socials: schema["sameAs"] = socials
                display_schema(schema)

    elif schema_type == "📰 Article / Blog Post":
        st.subheader("📰 Article / Blog Post Schema")
        c1, c2 = st.columns(2)
        with c1:
            art_title    = st.text_input("Article Title *", placeholder="Top 10 SEO Tips in 2025")
            art_author   = st.text_input("Author Name *", placeholder="Rahul Verma")
            art_pub      = st.text_input("Publisher / Site Name *", placeholder="SEO India Blog")
            art_url      = st.text_input("Article URL", placeholder="https://blog.com/article")
        with c2:
            art_pub_date = st.date_input("Published Date")
            art_mod_date = st.date_input("Last Modified Date")
            art_img      = st.text_input("Featured Image URL", placeholder="https://blog.com/image.jpg")
            art_type     = st.selectbox("Type", ["Article","BlogPosting","NewsArticle","TechArticle"])
        art_desc = st.text_area("Article Description *", placeholder="Brief summary of the article...", height=100)

        if st.button("⚡ Generate Schema"):
            if not art_title or not art_author or not art_pub or not art_desc:
                st.error("Please fill all required (*) fields.")
            else:
                schema = {
                    "@context": "https://schema.org", "@type": art_type,
                    "headline": art_title, "description": art_desc,
                    "author": {"@type": "Person", "name": art_author},
                    "publisher": {"@type": "Organization", "name": art_pub},
                    "datePublished": art_pub_date.strftime("%Y-%m-%d"),
                    "dateModified": art_mod_date.strftime("%Y-%m-%d")
                }
                if art_url: schema["url"] = art_url
                if art_img: schema["image"] = art_img
                display_schema(schema)


# ════════════════════════════════════════════════════════════════════════════════
# 3. HOW TO USE
# ════════════════════════════════════════════════════════════════════════════════
elif tool == "📋 How to Use":
    st.header("📋 How to Use This Tool")
    tab1, tab2, tab3 = st.tabs(["🗺️ Sitemap Parser", "🧩 Schema Generator", "🌐 Where to Paste Schema"])

    with tab1:
        st.markdown("""
### Sitemap Parser — Step by Step

**Step 1** — Go to the website you want to analyse

**Step 2** — Find the sitemap URL. Try these:
- `https://website.com/sitemap.xml`
- `https://website.com/sitemap_index.xml`
- Check `https://website.com/robots.txt` — it lists the sitemap

**Step 3** — Paste the URL into the Sitemap Parser tool

**Step 4** — Click **Parse**

**Step 5** — View all pages, filter by keyword, download as CSV or TXT

---
**Column meanings:**
| Column | Meaning |
|---|---|
| URL | Full page address |
| Path | Page path after the domain |
| Last Modified | When the page was last updated |
| Change Frequency | How often Google should re-crawl |
| Priority | 0.0 (lowest) to 1.0 (most important) |
        """)

    with tab2:
        st.markdown("""
### Schema Generator — Step by Step

**Step 1** — Choose the schema type that matches your need

**Step 2** — Fill in the form (fields with * are required)

**Step 3** — Click **Generate Schema**

**Step 4** — Copy the code OR click Download

**Step 5** — Paste it on your website (see next tab)

---
| Schema Type | Use For |
|---|---|
| 🏢 Local Business | Shop, office, clinic, restaurant |
| 🛍️ Product | Any product you sell online |
| ❓ FAQ | FAQ sections that appear in Google |
| ⭐ Review | Customer reviews |
| 👤 Person | Doctors, lawyers, consultants |
| 🌐 Organization | Companies, NGOs, institutions |
| 📰 Article | Blog posts, news articles |
        """)

    with tab3:
        st.markdown("""
### Where to Paste the Schema Code

After generating and downloading the schema, add it to your website:

---
#### WordPress (Easiest — No Coding)
1. Install free plugin: **Header Footer Code Manager**
2. WP Admin → HFCM → Add New
3. Paste the schema code → Location: Site Wide Header
4. Save ✅

#### Any Website (Manual)
Paste before `</head>` in your HTML:
```html
<script type="application/ld+json">
{ ...your schema code... }
</script>
</head>
```

#### Google Tag Manager (No code access needed)
1. GTM → New Tag → Custom HTML
2. Paste full schema code
3. Trigger: All Pages → Publish ✅

---
**Always test after adding:**
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)
        """)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("🔒 All processing happens in the backend. No data is stored or shared externally.")
