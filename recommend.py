"""
Study Specs — Laptop Recommendation Engine
--------------------------------------------
Given a student's academic domain (and optional preferences like budget,
performance need, graphics, processor brand, company, and storage type),
this recommends the best-fit laptops from the dataset using the
pre-computed domain suitability scores (score_cs_it, score_data_science, etc.).

This is the core logic layer for the project — the function
recommend_laptops() is what the Streamlit frontend (app.py) calls once
the student has answered the questionnaire.
"""

import sqlite3
import urllib.parse
import pandas as pd

# Maps the 11 academic domains to their score column in the dataset
DOMAIN_TO_COLUMN = {
    "CS & IT": "score_cs_it",
    "Engineering & Architecture": "score_engineering_arch",
    "Film/Media/Animation": "score_film_media",
    "Data Science & Statistics": "score_data_science",
    "Graphic Design & Fine Arts": "score_graphic_design_arts",
    "Medical & Health Sciences": "score_medical_health",
    "Earth & Physical Sciences": "score_earth_physical_sci",
    "Business/Finance/Economics": "score_business_finance",
    "Humanities & Social Sciences": "score_humanities_social",
    "Law & Public Policy": "score_law_policy",
    "Education & Communication": "score_education_comm",
}

# Performance tiers -> minimum core/RAM thresholds.
# Keeps the question beginner-friendly ("how heavy is your workload?")
# instead of asking a student to know what "16GB RAM" even means.
PERFORMANCE_TIERS = {
    "Light (notes, browsing, docs)": {"min_ram": 0, "min_cores": 0},
    "Medium (coding, office multitasking)": {"min_ram": 8, "min_cores": 6},
    "Heavy (video editing, gaming, 3D, simulations)": {"min_ram": 16, "min_cores": 8},
}

STORAGE_MAP = {
    "SSD (faster)": "SSD",
    "Hard Disk (cheaper, more space)": "Hard Disk",
    "eMMC (budget/light use)": "eMMC Storage",
}


def load_data(csv_path="study_specs_laptops_upgraded.csv"):
    """Load and lightly clean the laptop dataset.

    Reads from the given CSV path. If csv_path ends in .db, reads the
    'laptops' table from that SQLite file instead — so app.py can point
    this at either study_specs_laptops_upgraded.csv or study_specs.db
    without any other code changing.
    """
    if str(csv_path).endswith(".db"):
        conn = sqlite3.connect(csv_path)
        df = pd.read_sql("SELECT * FROM laptops", conn)
        conn.close()
    else:
        df = pd.read_csv(csv_path)

    # Basic cleaning: drop rows missing price/rating, since these are essential
    df = df.dropna(subset=["price", "rating"])
    return df


def recommend_laptops(
    df,
    domain,
    budget=None,
    min_rating=None,
    top_n=5,
    storage=None,
    performance=None,
    needs_dedicated_gpu=None,
    processor_brand=None,
    companies=None,
):
    """
    Return the top_n laptops best suited to a given academic domain.

    Parameters
    ----------
    df : pd.DataFrame              the loaded laptop dataset
    domain : str                   one of the keys in DOMAIN_TO_COLUMN
    budget : float, optional       max price in rupees
    min_rating : float, optional   minimum star rating (0-5)
    top_n : int                    number of results to return
    storage : str, optional        one of STORAGE_MAP's dataset values ("SSD"/"Hard Disk"/"eMMC Storage")
    performance : str, optional    one of PERFORMANCE_TIERS' keys
    needs_dedicated_gpu : bool, optional   True = only "Dedicated" gpu_type
    processor_brand : str, optional        "Intel" / "AMD" / "Apple" / etc. ("No preference" = skip)
    companies : list[str], optional        brand names to include ("No preference"/empty = skip)

    Returns
    -------
    pd.DataFrame with the top matching laptops, ranked by domain fit,
    including a 0-100 'match_percent' column.
    """
    if domain not in DOMAIN_TO_COLUMN:
        valid = ", ".join(DOMAIN_TO_COLUMN.keys())
        raise ValueError(f"Unknown domain '{domain}'. Choose from: {valid}")

    score_col = DOMAIN_TO_COLUMN[domain]
    result = df.copy()

    if budget is not None:
        result = result[result["price"] <= budget]
    if min_rating is not None:
        result = result[result["rating"] >= min_rating]
    if storage:
        result = result[result["memory_type"] == storage]
    if performance and performance in PERFORMANCE_TIERS:
        tier = PERFORMANCE_TIERS[performance]
        result = result[
            (result["ram_num"] >= tier["min_ram"])
            & (result["core_num"] >= tier["min_cores"])
        ]
    if needs_dedicated_gpu:
        result = result[result["gpu_type"] == "Dedicated"]
    if processor_brand and processor_brand != "No preference":
        result = result[result["processor_brand"] == processor_brand]
    if companies:
        result = result[result["brand_name"].isin(companies)]

    result = result.sort_values(by=score_col, ascending=False).head(top_n)

    display_cols = [
        "brand_name", "model", "price", "rating",
        "processor", "processor_brand", "ram", "ram_num", "core_num",
        "memory_type", "memory_size", "gpu_brand", "gpu_type", score_col,
    ]
    result = result[display_cols].rename(columns={score_col: "domain_fit_score"})

    # The pre-computed domain scores already sit on a 0-100 scale, so we
    # use them directly as a "match %" — easier for a non-technical
    # student to read than a raw "fit score".
    result["match_percent"] = result["domain_fit_score"].round(0).clip(upper=100).astype(int)

    return result


