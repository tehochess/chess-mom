import pandas as pd
import numpy as np

PYTHON = "/c/Users/hesam/AppData/Local/Python/pythoncore-3.14-64/python.exe"

print("=" * 60)
print("LOADING FILES")
print("=" * 60)

menu = pd.read_excel(r'C:\Users\hesam\project\mcdonalds_menu.xlsx')
orders = pd.read_excel(r'C:\Users\hesam\project\mcdonalds_orders.xlsx')

# ============================================================
print("\n" + "=" * 60)
print("MENU FILE - STRUCTURE")
print("=" * 60)
print(f"Shape: {menu.shape[0]} rows x {menu.shape[1]} columns")
print(f"Columns: {list(menu.columns)}")
print(f"\nData types:\n{menu.dtypes}")
print(f"\nNull counts:\n{menu.isnull().sum()}")
print(f"\nSample data (first 5 rows):\n{menu.head().to_string()}")

# ============================================================
print("\n" + "=" * 60)
print("ORDERS FILE - STRUCTURE")
print("=" * 60)
print(f"Shape: {orders.shape[0]} rows x {orders.shape[1]} columns")
print(f"Columns: {list(orders.columns)}")
print(f"\nData types:\n{orders.dtypes}")
print(f"\nNull counts:\n{orders.isnull().sum()}")
print(f"\nSample data (first 5 rows):\n{orders.head().to_string()}")

# ============================================================
print("\n" + "=" * 60)
print("MENU ANALYSIS")
print("=" * 60)

# Categories
cat_col = None
for c in menu.columns:
    if 'categ' in c.lower():
        cat_col = c
        break
if cat_col:
    print(f"\nCategories (column: '{cat_col}'):")
    print(menu[cat_col].value_counts().to_string())
else:
    print("No category column detected. Checking all string columns:")
    for c in menu.select_dtypes(include='object').columns:
        nuniq = menu[c].nunique()
        if 2 <= nuniq <= 30:
            print(f"  Potential category col '{c}': {nuniq} unique values")
            print(f"  Values: {list(menu[c].unique())[:20]}")

# Price
price_col = None
for c in menu.columns:
    if 'price' in c.lower():
        price_col = c
        break
if price_col:
    print(f"\nPrice analysis (column: '{price_col}'):")
    print(f"  Min: ${menu[price_col].min():.2f}")
    print(f"  Max: ${menu[price_col].max():.2f}")
    print(f"  Mean: ${menu[price_col].mean():.2f}")
    print(f"  Median: ${menu[price_col].median():.2f}")
    print(f"  Std: ${menu[price_col].std():.2f}")
    if cat_col:
        print(f"\nAverage price by category:")
        print(menu.groupby(cat_col)[price_col].mean().sort_values(ascending=False).to_string())
else:
    print("\nNo price column detected. Numeric columns:")
    print(menu.describe().to_string())

# Nutritional info
nutri_keywords = ['calorie', 'cal', 'fat', 'carb', 'protein', 'sodium', 'sugar', 'fiber', 'nutri']
nutri_cols = [c for c in menu.columns if any(k in c.lower() for k in nutri_keywords)]
if nutri_cols:
    print(f"\nNutritional columns found: {nutri_cols}")
    print(menu[nutri_cols].describe().to_string())
else:
    print("\nNo obvious nutritional columns. All numeric columns:")
    print(menu.select_dtypes(include=[np.number]).describe().to_string())

# Menu items
item_col = None
for c in menu.columns:
    if any(k in c.lower() for k in ['item', 'name', 'product', 'menu']):
        item_col = c
        break
if item_col:
    print(f"\nTotal menu items: {menu[item_col].nunique()}")
    print(f"Sample items: {list(menu[item_col].head(10))}")

# ============================================================
print("\n" + "=" * 60)
print("ORDERS ANALYSIS")
print("=" * 60)

# Date range
date_col = None
for c in orders.columns:
    if any(k in c.lower() for k in ['date', 'time', 'order_date', 'timestamp']):
        date_col = c
        break
if date_col:
    try:
        orders[date_col] = pd.to_datetime(orders[date_col])
        print(f"\nDate range (column: '{date_col}'):")
        print(f"  From: {orders[date_col].min()}")
        print(f"  To:   {orders[date_col].max()}")
        print(f"  Span: {(orders[date_col].max() - orders[date_col].min()).days} days")
        print(f"\nOrders by month:")
        print(orders[date_col].dt.to_period('M').value_counts().sort_index().to_string())
        print(f"\nOrders by day of week:")
        dow = orders[date_col].dt.day_name().value_counts()
        print(dow.to_string())
    except Exception as e:
        print(f"  Could not parse dates: {e}")
else:
    print("No date column detected.")

# Customer info
cust_cols = [c for c in orders.columns if any(k in c.lower() for k in ['customer', 'cust', 'client', 'user', 'name', 'id'])]
if cust_cols:
    print(f"\nCustomer-related columns: {cust_cols}")
    for c in cust_cols:
        print(f"  '{c}': {orders[c].nunique()} unique values, sample: {list(orders[c].dropna().unique()[:5])}")

# Order/quantity columns
qty_col = None
for c in orders.columns:
    if any(k in c.lower() for k in ['qty', 'quantity', 'count', 'amount']):
        qty_col = c
        break

# Revenue
rev_col = None
for c in orders.columns:
    if any(k in c.lower() for k in ['revenue', 'total', 'price', 'amount', 'sales', 'cost']):
        rev_col = c
        break

