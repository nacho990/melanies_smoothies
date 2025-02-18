# Importar paquetes necesarios
import streamlit as st
import requests
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
        "client_session_keep_alive": True  # Para evitar desconexiones
    }

    # Crear sesión con Snowflake
    session = Session.builder.configs(connection_parameters).create()
    st.success("✅ Conectado a Snowflake correctamente.")

except Exception as e:
    st.error(f"❌ Error de conexión a Snowflake: {e}")
    st.stop()

# Título de la app
st.title("🥤 Customize your Smoothies 🥤")
st.write("Choose the fruit you want in your custom Smoothie!")

# Nombre en la orden
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

# Obtener ingredientes desde Snowflake
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name')).to_pandas()
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        my_dataframe['FRUIT_NAME'],  # Convertir a lista de pandas
        max_selections=5
    )
except Exception as e:
    st.error(f"❌ Error al obtener datos: {e}")

# Insertar orden en la base de datos
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition information ')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+ fruit_chosen)
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('✅ Your Smoothie is ordered!')
        except Exception as e:
            st.error(f"❌ Error al insertar datos: {e}")
