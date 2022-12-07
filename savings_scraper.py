import gspread
import pandas as pd
import streamlit as st
import random


st.set_page_config(layout="wide")


gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
sh = gc.open_by_url(st.secrets["savings_spreadsheet"])


def card(product_name, base_rate, bonus_rate, max_rate, product_link):
    r = lambda: random.randint(150, 255)
    g = lambda: random.randint(150, 255)
    b = lambda: random.randint(136, 255)
    randcolor = ("#%02X%02X%02X" % (r(), g(), b()))
    # annotated_tuple = (i["text"], str(i["start"]), randcolor)
    return f"""
    <div class="example hoverable">
    <div class="card" style="width: 25rem; background-color: {randcolor};">
        <div class="card-body">
            <h6 class="card-title"><strong>{product_name}</strong></h6>
            <h6 class="card-subtitle mb-2 text-muted"><strong>Max Rate: {max_rate}</strong></h6>
            <p class="card-text">Bonus rate: {bonus_rate}</p>
            <p class="card-text">Base rate: {base_rate}</p>
            <a href="{product_link}" class="btn btn-outline-dark
            " role="button" aria-pressed="true">Open Account</a>
        </div>
    </div>
    </div>
    """
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
""", unsafe_allow_html=True)
st.markdown("<style>.card:hover{transform: scale(1.001); box-shadow: 0 10px 20px rgba(238,194,128,.33), 0 4px 8px rgba(0,0,0,.06);}</style>", unsafe_allow_html=True)

# find the names and id of worksheets if required:
worksheet_list = sh.worksheets()
print(worksheet_list)


savings_worksheet = sh.get_worksheet(2)
# print(savings_worksheet)
# print(savings_worksheet.row_values(5))



dataframe = pd.DataFrame(savings_worksheet.get_values())
# print(dataframe.head())

# dataframe.to_excel('savings.xlsx')


st.title("SUPERSAVERS AUS")

product_name_list = []
base_rate_list = []
bonus_rate_list = []
max_rate_list = []
product_link_list = []

for i, row in dataframe.iterrows():
    if "%" not in str(row[3]):
        continue
    else:
        product_name = row[1]
        
        # print(product_name)


        product_name_list.append(product_name)

        base_rate = row[3]
        base_rate_list.append(base_rate)
        bonus_rate = row[4]
        bonus_rate_list.append(bonus_rate)
        max_rate = row[5]
        max_rate_list.append(max_rate)
        product_link = row[12]
        product_link_list.append(product_link)
    


n_cols = 4
n_rows = int(1 + len(product_name_list) / n_cols)
rows = [st.columns(n_cols) for _ in range (n_rows)]
cols = [column for row in rows for column in row]

for col, product_name, base_rate, bonus_rate, max_rate, product_link in zip(cols, product_name_list, base_rate_list, bonus_rate_list, max_rate_list, product_link_list):
    col.markdown(card(product_name=product_name, base_rate=base_rate, bonus_rate=bonus_rate, max_rate=max_rate, product_link=product_link), unsafe_allow_html=True)
