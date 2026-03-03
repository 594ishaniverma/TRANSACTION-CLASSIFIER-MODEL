import pandas as pd
import numpy as np 
from sklearn.preprocessing import LabelEncoder
import re

#loading the csv file
#assuming the file is named 'Bank_statements.csv'
df=pd.read_csv('Bank_statements.csv')
#displaying the first few rows of the dataframe
print(df.head())
#knowing about the datatypes of the columns
print(df.dtypes)
#checking for duplicates
print(df.duplicated().sum())
#no duplicate value is there in the dataset
#checking for missing values
print(df.isnull().sum())
#since the missing value is of type object, we can fill it with a placeholder such as 'Unknown'
df['Merchant']=df['Merchant'].fillna('Unknown')
print(df.isnull().sum()) # Verifying that there are no more missing values
#converting the 'Date' column to datetime format 
#since the date in the csv file is in 'dd/mm/yyyy' format
df['DATE'] = pd.to_datetime(df['DATE'],format='mixed', errors='coerce')
#displaying the first few rows after conversion 
print(df.head())
print(df.tail())
#checking the data types again to confirm the conversion   
print(df.dtypes)
print(df.isnull().sum())
#filling missing values in the 'DATE' column with a placeholder date, here we use '2025-01-01'
df['DATE']=df['DATE'].fillna(pd.Timestamp("2025-01-01"))
print(df.isnull().sum())

#converting the 'AMOUNT' column to numeric, handling errors by coercing them to NaN
df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')
#checking the data types again to confirm the conversion
print(df.dtypes)
#standardizing the 'Merchant' column by converting it to lowercase
df['Merchant'] = df['Merchant'].str.lower()
#removing any leading or trailing whitespace from the 'Merchant' column
df['Merchant'] = df['Merchant'].str.strip()
#removing multiple in-word spaces in the 'Merchant' column
df['Merchant'] = df['Merchant'].str.replace(r'\s+', ' ', regex=True)
#displaying the first few rows after standardization   
print(df.head())
# Standardize the capitalization of the 'TRANSACTION TYPE' column by converting to lowercase
df['TRANSACTION TYPE'] = df['TRANSACTION TYPE'].str.lower()
#standardizing the 'DESCRIPTION' column by converting it to lowercase
df['DESCRIPTION'] = df['DESCRIPTION'].str.lower()
#removing any leading or trailing whitespace from the 'DESCRIPTION' column
df['DESCRIPTION'] = df['DESCRIPTION'].str.strip()   
#removing multiple in-word spaces in the 'DESCRIPTION' column 
df['DESCRIPTION'] = df['DESCRIPTION'].str.replace(r'\s+', ' ', regex=True)
#removing special characters from the 'DESCRIPTION' column
df['DESCRIPTION'] = df['DESCRIPTION'].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
#extracting reference numbers from the 'DESCRIPTION' column using regex
def extract_ref_no(DESCRIPTION):
    # This regex looks for digits that come after 'Refno' or 'Ref:'or"Ref No" or "Transaction ID:" or "Transaction"

    # It captures the digits that follow these keywords.
    # The 're.IGNORECASE' flag makes the search case-insensitive.
    # The '|' operator acts as an OR condition between different patterns.
    # The pattern '\d+' matches one or more digits.
    match = re.search(r'Refno\s*(\d+)|Ref:\s*(\d+)|Ref No\s*(\d+)|Transaction ID:\s*(\d+)|Transaction\s*(\d+)', DESCRIPTION, re.IGNORECASE)
    if match:
        # Return the first group that has a match
        return match.group(1) or match.group(2) or match.group(3) or match.group(4) or match.group(5)
    return None

# Apply the function to the 'Description' column
df['Reference_Number'] = df['DESCRIPTION'].apply(extract_ref_no)

