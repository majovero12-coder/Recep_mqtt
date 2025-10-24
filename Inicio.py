import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# 🌙 Estilo oscuro personalizado
st.markdown("""
    <style>
        body {
            background-color: #0f1116;
            color: #e5e5e5;
        }
        .stApp {
            background-color: #0f1116;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00e5ff;
        }
        .stButton button {
            background-color: #00e5ff;
            color: black;
            border-radius: 10px;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #00bcd4;
        }
        .stTextInput > div > div > input {
            background-color: #1c1f26;
            color: #ffffff;
        }
        .stNumberInput > div > input {
            background-color: #1c1f26;
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# Configuración de la página
st.set_page_config(page_title="Lector de Sensor MQTT", page_icon="📡", layout="centered")

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

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

# Sidebar
with st.sidebar:
    st.subheader('⚙️ Configuración de Conexión')
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com')
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535)
    topic = st.text_input('Tópico', value='sensor_st')
    client_id = st.text_input('ID del Cliente', value='streamlit_client')

# Título
st.title('📡 Lector de Sensor MQTT')

with st.expander('ℹ️ Información', expanded=False):
    st.markdown("""
    1. Configura los datos del broker en el panel lateral.
    2. Haz clic en **Obtener Datos** para recibir el último mensaje del sensor.
    3. Usa brokers públicos como:
       - broker.mqttdashboard.com  
       - test.mosquitto.org  
       - broker.hivemq.com
    """)

st.divider()

if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
    with st.spinner('Conectando al broker y esperando datos...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

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

