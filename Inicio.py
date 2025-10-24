import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# ---------------- CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered"
)

# ---------------- ESTILO VISUAL ----------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        h1, h2, h3, h4 {
            color: #80deea;
        }
        .stSidebar {
            background-color: #102027 !important;
        }
        .stButton>button {
            background-color: #00796b;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #26a69a;
        }
        .stMetric {
            background-color: #004d40;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- VARIABLES DE ESTADO ----------------
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# ---------------- FUNCIÓN MQTT ----------------
def get_mqtt_message(broker, port, topic, client_id):
    """Obtiene un solo mensaje MQTT del tópico indicado"""
    message_received = {"received": False, "payload": None}

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
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

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Configuración")
    st.markdown("Ajusta los parámetros de conexión al **broker MQTT**.")

    broker = st.text_input(
        'Broker MQTT',
        value='broker.mqttdashboard.com',
        help='Dirección del broker MQTT (p. ej. broker.mqttdashboard.com)'
    )

    port = st.number_input(
        'Puerto',
        value=1883,
        min_value=1,
        max_value=65535,
        help='Puerto del broker (normalmente 1883)'
    )

    topic = st.text_input(
        'Tópico',
        value='sensor_st',
        help='Canal MQTT al que suscribirse'
    )

    client_id = st.text_input(
        'ID del Cliente',
        value='streamlit_client',
        help='Identificador único para esta conexión'
    )

# ---------------- INTERFAZ PRINCIPAL ----------------
st.title("📡 Lector de Sensor MQTT")
st.subheader("Recibe datos en tiempo real desde un broker MQTT")

with st.expander("ℹ️ Cómo usar la aplicación"):
    st.markdown("""
    1️⃣ Configura la conexión en el panel lateral  
    2️⃣ Pulsa **Obtener Datos**  
    3️⃣ Verás la lectura en formato JSON o como métricas visuales  
    
    **Brokers públicos recomendados:**
    - `broker.mqttdashboard.com`
    - `test.mosquitto.org`
    - `broker.hivemq.com`
    """)

st.divider()

# ---------------- BOTÓN DE ACCIÓN ----------------
if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
    with st.spinner('🔌 Conectando al broker...'):
        data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = data

# ---------------- RESULTADOS ----------------
if st.session_state.sensor_data:
    st.divider()
    st.subheader("📊 Datos Recibidos")

    data = st.session_state.sensor_data

    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success("✅ Datos recibidos correctamente")

        if isinstance(data, dict):
            # Mostrar métricas
            num_cols = min(len(data), 4)
            cols = st.columns(num_cols)
            for i, (key, value) in enumerate(data.items()):
                with cols[i % num_cols]:
                    st.metric(label=key, value=value)

            with st.expander("📄 Ver JSON completo"):
                st.json(data)
        else:
            st.code(data)
else:
    st.info("Haz clic en **Obtener Datos del Sensor** para iniciar la lectura.")

# ---------------- PIE ----------------
st.markdown("---")
st.caption("📡 Aplicación MQTT desarrollada con Streamlit")
