# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Crear sesión con Snowflake
session = Session.builder.configs(connection_parameters).create()

# Write directly to the app
st.title(" :cup_with_straw: Cusomize your Smoothies :cup_with_straw:")
st.write(
    "Choose the fruit you want in your custom Smoothie!"
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session() #get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' ' # ' += ' add this to what is already in the variable
        
    #The st.write() command should be part of the IF block but not part of the FOR Loop.
    #You can try it as part of the FOR Loop and see an interesting result

    #st.write(ingredients_string)
    

    my_insert_stmt = """insert into smoothies.public.orders (ingredients, NAME_ON_ORDER)
                        values ('""" + ingredients_string + """','"""+name_on_order+ """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success('Your Smoothie is ordered!', icon="✅")

