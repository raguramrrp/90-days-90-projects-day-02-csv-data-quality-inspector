"""
Synthetic Dataset Generator
Generates realistic benchmark datasets for testing and demonstrating
the Automated Dataset Quality & Profiling Engine.
"""

import os
import random
import numpy as np
import pandas as pd


def generate_dirty_ecommerce(output_path: str, n_rows: int = 500, seed: int = 42):
    """
    Generates a realistic dirty e-commerce dataset containing missing values,
    duplicate transactions, extreme price/quantity outliers, untrimmed whitespace,
    and string formatting issues.
    """
    random.seed(seed)
    np.random.seed(seed)

    categories = [
        "Electronics", "Home & Kitchen", "Apparel", "Books",
        "Beauty & Health", "Sports", "Toys"
    ]
    countries = ["United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "Australia"]

    data = []
    base_date = pd.Timestamp("2024-01-01")

    for i in range(1, n_rows + 1):
        order_id = f"ORD-{10000 + i}"
        customer_id = f"CUST-{random.randint(100, 250)}" if random.random() > 0.08 else np.nan
        category = random.choice(categories)
        if random.random() < 0.15:
            # Inject untrimmed whitespace
            category = f"  {category}  " if random.random() > 0.5 else f" {category}"

        # Unit price with outliers
        if random.random() < 0.03:
            price = round(float(np.random.uniform(5000, 25000)), 2)  # Extreme high outlier
        elif random.random() < 0.01:
            price = -25.50  # Negative price error
        else:
            price = round(float(np.random.exponential(scale=65) + 5), 2)

        # Quantity
        if random.random() < 0.02:
            quantity = 500  # Bulk order outlier
        else:
            quantity = random.randint(1, 8)

        # Country
        country = random.choice(countries)
        if random.random() < 0.05:
            country = f" {country} "

        # Date
        days_offset = random.randint(0, 180)
        order_date = base_date + pd.Timedelta(days=days_offset)
        date_str = order_date.strftime("%Y-%m-%d") if random.random() > 0.10 else order_date.strftime("%m/%d/%Y")

        # Payment status with missing
        status = random.choice(["Completed", "Shipped", "Pending", "Cancelled"])
        if random.random() < 0.12:
            status = np.nan

        # Discount (sometimes NaN, mostly 0.0 - 0.3)
        discount = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.25]), 2) if random.random() > 0.20 else np.nan

        # Rating (1 to 5, nullable)
        rating = random.randint(1, 5) if random.random() > 0.25 else np.nan

        # Notes column (mostly empty - severe missingness)
        notes = "Urgent delivery requested" if random.random() < 0.05 else np.nan

        data.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "category": category,
            "unit_price": price,
            "quantity": quantity,
            "country": country,
            "order_date": date_str,
            "status": status,
            "discount": discount,
            "rating": rating,
            "notes": notes,
        })

    df = pd.DataFrame(data)

    # Inject exact duplicate rows (approx 5% duplicates)
    dup_indices = random.sample(range(len(df)), int(n_rows * 0.05))
    duplicates = df.iloc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # Inject 2 completely empty rows
    empty_row = pd.DataFrame([{col: np.nan for col in df.columns}] * 2)
    df = pd.concat([df, empty_row], ignore_index=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated dirty e-commerce dataset: {output_path} ({len(df)} rows, {len(df.columns)} cols)")


def generate_employee_records(output_path: str, n_rows: int = 350, seed: int = 101):
    """
    Generates an HR employee records dataset with constant columns, negative experience,
    duplicate emails, and salary outliers.
    """
    random.seed(seed)
    np.random.seed(seed)

    departments = ["Engineering", "Product", "Sales", "Marketing", "HR", "Legal", "Operations"]
    titles = ["Specialist", "Senior", "Lead", "Manager", "Director"]

    data = []
    for i in range(1, n_rows + 1):
        emp_id = f"EMP-{2000 + i}"
        first_name = random.choice(["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Chris"])
        last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"])
        email = f"{first_name.lower()}.{last_name.lower()}@acmecorp.com"
        dept = random.choice(departments)
        level = random.choice(titles)

        # Experience with occasional negative value
        if random.random() < 0.03:
            years_exp = -2  # Data entry glitch
        else:
            years_exp = random.randint(0, 30)

        # Salary with executive outliers
        if random.random() < 0.03:
            salary = random.choice([750000, 1200000, 1500000])  # Executive outliers
        else:
            base_sal = 45000 + (years_exp * 3200) + random.randint(-5000, 15000)
            salary = round(base_sal, -2)

        # Nullable salary
        if random.random() < 0.08:
            salary = np.nan

        # Constant column: company_name
        company = "Acme Global Solutions Inc."

        # Performance score (1.0 to 5.0)
        perf_score = round(random.uniform(2.5, 5.0), 1) if random.random() > 0.10 else np.nan

        # Remote status
        is_remote = random.choice(["Yes", "No", "yes", "NO", "True"]) if random.random() > 0.05 else np.nan

        data.append({
            "employee_id": emp_id,
            "full_name": f"{first_name} {last_name}",
            "email": email,
            "company_name": company,
            "department": dept,
            "title_level": level,
            "years_experience": years_exp,
            "annual_salary": salary,
            "performance_score": perf_score,
            "is_remote": is_remote,
        })

    df = pd.DataFrame(data)

    # Duplicate 10 rows
    dup_sample = df.sample(10, random_state=seed)
    df = pd.concat([df, dup_sample], ignore_index=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated employee records dataset: {output_path} ({len(df)} rows, {len(df.columns)} cols)")


def generate_clean_baseline(output_path: str, n_rows: int = 400, seed: int = 999):
    """
    Generates a high-quality, pristine tabular dataset without missing values,
    duplicates, or structural defects, for testing near 100% quality scores.
    """
    random.seed(seed)
    np.random.seed(seed)

    cities = ["New York", "San Francisco", "Austin", "Seattle", "Chicago", "Boston"]
    property_types = ["Single Family", "Condo", "Townhouse", "Multi-Family"]

    data = []
    for i in range(1, n_rows + 1):
        prop_id = f"PROP-{50000 + i}"
        city = cities[(i % len(cities))]
        p_type = property_types[(i % len(property_types))]
        bedrooms = random.randint(1, 5)
        bathrooms = round(bedrooms * random.choice([0.75, 1.0, 1.25]), 1)
        sqft = bedrooms * random.randint(450, 750) + random.randint(100, 300)
        price = round(sqft * random.uniform(220, 380), -2)
        year_built = random.randint(1975, 2023)
        has_garage = random.choice([True, False])

        data.append({
            "property_id": prop_id,
            "city": city,
            "property_type": p_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "square_feet": sqft,
            "listing_price": price,
            "year_built": year_built,
            "has_garage": has_garage,
        })

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated clean baseline dataset: {output_path} ({len(df)} rows, {len(df.columns)} cols)")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    generate_dirty_ecommerce(os.path.join(data_dir, "sample_ecommerce_dirty.csv"))
    generate_employee_records(os.path.join(data_dir, "sample_employee_records.csv"))
    generate_clean_baseline(os.path.join(data_dir, "sample_clean_baseline.csv"))
