import pandas as pd
from thefuzz import fuzz

def find_best_match(bank_statement, reconciliation_csv):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(reconciliation_csv)
   
    # Extract statement details
    statement_name = bank_statement['Name']
    statement_reference = bank_statement['Reference']
    statement_date = bank_statement['Date']
    statement_amount = float(bank_statement['Amount'].replace(",", "").replace("(", "-").replace(")", ""))

    # Step 2: Match the name
    df['Name_Score'] = df['Name'].apply(lambda x: fuzz.partial_ratio(statement_name, x))
    matched_names = df[df['Name_Score'] > 90]
   
    if not matched_names.empty:
        if len(matched_names) == 1:
            # Single match found by name
            return matched_names[['Name', 'Reference', 'Amount']].iloc[0].to_dict()
        else:
            # Multiple matches found by name
            matched_names['Amount_Score'] = matched_names['Amount'].apply(lambda x: fuzz.ratio(str(statement_amount), str(x)))
            best_name_match = matched_names.loc[matched_names['Amount_Score'].idxmax()]
            if best_name_match['Amount_Score'] == 100:
                return best_name_match[['Name', 'Reference', 'Amount']].to_dict()
            else:
                total_amount = matched_names['Amount'].apply(lambda x: abs(float(x.replace(",", "").replace("(", "-").replace(")", "")))).sum()
                if total_amount == statement_amount:
                    return matched_names[['Name', 'Reference', 'Amount']].to_dict()
   
    # Step 3: Match the reference
    df['Reference_Score'] = df['Reference'].apply(lambda x: fuzz.partial_ratio(statement_reference, x))
    matched_references = df[df['Reference_Score'] > 90]
   
    if not matched_references.empty:
        if len(matched_references) == 1:
            # Single match found by reference
            return matched_references[['Name', 'Reference', 'Amount']].iloc[0].to_dict()
        else:
            # Multiple matches found by reference
            matched_references['Amount_Score'] = matched_references['Amount'].apply(lambda x: fuzz.ratio(str(statement_amount), str(x)))
            best_reference_match = matched_references.loc[matched_references['Amount_Score'].idxmax()]
            if best_reference_match['Amount_Score'] == 100:
                return best_reference_match[['Name', 'Reference', 'Amount']].to_dict()
            else:
                total_amount = matched_references['Amount'].apply(lambda x: abs(float(x.replace(",", "").replace("(", "-").replace(")", "")))).sum()
                if total_amount == statement_amount:
                    return matched_references[['Name', 'Reference', 'Amount']].to_dict()
   
    return None

# Define a function to convert CSV items to a dictionary
def convert_csv_to_dict(csv_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Convert the DataFrame to a list of dictionaries
    dict_list = df.to_dict('records')

    # Convert the 'Amount' field to string and format it
    for item in dict_list:
        item['Amount'] = "{:,.2f}".format(item['Amount'])

    return dict_list


# Define the CSV file path
csv_file = "Bank_Statements.csv"
reconciliation_csv = 'Bank_Reconciliation.csv'

# Convert Bank_Statement.csv into DF
statement_df = pd.read_csv(csv_file)

# Call the function to convert the CSV items to dictionaries
bank_statements = convert_csv_to_dict(csv_file)

match = []
for bank_statement in bank_statements:
    result = find_best_match(bank_statement, reconciliation_csv)
    print(result)
    match.append(result)


match_df = pd.DataFrame(match)
print(match_df)

output_df = pd.concat([statement_df, match_df], axis=1)
output_df.columns.values[4] = "Results"
output_df.to_csv('output.csv', index=False)