def why_this_laptop(row, domain, security_priority=None):
    """
    Build a short, plain-language list of reasons a laptop was recommended.
    Used to power the "Why this matches you" dropdown on the results page.
    Every reason is derived directly from the laptop's own data — nothing
    fabricated or copied from a review site.
    """
    reasons = []
    reasons.append(f"Scores {row.match_percent}% fit for {domain} coursework.")
    reasons.append(f"{row.ram} and a {row.core_num}-core {row.processor_brand} processor "
                    f"for handling your workload.")
    reasons.append(f"{row.memory_size}GB {row.memory_type} storage.")
    if row.gpu_type == "Dedicated":
        reasons.append(f"Dedicated {row.gpu_brand} graphics — useful for design, video, or gaming work.")
    if row.rating >= 4.5:
        reasons.append(f"Highly rated by buyers ({row.rating}★).")
    if security_priority == "High":
        if row.memory_type == "SSD":
            reasons.append("SSD storage supports fast, encrypted drives — a plus if data security matters to you.")
        reasons.append("Tip: enable BitLocker (Windows) or FileVault (Mac) for extra protection on any laptop you buy.")
    return reasons


def shopping_links(brand_name, model):
    """
    Build search-result links (not scraped live prices) for a laptop on a
    few major Indian marketplaces, so a student can quickly compare prices
    themselves. Using search URLs keeps this reliable without needing a
    paid price-comparison API.
    """
    query = urllib.parse.quote_plus(f"{brand_name} {model}")
    return {
        "Amazon": f"https://www.amazon.in/s?k={query}",
        "Flipkart": f"https://www.flipkart.com/search?q={query}",
        "Croma": f"https://www.croma.com/searchB?q={query}",
    }


def print_recommendations(recs, domain):
    """Pretty-print recommendations to the console."""
    if recs.empty:
        print(f"No laptops found matching your criteria for {domain}.")
        return
    print(f"\nTop {len(recs)} laptop recommendations for {domain}:\n")
    for i, row in enumerate(recs.itertuples(index=False), start=1):
        print(f"{i}. {row.brand_name} — {row.model}")
        print(f"   Price: ₹{row.price:,.0f} | Rating: {row.rating} | "
              f"Match: {row.match_percent}%")
        print(f"   {row.processor}, {row.ram}, {row.memory_size}GB {row.memory_type}, "
              f"{row.gpu_brand} {row.gpu_type}")
        print()


if __name__ == "__main__":
    # --- Example usage / quick test ---
    data = load_data("study_specs_laptops_upgraded.csv")

    # Example: a Data Science student with a budget of ₹70,000
    recs = recommend_laptops(
        data,
        domain="Data Science & Statistics",
        budget=70000,
        top_n=5,
    )
    print_recommendations(recs, "Data Science & Statistics")
