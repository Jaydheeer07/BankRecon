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
            return matched_names[['Name', 'Amount']].iloc[0].to_dict()
        else:
            # Multiple matches found by name
            matched_names['Amount_Score'] = matched_names['Amount'].apply(lambda x: fuzz.ratio(str(statement_amount), str(x)))
            best_name_match = matched_names.loc[matched_names['Amount_Score'].idxmax()]
            if best_name_match['Amount_Score'] == 100:
                return best_name_match[['Name', 'Amount']].to_dict()
            else:
                total_amount = matched_names['Amount'].apply(lambda x: abs(float(x.replace(",", "").replace("(", "-").replace(")", "")))).sum()
                if total_amount == statement_amount:
                    return matched_names[['Name', 'Amount']].to_dict()
   
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

# Example usage
bank_statement = {
    'Name': 'SMART',
    'Reference': '',
    'Date': 'May 28, 2024',
    'Amount': '4,500.00'
}
reconciliation_csv = 'Bank_Reconciliation.csv'

result = find_best_match(bank_statement, reconciliation_csv)
print(result)