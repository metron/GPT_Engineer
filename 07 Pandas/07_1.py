import pandas as pd

ser = pd.Series([1, 2, 3])
df = pd.DataFrame({
    "col_name": [1, None, 3]
})
print(ser)
print(df)
