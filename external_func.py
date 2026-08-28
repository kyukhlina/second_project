def columns_formating(df: pd.Series) -> pd.Series:
    df.columns = [(column.lower()).replace(" ","_") for column in df.columns]  
    return df