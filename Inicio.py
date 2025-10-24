import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# 🎨 --- Colores personalizados (solo estilo visual) ---
st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background-color: #eef1ff;
            color: #222;
        }

        /* Títulos */
        h1, h2, h3 {
            color: #4a3aff;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #e2e0ff;
            color: #111;
        }

        /* Botones */
        .stButton>button {
            background-color: #4a3aff;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #6d5eff;
            transform: scale(1.03);
        }

        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #4a3aff;
        }

        /* Expander */
        details {
            background-color: #f6f5ff;
            border-radius: 10px;
            padding: 8px;
        }

        /* Divisiones */
        hr {
            border: 1px solid #d7d3ff;
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
        se


