import pandas as pd

# Load your processed dataset (update the path if needed)
df = pd.read_csv("../data/preprocessed_60000.csv")

def search_keyword(keyword):
    # Search inside ingredient tokens OR title OR steps
    mask = (
        df["name"].str.contains(keyword, case=False, na=False) |
        df["ingredients_tokens"].astype(str).str.contains(keyword, case=False, na=False) |
        df["steps_tokens"].astype(str).str.contains(keyword, case=False, na=False)
    )
    results = df[mask]
    return results[["id", "name"]]

print("=== Manual Ground Truth Helper ===")
print("Type a keyword (e.g., 'spinach') to see relevant recipes.")
print("Use this to pick correct relevant_ids for eval_queries.json")
print("Type 'exit' to stop.\n")

while True:
    q = input("Enter keyword: ").strip()
    if q.lower() == "exit":
        break
    matches = search_keyword(q)
    if matches.empty:
        print("No matches found.\n")
    else:
        print(matches.head(20))
        print("\nPick IDs from this list that are truly relevant.\n")
