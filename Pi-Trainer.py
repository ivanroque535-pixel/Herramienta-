def entrenador_pi():
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

    print("==================================================")
    print(" 🧠 MODO ENTRENAMIENTO ESTRICTO ACTIVADO 🧠")
    print("==================================================")
    print("- Ingresa cada dígito y presiona Enter.")
    print("- El sistema no te dejará avanzar hasta que aciertes.")
    print("- Escribe 'q' y presiona Enter para salir.")
    print("==================================================\n")
    print("Empezamos después del 3.\n")

    posicion = 0
    secuencia_actual = ""

    while posicion < len(pi_500):
        digito_real = pi_500[posicion]
        
        # Pedimos el dígito
        intento = input(f"[Posición {posicion + 1:03d}] Ingresa dígito: ").strip()
        
        # Opción para salir del loop
        if intento.lower() == 'q':
            print(f"\n🛑 Entrenamiento pausado. Tu récord actual quedó en la posición {posicion}.")
            break
            
        # Evaluamos el dígito
        if intento == digito_real:
            posicion += 1
            secuencia_actual += intento
            
            # Celebración de micropasos cada 10 dígitos (un bloque)
            if posicion % 10 == 0:
                print(f"   ✅ ¡Bloque completado! Secuencia: {secuencia_actual[-10:]}")
                print(f"   🔥 Llevas {posicion} dígitos perfectos.\n")
        else:
            print("   ❌ ERROR DE CONEXIÓN. Ese no es el número. Piensa bien e intenta de nuevo.")
            
    # Si logras terminar el jefe final
    if posicion == len(pi_500):
        print("\n🏆 ¡HAZAÑA COMPLETADA! Has navegado los 500 dígitos a la perfección.")

# Iniciar el programa
entrenador_pi()
