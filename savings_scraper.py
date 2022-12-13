import gspread
import pandas as pd
import streamlit as st
import random


st.set_page_config(layout="wide")

def return_calc(savings_amt, monthly_max_rate, investment_length, regular_contribution, max_rate_cap):
    global month
    global total_balance  
    for _ in range(int(investment_length)):

        balance = float(total_balance + regular_contribution)
        if balance > max_rate_cap:
            balance_capped = float(max_rate_cap * (1 + (monthly_max_rate/100)))
            difference = balance - max_rate_cap
            balance_over = float(difference * (1 + (0.0055 / 12)))
            balance = balance_capped + balance_over 
            total_balance += round((balance - total_balance), 2) 
        else:
            balance = float(balance * (1 + (monthly_max_rate / 100)))
            total_balance += round((balance - total_balance), 2) 

        month += 1


with st.spinner("Crunching  numbers..."):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open_by_url(st.secrets["savings_spreadsheet"])


    def card(product_name, base_rate, bonus_rate, max_rate, product_link):
        r = lambda: random.randint(150, 255)
        g = lambda: random.randint(150, 255)
        b = lambda: random.randint(136, 255)
        randcolor = ("#%02X%02X%02X" % (r(), g(), b()))
        return f"""
        <div class="col-lg-3 col-md-6 col-sm-12 col-xs-12">
        <div class="example hoverable">
        <div class="card" style="width: 21rem; background-color: {randcolor};">
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
        </div>
        """
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
    """, unsafe_allow_html=True)
    st.markdown("<style>.card:hover{transform: scale(1.001); box-shadow: 0 10px 20px rgba(238,194,128,.33), 0 4px 8px rgba(0,0,0,.06);}</style>", unsafe_allow_html=True)
    st.markdown("<style>.card{width: 100%; height: auto;}</style>", unsafe_allow_html=True)
    st.markdown("<style>.css-1offfwp e16nr0p34{width: 100%;, height: auto;}</style>", unsafe_allow_html=True)
    st.markdown("<style>.col-lg-3 col-md-6 col-sm-12 col-xs-12{width: 100%;, height: auto;}</style>", unsafe_allow_html=True)

    # find the names and id of worksheets if required:
    worksheet_list = sh.worksheets()
    # print(worksheet_list)


    savings_worksheet = sh.get_worksheet(2)




    dataframe = pd.DataFrame(savings_worksheet.get_values())


    with st.sidebar:

        st.markdown("### Calculator")
        month = 0
        total_balance = 0
        mod_df = pd.read_excel("savings_modded.xlsx")
        preset_names = []
        base_rates = []
        bonus_rates= []
        max_rates = []
        min_balances = []
        max_caps = []
        max_balances = []
        for i, row in mod_df.iterrows():
            preset_name = row[1]
            base_rate = row[3]
            bonus_rate = row[4]
            max_rate = row[5]
            min_bal = row[6]
            max_cap = row[7]
            max_bal = row[8]
    
            if "%" in str(base_rate) and "%" in str(bonus_rate) and "%" in str(max_rate) and str(preset_name) != "nan" and str(min_bal) != "nan":
                preset_names.append(str(preset_name))
                base_rates.append(str(base_rate))
                bonus_rates.append(str(bonus_rate))
                max_rates.append(str(max_rate))
                min_balances.append(str(min_bal))
                max_caps.append(str(max_cap))
                max_balances.append(str(max_bal))
            else:
                continue

        record = {
            "name": preset_names,
            "base_rate": base_rates,
            "bonus_rate": bonus_rates,
            "max_rate": max_rates,
            "min_balance": min_balances,
            "max_cap": max_caps,
            "max_balance": max_balances
        }
        preset_df = pd.DataFrame({"name": preset_names,
                                "base_rate": base_rates,
                                "bonus_rate": bonus_rates,
                                "max_rate": max_rates,
                                "min_balance": min_balances,
                                "max_cap": max_caps,
                                "max_balance": max_balances},
                                )
        other_row = {"name": "Other",
                    "base_rate": 0,
                    "bonus_rate": 0,
                    "max_rate": 0,
                    "min_balance": 0,
                    "max_cap": 0,
                    "max_balance": 0,
                    }
        preset_df = preset_df.append(other_row, ignore_index=True)
        # preset_df.to_excel("savings_preset.xlsx")




        preset_selector = st.selectbox("Presets:",
                                    options=(preset_df["name"]),
                                    )
        with st.spinner("Crunching the numbers"):

            with st.form(key="calc_format"):
                
                savings_amt = float(st.number_input("Initial Savings"))
                # cnt = 0
                investment_length = st.number_input(label="Months Saved", value=0, key=f"length")
                regular_contribution = st.number_input(label="Monthly Contribution", value=0, key=f"Cont")


                for i, row in preset_df.iterrows():
                    # cnt += 1
                    cnt = i

                    if row[0] == preset_selector:

                        clean_cap = row[5].split("%")[0]
                        float_cap = float(clean_cap)
                        clean_rate = row[3].split("%")[0]
                        float_rate = float(clean_rate)
                        max_rate_cap = st.number_input(label="Max Rate Cap", value=float_cap, key=f"Cap {cnt}")
                        max_return_rate = st.number_input("Max Return %", value=float_rate, key=f"Rate {cnt}")
                        monthly_max_rate = float(max_return_rate / 12.00)

                        break
                        

                    elif preset_selector == "Other":
                        max_rate_cap = st.number_input(label="Max Rate Cap", value=0, key=f"Cap {cnt}")
                        max_return_rate = st.number_input(label="Max Return %", value=0, key=f"Rate {cnt}")
                        monthly_max_rate = float(max_return_rate / 12.00)

                        break

                    else:
                        continue
                        

                

                total_balance = savings_amt
                submit_button = st.form_submit_button(label="Calculate!", type="secondary")
                with st.spinner("Crunching numbers..."):
                    if submit_button:

                        return_calc(savings_amt=savings_amt, monthly_max_rate=monthly_max_rate, investment_length=investment_length, regular_contribution=regular_contribution, max_rate_cap=max_rate_cap)
                        st.markdown("* * *", unsafe_allow_html=True)
                        
                        if savings_amt <= 0:
                            st.warning("Please add initial savings amount greater than zero to complete the calculation")
                        elif month == 1:
                            st.success(f"After {month} month, your total balance will be ${'{:,.2f}'.format(total_balance)}.")
                        elif month <= 0:
                            st.warning("Please add at least one month to 'Months Saved' to complete the calculation")
                        else:
                            st.success(f"After {month} months, your total balance will be ${'{:,.2f}'.format(total_balance)}.")


            



    st.title("SUPERSAVERS AUS")

    product_name_list = []
    base_rate_list = []
    bonus_rate_list = []
    max_rate_list = []
    product_link_list = []


    def saver_details():

        for i, row in dataframe.iterrows():
            if "%" not in str(row[3]):
                continue
            else:
                product_name = row[1]
                


                product_name_list.append(product_name)

                base_rate = row[3]
                base_rate_list.append(base_rate)
                bonus_rate = row[4]
                bonus_rate_list.append(bonus_rate)
                max_rate = row[5]
                max_rate_list.append(max_rate)
                product_link = row[12]
                product_link_list.append(product_link)
        
    saver_details()


    with st.spinner("Crunching numbers..."):


        t1, t2 = st.tabs(["CARD VIEW", "LIST VIEW"])

        with t1:

            n_cols = 4
            n_rows = int(1 + len(product_name_list) / n_cols)
            rows = [st.columns(n_cols) for _ in range (n_rows)]
            cols = [column for row in rows for column in row]


            for col, product_name, base_rate, bonus_rate, max_rate, product_link in zip(cols, product_name_list, base_rate_list, bonus_rate_list, max_rate_list, product_link_list):
                col.markdown(card(product_name=product_name, base_rate=base_rate, bonus_rate=bonus_rate, max_rate=max_rate, product_link=product_link), unsafe_allow_html=True)


        with t2:
            st.dataframe(dataframe, use_container_width=True)