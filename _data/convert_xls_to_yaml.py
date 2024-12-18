import pandas as pd
import sys
import yaml

excel_file =  sys.argv[1]
##sheet_name =  None  
sheet_name =  'Sheet1'
### out_file =  excel_file + '.yml'

dtype={'year': str, 'assign_date': str}

df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=dtype )
##df = pd.read_excel(excel_file, sheet_name=sheet_name, parse_dates=['assign_date'])
##df['assign_date'] = df['assign_date'].dt.strftime('%Y-%m-%d')
df = df.where(df.notnull(), None)

data_dict = df.to_dict(orient='records')
yaml_str = yaml.dump(data_dict, allow_unicode=True)

print(yaml_str)  

