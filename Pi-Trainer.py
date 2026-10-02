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
st.write("Teclea sin detenerte. El sistema organizará tu memoria en bloques de 10 automáticamente.")

posicion_actual = 0
error = False
secuencia_correcta = ""

# 1. El radar de tecleo (mantiene el cursor activo)
intento = st_keyup("Teclea el siguiente dígito:", key="entrada_continua")

if intento:
    intento_limpio = intento.replace(" ", "")
    
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

# 2. Formateo de la secuencia con espacios cada 10 dígitos
secuencia_formateada = " ".join([secuencia_correcta[i:i+10] for i in range(0, len(secuencia_correcta), 10)])
texto_mostrar = f"3.{secuencia_formateada}" if secuencia_correcta else "3."

# 3. La caja de texto consolidada (estilo visual solicitado)
st.text_area("Tu Secuencia Lograda:", value=texto_mostrar, height=150, disabled=True)

# 4. Sistema de alertas justo debajo de la caja
if error:
    st.error("❌ ANOMALÍA DETECTADA. El último número es incorrecto. ¡Presiona borrar para corregirlo!")
else:
    if posicion_actual > 0 and posicion_actual % 10 == 0:
        st.success(f"🔥 ¡Bloque de 10 sellado! Llevas {posicion_actual} decimales puros.")

# 5. Barra de progreso colocada al final de toda la interfaz
st.write("---")
porcentaje_float = min(posicion_actual / 500.0, 1.0)
st.progress(porcentaje_float, text=f"Progreso: {posicion_actual} de 500 decimales ({porcentaje_float * 100:.1f}%)")

if posicion_actual >= 500:
    st.balloons()
    st.success("🏆 ¡CONEXIÓN TOTAL! Has plasmado los 500 dígitos perfectos.")
