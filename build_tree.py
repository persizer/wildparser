import json

def build_tree(data):
    tree = {}
    for item in data:
        main_category = item["main_category"]
        sub_category = item["sub_category"]

        if main_category not in tree:
            tree[main_category] = set()

        tree[main_category].add(sub_category)

    # Convert sets to lists
    for main_category, subcategories in tree.items():
        tree[main_category] = list(subcategories)
        
    return tree

def main():
    # Specify the input and output file paths
    input_json_file_path = 'categories.json'
    output_json_file_path = 'categories1.json'

    # Read the contents of the input JSON file
    with open(input_json_file_path, 'r', encoding='utf-8') as file:
        json_data = file.read()

    # Parse JSON
    data = json.loads(json_data)["data"]

    # Build the tree
    tree = build_tree(data)

    # Display the tree
    print(json.dumps(tree, indent=2, ensure_ascii=False))

    # Save the result to the output JSON file
    with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(tree, output_file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
