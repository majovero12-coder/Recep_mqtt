import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# 🌈 --- Estilos visuales personalizados ---
st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background-color: #f5f7fa;
            color: #222;
            font-family: 'Inter', sans-serif;
        }

        /* Títulos */
        h1, h2, h3 {
            color: #5a3fef;
        }

        /* Botón principal */
        .stButton button {
            background: linear-gradient(90deg, #5a3fef, #7b61ff);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1em;
            font-weight: 600;
            transition: 0.2s ease-in-out;
        }
        .stButton button:hover {
            background: linear-gradient(90deg, #7b61ff, #a483ff);
            transform: scale(1.02);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ebe8ff;
            border-right: 2px solid #c8c3ff;
        }

        /* Inputs */
        input, textarea {
            border-radius: 8px !important;
            border: 1px solid #c5bfff !important;
        }

        /* Expander */
        details {
            background-color: #f2efff;
            border-radius: 10px;
            padding: 10px;
        }

        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #5a3fef;
            font-weight: 700;
        }

        /* Divider */
        hr {
            border: 1px solid #cfcaff;
        }
    </style>
""", unsafe_allow_html=True)


# --- Configuración de la página ---
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered"
)

# --- Variables de estado ---
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None


# --- Función para obtener datos MQTT ---
def get_mqtt_message(broker, port, topic, client_id):
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}


# --- Sidebar (configuración) ---
with st.sidebar:
    st.subheader('⚙️ Configuración de Conexión')
    
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com', 
                           help='Dirección del broker MQTT')
    
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535,
                           help='Puerto del broker (generalmente 1883)')
    
    topic = st.text_input('Tópico', value='sensor_st',
                          help='Tópico MQTT a suscribirse')
    
    client_id = st.text_input('ID del Cliente', value='streamlit_client',
                              help='Identificador único para este cliente')


# --- Contenido principal ---
st.title('📡 Lector de Sensor MQTT')

with st.expander('ℹ️ Información', expanded=False):
    st.markdown("""
    ### Cómo usar esta aplicación:
    1. **Broker MQTT:** Ingresa la dirección del servidor MQTT en el panel lateral.  
    2. **Puerto:** Generalmente es 1883 para conexiones no seguras.  
    3. **Tópico:** El canal al que deseas suscribirte.  
    4. **ID del Cliente:** Un identificador único para esta conexión.  
    5. Haz clic en **Obtener Datos** para recibir el mensaje más reciente.
    
    ### Brokers públicos para pruebas:
    - broker.mqttdashboard.com  
    - test.mosquitto.org  
    - broker.hivemq.com
    """)

st.divider()

# --- Botón para obtener datos ---
if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
    with st.spinner('Conectando al broker y esperando datos...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

# --- Mostrar resultados ---
if st.session_state.sensor_data:
    st.divider()
    st.subheader('📊 Datos Recibidos')
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success('✅ Datos recibidos correctamente')
        
        if isinstance(data, dict):
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key, value=value)
            
            with st.expander('📄 Ver JSON completo'):
                st.json(data)
        else:
            st.code(data)

