import pandas as pd
from IPython.display import display

all_df = pd.DataFrame()

path = 'data/'
import os

for file in os.listdir(path):
    if file.endswith('.csv'):
        print(file)
        df = pd.read_csv(os.path.join(path, file))
        df['term'] = file.split('_')[1]
        df['year'] = file.split('_')[2]
        all_df = pd.concat([all_df, df], ignore_index=True)

# Filter for sections no ending with a number
all_df = all_df[~all_df['section'].str.contains(r'\d$', na=False)]

display(all_df[(all_df['course_code'] == 'MATH 6121')])

all_df['term_year'] = all_df['term'].astype(str) + all_df['year'].astype(str)

def translate_terms(terms):
    # take array([202408, 202208, 202108, 202008, 202308]) and return f"Fall {x // 100}" or f"Spring {x // 100}"
    return [f"Fall {x // 100}" if x % 100 == 8 else f"Spring {x // 100}" for x in terms]

def syntactic_join(lst):
    if not lst.any() or len(lst) == 0:
        return " "
    if len(lst) == 1:
        return str(lst[0])
    return ", ".join(str(item) for item in lst[:-1]) + ", and " + str(lst[-1])

in_file_path = 'data2/gt_math_courses.csv'
out_file_path = 'data2/gt_math_courses.csv'
math_courses_df = pd.read_csv(in_file_path)
math_courses_df['course_code'] = math_courses_df['title'].str.split('-').str[0].str.strip()
math_courses_df['terms'] = math_courses_df['course_code'].apply(lambda x: all_df[all_df['course_code'] == x].sort_values(['year', 'term'])['term_year'].unique()[-5:][::-1])
math_courses_df['professors'] = math_courses_df['course_code'].apply(lambda x: all_df[all_df['course_code'] == x].sort_values(['year', 'term'])['instructor'].apply(lambda y: y.split(',')[0].strip() if pd.notna(y) else '').unique()[-5:][::-1])

math_courses_df['terms_str'] = math_courses_df['terms'].apply(lambda x: syntactic_join(x))
math_courses_df['professors_str'] = math_courses_df['professors'].apply(lambda x:  syntactic_join(x))
import re
math_courses_df['professors_str'] = math_courses_df['professors_str'].apply(lambda x: re.sub(r'\s+', ' ', x.replace('\n', ' ')).strip())
math_courses_df['terms_str'] = math_courses_df['terms_str'].apply(lambda x: re.sub(r'\s+', ' ', x.replace('\n', ' ')).strip())  
math_courses_df['professors_str'] = math_courses_df['professors_str'].str.replace('\n', ' ')
math_courses_df['terms_str'] = math_courses_df['terms_str'].str.replace('\n', ' ')

print(repr(math_courses_df[math_courses_df['course_code'] == 'MATH 2550']['professors_str'].iloc[0]))
print(math_courses_df[math_courses_df['course_code'] == 'MATH 2550']['professors_str'].iloc[0])

math_courses_df.to_csv(out_file_path, index=False)
