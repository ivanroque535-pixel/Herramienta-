import streamlit as st
from st_keyup import st_keyup

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
st.title("🧠 Entrenador de Pi: Nivel Alienígena")
st.write("Teclea desde tu computadora o despliega el panel numérico si estás en el celular.")

# --- 1. MEMORIA MAESTRA MULTI-DISPOSITIVO ---
if "secuencia_maestra" not in st.session_state:
    st.session_state.secuencia_maestra = ""

# --- 2. FUNCIONES DEL TECLADO MÓVIL ---
def teclear(num):
    st.session_state.secuencia_maestra += str(num)

def borrar():
    st.session_state.secuencia_maestra = st.session_state.secuencia_maestra[:-1]

def limpiar():
    st.session_state.secuencia_maestra = ""

# --- 3. PANEL DESPLEGABLE (MÓVIL) ---
with st.expander("📱 Abrir Teclado Numérico en Pantalla", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("1", on_click=teclear, args=(1,), use_container_width=True)
        st.button("4", on_click=teclear, args=(4,), use_container_width=True)
        st.button("7", on_click=teclear, args=(7,), use_container_width=True)
        st.button("⌫", on_click=borrar, use_container_width=True)
    with c2:
        st.button("2", on_click=teclear, args=(2,), use_container_width=True)
        st.button("5", on_click=teclear, args=(5,), use_container_width=True)
        st.button("8", on_click=teclear, args=(8,), use_container_width=True)
        st.button("0", on_click=teclear, args=(0,), use_container_width=True)
    with c3:
        st.button("3", on_click=teclear, args=(3,), use_container_width=True)
        st.button("6", on_click=teclear, args=(6,), use_container_width=True)
        st.button("9", on_click=teclear, args=(9,), use_container_width=True)
        st.button("Limpiar", on_click=limpiar, use_container_width=True)

# --- 4. RADAR DE TECLEO (PC) ---
# Sincronizamos la barra de texto clásica con los botones de la pantalla
intento = st_keyup("Radar de tecleo:", value=st.session_state.secuencia_maestra, key="entrada_continua")

# Si usas el teclado físico, actualiza la memoria maestra
if intento is not None and intento != st.session_state.secuencia_maestra:
    st.session_state.secuencia_maestra = intento

# --- 5. LÓGICA DE ESCANEO ---
posicion_actual = 0
error = False
secuencia_correcta = ""

intento_limpio = st.session_state.secuencia_maestra.replace(" ", "")

if pi_500.startswith(intento_limpio):
    posicion_actual = len(intento_limpio)
    secuencia_correcta = intento_limpio
else:
    error = True
    for i in range(len(intento_limpio)):
        if i < len(pi_500) and intento_limpio[i] == pi_500[i]:
            posicion_actual += 1
            secuencia_correcta += intento_limpio[i]
        else:
            break

# --- 6. CAJA CONSOLIDADA OSCURA ---
secuencia_formateada = " ".join([secuencia_correcta[i:i+10] for i in range(0, len(secuencia_correcta), 10)])
texto_mostrar = f"3.{secuencia_formateada}" if secuencia_correcta else "3."

st.text_area("Tu Secuencia Lograda:", value=texto_mostrar, height=150, disabled=True)

# --- 7. ALERTAS ---
if error:
    st.error("❌ ANOMALÍA DETECTADA. El último número es incorrecto. ¡Presiona borrar para corregirlo!")
else:
    if posicion_actual > 0 and posicion_actual % 10 == 0:
        st.success(f"🔥 ¡Bloque de 10 sellado! Llevas {posicion_actual} decimales puros.")

# --- 8. BARRA DE PROGRESO INFERIOR ---
st.write("---")
porcentaje_float = min(posicion_actual / 500.0, 1.0)
st.progress(porcentaje_float, text=f"Progreso: {posicion_actual} de 500 decimales ({porcentaje_float * 100:.1f}%)")

if posicion_actual >= 500:
    st.balloons()
    st.success("🏆 ¡CONEXIÓN TOTAL! Has plasmado los 500 dígitos perfectos.")
