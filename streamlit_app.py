# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruit you want in your custom smoothie!")

# Name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit table
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(
    col("FRUIT_NAME"), 
    col("SEARCH_ON")
)

# Convert to pandas for searching
pd_df = my_dataframe.to_pandas()

# Ingredient selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

my_insert_stmt = ""

# Handle ingredient logic
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Find the value in SEARCH_ON column
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, 
            "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for", fruit_chosen, "is", search_on)

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API call using SEARCH_ON value
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Build SQL INSERT statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

# Submit button
time_to_insert = st.button("Submit Order")

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered!", icon="✅")
