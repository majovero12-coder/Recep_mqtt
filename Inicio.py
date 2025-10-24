import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# --- Configuración de la página (debe ir primero) ---
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered"
)

# --- Estilos personalizados ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #0a0f1c, #1f3b73);
        color: #f0f0f0;
    }

    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #FFD700; /* Dorado */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1623, #1b2b45);
        color: white;
    }

    /* Inputs */
    input, textarea, select {
        border-radius: 10px !important;
        border: 1px solid #FFD700 !important;
        background-color: #0d1b2a !important;
        color: #ffffff !important;
    }

    /* Botones */
    div.stButton > button {
        background-color: #FFD700;
        color: #0b0b0b;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #ffcc00;
        color: black;
        transform: scale(1.05);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a2a40 !important;
        color: #FFD700 !important;
        border-radius: 5px;
    }

    /* Divider */
    hr {
        border: 1px solid #FFD700;
    }
    </style>
""", unsafe_allow_html=True)

# --- Variables de estado ---
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None


# --- Función MQTT ---
def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
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


# --- Sidebar ---
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

# --- Título ---
st.title('📡 Lector de Sensor MQTT')

# --- Información ---
with st.expander('ℹ️ Información', expanded=False):
    st.markdown("""
    ### Cómo usar esta aplicación:
    
    1. **Broker MQTT**: Ingresa la dirección del servidor MQTT en el sidebar  
    2. **Puerto**: Generalmente es 1883 para conexiones no seguras  
    3. **Tópico**: El canal al que deseas suscribirte  
    4. **ID del Cliente**: Un identificador único para esta conexión  
    5. Haz clic en **Obtener Datos** para recibir el mensaje más reciente  
    
    ### Brokers públicos para pruebas:
    - broker.mqttdashboard.com  
    - test.mosquitto.org  
    - broker.hivemq.com
    """)

st.divider()

# --- Botón ---
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
            
            with st.expander('Ver JSON completo'):
                st.json(data)
        else:
            st.code(data)
