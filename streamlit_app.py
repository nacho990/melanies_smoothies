# Importar paquetes necesarios
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Verificar si los secrets existen antes de usarlos
if "snowflake" not in st.secrets:
    st.error("❌ No se encontraron credenciales de Snowflake en `st.secrets`. Verifica la configuración en Streamlit Cloud.")
    st.stop()

# Configurar conexión con Snowflake desde `st.secrets`
try:
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "role": st.secrets["snowflake"]["role"],
        "client_session_keep_alive": st.secrets["snowflake"].get("client_session_keep_alive", True)
    }

    # Crear sesión con Snowflake
    session = Session.builder.configs(connection_parameters).create()
    st.success("✅ Conectado a Snowflake correctamente.")

except Exception as e:
    st.error(f"❌ Error de conexión a Snowflake: {e}")
    st.stop()

# Título de la app
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

