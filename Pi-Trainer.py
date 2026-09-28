import streamlit as st

# Los 500 primeros decimales exactos de Pi
pi_500 = (
    "14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170679"
    "82148086513282306647093844609550582231725359408128"
    "48111745028410270193852110555964462294895493038196"
    "44288109756659334461284756482337867831652712019091"
    "45648566923460348610454326648213393607260249141273"
    "72458700660631558817488152092096282925409171536436"
    "78925903600113305305488204665213841469519415116094"
    "33057270365759591953092186117381932611793105118548"
    "07446237996274956735188575272489122793818301194912"
)

st.title("🧠 Entrenador de Pi: Nivel Titán")
st.write("Ingresa cada dígito uno por uno. El sistema solo te dejará avanzar si es correcto.")

# Inicializar la "memoria" de la aplicación
if 'posicion' not in st.session_state:
    st.session_state.posicion = 0
    st.session_state.secuencia = ""
    st.session_state.error = False

# Función que se ejecuta cada vez que presionas Enter en la caja de texto
def verificar_digito():
    intento = st.session_state.input_digito.strip()
    
    # Ignorar si está vacío
    if not intento:
        return
        
    digito_real = pi_500[st.session_state.posicion]
    
    if intento == digito_real:
        st.session_state.posicion += 1
        st.session_state.secuencia += intento
        st.session_state.error = False
    else:
        st.session_state.error = True
        
    # Limpiar la caja de texto automáticamente para el siguiente número
    st.session_state.input_digito = ""

# Interfaz principal
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Posición Actual", value=st.session_state.posicion + 1)
with col2:
    st.metric(label="Dígitos Perfectos", value=st.session_state.posicion)

st.text_area("Tu Secuencia Lograda:", value="3." + st.session_state.secuencia, height=150, disabled=True)

# Mensaje de error condicional
if st.session_state.error:
    st.error("❌ ERROR DE CONEXIÓN. Ese no es el número correcto.")

# Caja de entrada (llama a la función verificar_digito al presionar Enter)
st.text_input("Ingresa el siguiente dígito y presiona Enter:", 
              key="input_digito", 
              on_change=verificar_digito)

# Celebración por bloques
if st.session_state.posicion > 0 and st.session_state.posicion % 10 == 0 and not st.session_state.error:
    st.success(f"🔥 ¡Bloque completado! Llevas {st.session_state.posicion} dígitos perfectos.")

# Victoria final
if st.session_state.posicion == 500:
    st.balloons()
    st.success("🏆 ¡HAZAÑA COMPLETADA! Has dominado los 500 dígitos.")
