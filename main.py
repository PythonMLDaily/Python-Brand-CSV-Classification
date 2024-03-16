import pandas
import json


def get_brand_details(details, brand):
    json_details = json.loads(details)

    # Check if the details are in a list
    if len(json_details) > 1:
        # Loop through the list of details
        for details in json_details:
            try:
                if len(details) == 0:
                    return 'N/A'
                # Check if the brand is in the details
                if details['brand'] == brand:
                    return details['details']
            except:
                error_lines['multi-details'] += 1
                print('Error multi-details: ', details, brand)
    else:
        # Brand is not a list, so we can just check if the brand is in the details
        try:
            if json_details[0]['brand'] == brand:
                return json_details[0]['details']
        except:
            error_lines['single-details'] += 1
            print('Error single-details: ', json_details, brand)
    return 'N/A'


def get_brand_classification(classification, brand):
    json_classification = json.loads(classification)

    # Check if the classification is keyed by 'brands' or not
    if 'brands' in json_classification:
        json_classification = json_classification['brands']

    # Check if the classification a list of classifications and there's more than one
    if type(json_classification) is list and len(json_classification) > 1:
        for classification in json_classification:
            try:
                if classification['brand'] == brand:
                    return classification['category']
            except:
                error_lines['multi-classification'] += 1
                print('Error multi classification: ', classification, brand)
    else:
        try:
            # Check if the classification is a list, then get the first item
            if type(json_classification) is list:
                json_classification = json_classification[0]

            # Check if the brand is in the classification
            # or if the brand is the classification
            # (e.g. 'brand': {'category': []} or ['brand': 'brand', 'category': 'category'])
            if json_classification['brand'] == brand or brand in json_classification:
                return json_classification['category']
        except:
            error_lines['single-classification'] += 1
            print('Error single classification: ', json_classification, brand)
            print(json_classification.keys(), brand)
    return 'N/A'


df = pandas.read_csv('data/articles.csv')

output = [
    [
        'Brand',  # Brand name
        'Classification',  # Category of each row
        'Details',  # All other details in the row
    ]
]

error_lines = {
    'single-details': 0,
    'multi-details': 0,
    'single-classification': 0,
    'multi-classification': 0,
}

lines = 0

for index, row in df.iterrows():
    row_brands = json.loads(row['brand'])['brand']
    if len(row_brands) > 1:
        for row_brand in row_brands:
            lines += 1
            if row_brand == 'N/A':  # Skip N/A brands
                continue
            brand_classification = get_brand_classification(row['classification'], row_brand)
            brand_details = get_brand_details(row['details'], row_brand)
            if brand_classification == 'N/A' or brand_details == 'N/A':  # Skip rows with no classification or details
                continue
            output.append([
                row_brand,
                brand_classification,
                brand_details,
            ])
    else:
        lines += 1
        if row_brands[0] == 'N/A':  # Skip N/A brands
            continue
        brand_classification = get_brand_classification(row['classification'], row_brands[0])
        brand_details = get_brand_details(row['details'], row_brands[0])
        if brand_classification == 'N/A' or brand_details == 'N/A':  # Skip rows with no classification or details
            continue
        output.append([
            row_brands[0],
            brand_classification,
            brand_details,
        ])

imported = len(output) - 1

print("=" * 50)

print('Initial CSV size:', df.shape[0], 'lines')
print('Imported:', imported, ' brands of potential', lines)

print("Error lines count:")
print(error_lines)

newdf = pandas.DataFrame(output)
newdf.to_csv('data/output.csv', header=df.get(0))
