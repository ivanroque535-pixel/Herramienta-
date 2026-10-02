import streamlit as st
from st_keyup import st_keyup
import streamlit.components.v1 as components

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

st.set_page_config(page_title="Escáner Pi", layout="centered")

# Inicializar la "memoria" RAM de la aplicación
if 'posicion' not in st.session_state:
    st.session_state.posicion = 0
    st.session_state.secuencia = ""
    st.session_state.error = False
    st.session_state.llave_reinicio = 0  # Clave maestra para vaciar la caja de texto

st.title("🧠 Entrenador de Pi: Fuego Rápido")

# --- BARRA DE PROGRESO LÍQUIDA ---
porcentaje_float = st.session_state.posicion / 500.0
porcentaje_texto = porcentaje_float * 100
st.progress(porcentaje_float, text=f"Progreso: {st.session_state.posicion} de 500 decimales ({porcentaje_texto:.1f}%)")

# Pantalla principal con tu recorrido
st.text_area("Tu Secuencia Lograda:", value="3." + st.session_state.secuencia, height=150, disabled=True)

# Alerta de error
if st.session_state.error:
    st.error("❌ ANOMALÍA DETECTADA. Ese no es el número. Tu procesador falló, corrígelo.")

# --- ENTRADA AUTOMÁTICA (SIN ENTER) ---
if st.session_state.posicion < 500:
    st.write("Teclea el siguiente dígito:")
    
    # Generamos un ID único para la caja cada vez. Esto fuerza a Streamlit a borrarla al instante.
    id_caja = f"caja_texto_{st.session_state.llave_reinicio}"
    
    # st_keyup lee la tecla en el milisegundo en que la presionas
    intento = st_keyup("", key=id_caja, max_chars=1)

    if intento:
        digito_real = pi_500[st.session_state.posicion]
        
        if intento == digito_real:
            st.session_state.posicion += 1
            st.session_state.secuencia += intento
            st.session_state.error = False
            st.session_state.llave_reinicio += 1  # Destruye y recrea la caja vacía
            st.rerun()  # Recarga la app a velocidad luz
        else:
            st.session_state.error = True
            st.session_state.llave_reinicio += 1  # Destruye la caja errónea
            st.rerun()

# --- VICTORIAS Y CELEBRACIONES ---
if st.session_state.posicion == 500:
    st.balloons()
    st.success("🏆 ¡SISTEMA COMPLETADO! Has dominado los 500 dígitos como una supercomputadora.")
elif st.session_state.posicion > 0 and st.session_state.posicion % 10 == 0 and not st.session_state.error:
    st.success(f"🔥 ¡Bloque completado! La memoria muscular está al 100%.")

# --- HACK PARA MANTENER EL CURSOR EN LA CAJA ---
components.html(
    """
    <script>
    const doc = window.parent.document;
    const inputs = doc.querySelectorAll('input');
    if (inputs.length > 0) {
        inputs[0].focus();
    }
    </script>
    """,
    height=0
)
