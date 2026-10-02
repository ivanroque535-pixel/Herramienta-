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
st.title("🧠 Entrenador de Pi: Fuego Rápido")
st.write("Escribe los números de corrido sin presionar Enter. Si te equivocas, usa tu tecla de borrar (Backspace).")

# La caja de entrada mágica (nunca se destruye, por lo que nunca pierdes el cursor)
intento = st_keyup("Secuencia (inicia en 1415...):", key="entrada_continua")

# Lógica de escaneo en tiempo real
posicion_actual = 0
error = False

if intento:
    # Quitamos espacios por si escribes en bloques
    intento_limpio = intento.replace(" ", "")
    
    # Comprobamos si tu secuencia coincide exactamente con el mapa
    if pi_500.startswith(intento_limpio):
        posicion_actual = len(intento_limpio)
    else:
        error = True
        # Calculamos hasta dónde ibas bien antes del error
        for i in range(len(intento_limpio)):
            if i < len(pi_500) and intento_limpio[i] == pi_500[i]:
                posicion_actual += 1
            else:
                break

# Interfaz visual
if error:
    st.error("❌ ANOMALÍA DETECTADA. El último número es incorrecto. ¡Presiona borrar para corregirlo!")
else:
    if posicion_actual > 0 and posicion_actual % 10 == 0:
        st.success(f"🔥 ¡Bloque completado! Llevas {posicion_actual} números.")

# Barra de progreso
porcentaje_float = min(posicion_actual / 500.0, 1.0)
st.progress(porcentaje_float, text=f"Progreso: {posicion_actual} de 500 decimales ({porcentaje_float * 100:.1f}%)")

if posicion_actual >= 500:
    st.balloons()
    st.success("🏆 ¡SISTEMA COMPLETADO! Has logrado los 500 perfectos.")
