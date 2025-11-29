# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(""" choose the fruit you want in your custom smoothie! """)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
                      .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Show Snowpark dataframe
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Let user pick ingredients
ingredients_list = st.multiselect(
    "choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

my_insert_stmt = ''

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Find the correct API search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Call API using the SEARCH_ON value
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)

    # Build SQL insert
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

# Submit button
time_to_insert = st.button('submit order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