# Display the new column to verify
print(df[['DESCRIPTION', 'Reference_Number']].head(10))
#filling NaN values in the 'Reference_Number' column with '515394903436'
df['Reference_Number'] = df['Reference_Number'].fillna('515394903436')
print(df[['DESCRIPTION', 'Reference_Number']].head(10))
#Feature enginnering 
df["Year"]=df["DATE"].dt.year
df["Month"]=df["DATE"].dt.month
df["Day"]=df["DATE"].dt.day
print(df.head())
#fearture engineering for categorization of merchants
# Define the category mapping based on the unique merchant list
category_mapping = {
    'Food & Dining': ['zomato','kfc' ,'swiggy', 'dominos', 'food court', 'gupta cafe', 'thakur confectio'],
    'Shopping': ['amazon', 'myntra', 'flipkart', 'paytm mall', 'jio mart', 'big bazaar', "spencer's", 'reliance fresh', 'nykaa', 'jk readymade ga'],
    'Bills & Utilities': ['jio','vi recharge' ,'jio recharge', 'mobile bill', 'internet bill', 'water bill', 'gas agency','google india digital services pvt ltd', 'electricity bill', 'electricity', 'broadband', 'postpaid','jioin app direct','google india dig'],
    'Groceries': ['grocery','reliance retail', 'd-mart', 'nature basket', 'more super market', 'star bazaar', 'bigbasket'],
    'Fuel & Transportation': ['petrol pump', 'fuel', 'indian oil', 'bharat petroleum', 'hpcl', 'shell', 'esso'],
    'Transportation': ['uber', 'ola', 'rapido'],
    'Entertainment': ['netflix', 'spotify', 'prime video', 'hotstar', 'bookmyshow', 'mx player', 'zee5','spotify india pvt ltd', 'google play music', 'google youtube music', 'google youtube prem' ,'youtube premium','youtube music'],
    'Income': ['salary','govt subsidy','freelance' ,'credit interest', 'interest','bonus','cashback', 'refund', 'dividend', 'upi', 'neft', 'imps', 'rtgs'],
    'Education': ['unacademy', 'udemy','byjus', 'upgrad', 'coursera', 'edx'],
    'Health & Wellness': ['practo','medplus', '1mg', 'pharmacy', 'medlife','pharmeasy'],
    'Travel': ['make my trip', 'goibibo', 'redbus', 'yatra'],
    'Gifts & Donations': ['donation', 'charity'], 
    'Financial': ['loan', 'credit card payment', 'refund', 'dividend', 'getepay', 'airtel payments bank', 'flipkart payments'],
    'Rent': ['rent', 'pg rent', 'rent transfer'],
    'Personal & Others': ['diwan chand', 'rohit kumar', 'sidarth sharma', 'shivam choudhary', 'pranav sharma', 'kanan verma', 'ishani verma', 'suraj sharma', 'sunil kumar', 'om prakash', 'arun kumar', 'raj kumar so hukam singh', 'sahil', 'unknown', 'ujjwal katoch', 'nikhil bhardwaj', 'vinod kumar s o', 'mrs bhavana dev', 'sharma shudh vai', 'ravi kumar', 'ravinder prakash', 'shrestha thakur', 'jagdish ram and', 'piyush sharma', 'guru prashad so', 'rahul thakur', 'narender kumar', 'mahender pal', 'rashmi rana', 'rahul mehta']
}
# Create a categorization function
def categorize_merchant(merchant):
    # Iterate through the category mapping to find a match
    for category, keywords in category_mapping.items():
        for keyword in keywords:
            if keyword in merchant:
                return category
    return 'Other'
#hlo so is the above logic is ready 
# Apply the function to create the new 'Category' column
df['Category'] = df['Merchant'].apply(categorize_merchant)


# Print the value counts for the new 'Category' column
print("Breakdown of transactions by the new category:")
print(df['Category'].value_counts())







#removal of stopwords ,special characters,text standardisation of description column

# creating a signed_amount column positive for credit and negative for debit
df['Signed Amount'] = np.where(df['TRANSACTION TYPE'] == 'credited', df['AMOUNT'], -df['AMOUNT'])
#checking the dataframe after adding the signed amount column
print(df.head())




# label encoding the transaction type column 
# label encoder is a good way for this because it has just two things credited and debited 
le=LabelEncoder()
df["Transaction Type Encoded "]=le.fit_transform(df["TRANSACTION TYPE"])
# I AM making a new columnn for the transacation type encode while keeping the transaction type also in the dataset 
print(df.head())



#for converting the text description into vectors
 
from sklearn.feature_extraction.text import TfidfVectorizer
#this tfidfvectorizer will help in converting the text data into numerical format
import joblib
#for dumping the pickle file for future use 
#term frequency-inverse document frequency is what tfidf stands for 
# Initialize the TF-IDF Vectorizer
# I'll use stop_words='english' to remove common English words that don't add much value.
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
#this above  is the initialization of the tfidf vectorizer
#that is the above will contain the list of stop words


# Fit and transform the 'DESCRIPTION' column
tfidf_matrix = tfidf_vectorizer.fit_transform(df['DESCRIPTION'])

# Print the shape of the resulting matrix
print(f"Shape of the TF-IDF matrix: {tfidf_matrix.shape}")
# Save the TF-IDF matrix and the vectorizer object
np.savez_compressed('tfidf_matrix.npz', data=tfidf_matrix.data, indices=tfidf_matrix.indices, indptr=tfidf_matrix.indptr, shape=tfidf_matrix.shape)
joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.pkl')#storing the stopwords in the pkl file for the future refernce 

print("TF-IDF matrix saved to 'tfidf_matrix.npz'")#.npz is the compressed file format for storign the numpy arrays and matrices in a zipped format
print("TF-IDF vectorizer object saved to 'tfidf_vectorizer.pkl'")#this pkl that is pickle file  are used to store the python objects and we can use them in the future as they are working before

df.to_csv("Preprocessed bank statements.csv",index=False)#the index=False is there because it will not store index column 
# now we will  fit our model


   


