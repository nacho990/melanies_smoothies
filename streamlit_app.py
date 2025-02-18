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
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('SEARCH_ON')).to_pandas()
    
    # Crear un diccionario para mapear FRUIT_NAME -> SEARCH_ON
    search_on_mapping = dict(zip(my_dataframe['FRUIT_NAME'], my_dataframe['SEARCH_ON']))
    
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        my_dataframe['FRUIT_NAME'],  # Mostrar nombres de fruta
        max_selections=6
    )
except Exception as e:
    st.error(f"❌ Error al obtener datos: {e}")

# Insertar orden en la base de datos
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Convertir la lista en una cadena de texto

    for fruit_chosen in ingredients_list:
        # Obtener el valor de SEARCH_ON correspondiente
        search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Validar la relación
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        st.subheader(f"{fruit_chosen} Nutrition information")

        # Usar SEARCH_ON en la llamada a la API
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        smoothiefroot_response = requests.get(api_url)

        # Verificar si la respuesta es válida antes de mostrarla
        if smoothiefroot_response.status_code == 200:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"❌ Error al obtener información para {fruit_chosen}")

    time_to_insert = st.button('Submit Order')

if time_to_insert:
    try:
        # Definir la sentencia SQL para insertar la orden en la base de datos
        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (NAME_ON_ORDER, INGREDIENTS)
        VALUES ('{name_on_order}', '{ingredients_string}')
        """
        
        # Mostrar la consulta generada en la app para verificar que es correcta
        st.write("Generated SQL Statement:", my_insert_stmt)
        
        # Ejecutar la sentencia en Snowflake
        session.sql(my_insert_stmt).collect()
        st.success('✅ Your Smoothie is ordered!')
    except Exception as e:
        st.error(f"❌ Error al insertar datos: {e}")