if rev_col:
    print(f"\nRevenue analysis (column: '{rev_col}'):")
    print(f"  Total: ${orders[rev_col].sum():,.2f}")
    print(f"  Mean per order: ${orders[rev_col].mean():.2f}")
    print(f"  Median: ${orders[rev_col].median():.2f}")
    print(f"  Min: ${orders[rev_col].min():.2f}")
    print(f"  Max: ${orders[rev_col].max():.2f}")

# Popular items
item_in_orders = None
for c in orders.columns:
    if any(k in c.lower() for k in ['item', 'product', 'name', 'menu']):
        item_in_orders = c
        break
if item_in_orders:
    print(f"\nTop 15 most ordered items (column: '{item_in_orders}'):")
    if qty_col:
        top_items = orders.groupby(item_in_orders)[qty_col].sum().sort_values(ascending=False).head(15)
    else:
        top_items = orders[item_in_orders].value_counts().head(15)
    print(top_items.to_string())

    if rev_col:
        print(f"\nTop 15 items by revenue:")
        top_rev = orders.groupby(item_in_orders)[rev_col].sum().sort_values(ascending=False).head(15)
        print(top_rev.to_string())

# Order ID
order_id_col = None
for c in orders.columns:
    if any(k in c.lower() for k in ['order_id', 'orderid', 'order id']):
        order_id_col = c
        break
if order_id_col:
    print(f"\nTotal unique orders: {orders[order_id_col].nunique()}")
    print(f"Total order rows: {len(orders)}")
    avg_items = len(orders) / orders[order_id_col].nunique()
    print(f"Average items per order: {avg_items:.2f}")

# Show all numeric stats for orders
print(f"\nAll numeric columns stats:")
print(orders.describe().to_string())

# ============================================================
print("\n" + "=" * 60)
print("RELATIONSHIP ANALYSIS (Menu <-> Orders)")
print("=" * 60)

# Try to find common join keys
menu_cols_lower = {c.lower(): c for c in menu.columns}
orders_cols_lower = {c.lower(): c for c in orders.columns}
common_keys = set(menu_cols_lower.keys()) & set(orders_cols_lower.keys())
print(f"Common column names: {common_keys}")

# Check if item names match
if item_col and item_in_orders:
    menu_items_set = set(menu[item_col].dropna().str.strip().str.lower())
    orders_items_set = set(orders[item_in_orders].dropna().str.strip().str.lower())
    matched = menu_items_set & orders_items_set
    only_in_menu = menu_items_set - orders_items_set
    only_in_orders = orders_items_set - menu_items_set
    print(f"\nItem matching between menu and orders:")
    print(f"  Menu items: {len(menu_items_set)}")
    print(f"  Unique items in orders: {len(orders_items_set)}")
    print(f"  Items in BOTH: {len(matched)}")
    print(f"  Items ONLY in menu (never ordered): {len(only_in_menu)}")
    if only_in_menu:
        print(f"    Examples: {list(only_in_menu)[:10]}")
    print(f"  Items ONLY in orders (not in menu): {len(only_in_orders)}")
    if only_in_orders:
        print(f"    Examples: {list(only_in_orders)[:10]}")

# ============================================================
print("\n" + "=" * 60)
print("INTERESTING INSIGHTS & ANOMALIES")
print("=" * 60)

# Duplicate rows
print(f"\nMenu duplicate rows: {menu.duplicated().sum()}")
print(f"Orders duplicate rows: {orders.duplicated().sum()}")

# Negative or zero values
if price_col:
    neg_price = menu[menu[price_col] <= 0]
    if len(neg_price) > 0:
        print(f"\nWARNING: {len(neg_price)} menu items with zero or negative price!")
        print(neg_price.to_string())

if rev_col:
    neg_rev = orders[orders[rev_col] < 0]
    if len(neg_rev) > 0:
        print(f"\nWARNING: {len(neg_rev)} orders with negative revenue (possible refunds?)!")
        print(neg_rev.head().to_string())

# Price mismatches if we can join
if item_col and item_in_orders and price_col and rev_col:
    # Try to merge
    menu_prices = menu[[item_col, price_col]].copy()
    menu_prices.columns = ['item_key', 'menu_price']
    menu_prices['item_key'] = menu_prices['item_key'].str.strip().str.lower()
    orders_merged = orders.copy()
    orders_merged['item_key'] = orders_merged[item_in_orders].str.strip().str.lower()
    merged = orders_merged.merge(menu_prices, on='item_key', how='inner')
    if len(merged) > 0:
        print(f"\nSuccessfully joined {len(merged)} order rows with menu prices.")
        if qty_col:
            merged['expected_total'] = merged['menu_price'] * merged[qty_col]
            merged['price_diff'] = (merged[rev_col] - merged['expected_total']).abs()
            high_diff = merged[merged['price_diff'] > 0.01]
            print(f"Orders where order price != menu price * qty: {len(high_diff)}")
            if len(high_diff) > 0:
                print(high_diff[['item_key', rev_col, 'menu_price', qty_col, 'expected_total', 'price_diff']].head(10).to_string())

# Most expensive vs least expensive
if price_col and item_col:
    print(f"\nTop 5 most expensive items:")
    print(menu.nlargest(5, price_col)[[item_col, price_col]].to_string())
    print(f"\nTop 5 cheapest items:")
    print(menu.nsmallest(5, price_col)[[item_col, price_col]].to_string())

# Category revenue
if item_in_orders and rev_col and cat_col and item_col:
    cat_map = menu.set_index(item_col)[cat_col].to_dict()
    orders['category'] = orders[item_in_orders].map(cat_map)
    cat_revenue = orders.groupby('category')[rev_col].sum().sort_values(ascending=False)
    print(f"\nRevenue by category:")
    print(cat_revenue.to_string())

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
