import sympy as sp
from IPython.display import display

# 1. Definir las variables articulares simbólicas
q1, q2, q3, q4 = sp.symbols('q1 q2 q3 q4')

# 2. Definir la función para la matriz de transformación de Denavit-Hartenberg
def dh_matrix(theta, d, a, alpha):
    return sp.Matrix([
        [sp.cos(theta), -sp.sin(theta)*sp.cos(alpha),  sp.sin(theta)*sp.sin(alpha), a*sp.cos(theta)],
        [sp.sin(theta),  sp.cos(theta)*sp.cos(alpha), -sp.cos(theta)*sp.sin(alpha), a*sp.sin(theta)],
        [0,              sp.sin(alpha),                sp.cos(alpha),               d],
        [0,              0,                            0,                           1]
    ])

# 3. Factor de conversión de grados a radianes
# (SymPy y Python evalúan trigonométricamente en radianes)
deg2rad = sp.pi / 180

# 4. Tabla de parámetros DH [theta, d, a, alpha] extraída de tu imagen
dh_table = [
    [q1 - sp.Rational(90, 1) * deg2rad,  sp.Rational(42057, 1000), sp.Rational(10138, 1000), -sp.Rational(90, 1) * deg2rad],
    [q2 + sp.Rational(4799, 100) * deg2rad, sp.Rational(0,1),      sp.Rational(94882, 1000),   sp.Rational(0,1)],
    [q3 - sp.Rational(784, 100) * deg2rad,  sp.Rational(0,1),      sp.Rational(83809, 1000),   sp.Rational(0,1)],
    [q4 - sp.Rational(4015, 100) * deg2rad, sp.Rational(0,1),      sp.Rational(15622, 100),   sp.Rational(0,1)]
]

# 5. Calcular las matrices individuales
T01 = dh_matrix(*dh_table[0])
T12 = dh_matrix(*dh_table[1])
T23 = dh_matrix(*dh_table[2])
T34 = dh_matrix(*dh_table[3])

# Mostrar matrices individuales (opcional)
print("--- Matrices Individuales ---")
print("Matriz T01:")
display(T01)
print("\nMatriz T12:")
display(T12)
print("\nMatriz T23:")
display(T23)
print("\nMatriz T34:")
display(T34)

# 6. Calcular la matriz de transformación total (0T4) de forma exacta

T04 = T01 * T12 * T23 * T34

# 7. MOSTRAR LA MATRIZ FINAL EXACTA
print("\n==================================================")
print("                  MATRIZ FINAL 0T4         ")
print("==================================================")


#display(redondear_matriz(T04, 3)) (Comentada para tener exactitud en los cálculos posteriores)
sp.trigsimp(display(T04))


# === CÓDIGO PARA LA MATRIZ JACOBIANA LINEAL ===

# 1. Función para redondear (la agrego aquí por si no estaba definida en tu celda actual)
def redondear_matriz(matriz, decimales=3):
    return matriz.xreplace({n: round(n, decimales) for n in matriz.atoms(sp.Float)})

# 2. Extraer el vector de posición P del efector final
# Tomamos las primeras 3 filas (índices 0, 1, 2) de la última columna (índice 3) de T04
P = T04[:3, 3]

# 3. Agrupar nuestras variables articulares en una lista
# Esto le dirá a SymPy respecto a qué variables debe derivar
q_vars = [q1, q2, q3, q4]

# 4. Calcular la Matriz Jacobiana Lineal (Jv)
# La función .jacobian() deriva el vector P respecto a cada variable en q_vars
# El resultado será una matriz de 3 filas (x, y, z) por 4 columnas (q1, q2, q3, q4)
J_v = P.jacobian(q_vars)

# 5. MOSTRAR LOS RESULTADOS
print("\n==================================================")
print("           MATRIZ JACOBIANA LINEAL (Jv)           ")
print("==================================================")

# =========================================================
# SELECCIONA QUÉ VERSIÓN MOSTRAR (Comentar/Descomentar con #)
# =========================================================

# VERSIÓN 1: Matriz redondeada a 3 decimales r
#display(redondear_matriz(J_v, 3))

# VERSIÓN 2: Matriz exacta (Usada para cálculos numéricos posteriores)
display(J_v)

# 1. Calcular las matrices de transformación intermedias
# Ya tenemos T01. Necesitamos T02 y T03 para extraer sus vectores Z.
T02 = T01 * T12
T03 = T02 * T23

# 2. Extraer los vectores Z de cada articulación (ejes de rotación)
# En SymPy, [:3, 2] toma las filas 0, 1 y 2 (x, y, z) de la columna 2 (que es la tercera columna, el vector Z)

# Z0 es el eje de la base (Articulación 1). Siempre es [0, 0, 1] en robots estándar montados en el suelo.
Z0 = sp.Matrix([0, 0, 1])

# Z1 es el eje de la Articulación 2, extraído de T01
Z1 = T01[:3, 2]

# Z2 es el eje de la Articulación 3, extraído de T02
Z2 = T02[:3, 2]

# Z3 es el eje de la Articulación 4, extraído de T03
Z3 = T03[:3, 2]

# 3. Construir la Matriz Jacobiana Angular (Jw)
# Unimos todos los vectores Z lado a lado (horizontal stack)
J_w = sp.Matrix.hstack(Z0, Z1, Z2, Z3)

# 4. MOSTRAR LOS RESULTADOS
print("\n==================================================")
print("          MATRIZ JACOBIANA ANGULAR (Jw)           ")
print("==================================================")

display(J_w)






from IPython.display import Math

print("\n==================================================")
print("   CÁLCULO DEL ÍNDICE DE MANIPULABILIDAD (w)      ")
print("==================================================")

# 1. Usamos SOLO la Jacobiana Lineal (J_v)
# Multiplicamos J_v (3x4) por su transpuesta (4x3) para obtener una matriz 3x3
Jv_Jv_T = J_v * J_v.T

# 2. Calculamos el determinante de esa matriz 3x3
det_Jv = Jv_Jv_T.det()

# 3. Simplificamos

det_Jv_simplificado = sp.trigsimp(det_Jv)

# 4. Aplicamos la raíz cuadrada
w_posicional = sp.sqrt(det_Jv_simplificado)

# 5. Mostramos el resultado con formato LaTeX
print("\nLa ecuación analítica de la manipulabilidad posicional (w) es:")
display(Math('w = ' + sp.latex(w_posicional)))


print("\n==================================================")
print("              BÚSQUEDA DE SINGULARIDADES      ")
print("==================================================")

try:
    # Igualamos a 0 el determinante simplificado (más rápido para SymPy que usar la raíz)
    ecuacion_sing = sp.factor(det_Jv_simplificado)

    # Buscamos los ángulos que hacen que la ecuación sea 0
    singularidades = sp.solve(ecuacion_sing, q_vars)

    if not singularidades:
        print("No se encontraron singularidades analíticas directas o la expresión es muy compleja.")
    else:
        print("El robot entra en singularidad posicional bajo las siguientes condiciones:")

        # Formatear la salida para que sea fácil de leer
        if isinstance(singularidades, list):
            for i, conf in enumerate(singularidades):
                print(f"Solución {i+1}: {conf}")
        else:
            print(singularidades)

except Exception as e:
    print(f"La ecuación es demasiado compleja para resolverla analíticamente de forma directa:\n{e}")

77
7
7
7
7
7
from sympy import *
from math import radians, degrees

# ==========================================
# 1. METODOLOGÍA MATRICIAL (Denavit-Hartenberg)
# ==========================================
def matriz_DH(theta, d, a, alpha):
    """
    Calcula la matriz de transformación homogénea estándar de DH.
    Sistemas de referencia:
    - Z_(i-1) es el eje de la articulación i.
    - X_i es la perpendicular común entre Z_(i-1) y Z_i.
    """
    return Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),              cos(alpha),            d],
        [0,           0,                       0,                     1]
    ])

# ==========================================
# 2. CONFIGURACIÓN DEL ROBOT (Dimensiones y Restricciones)
# ==========================================
# Dimensiones físicas reales (Eslabones en mm)
L1_d1 = 30.78   # Distancia vertical del suelo al eje del hombro
L2_a2 = 87.00   # Longitud física del hombro al codo
L3_a3 = 87.00   # Longitud física del codo a la muñeca
L4_a4 = 171.14  # Longitud física de la muñeca al efector final

# Restricciones operacionales de las articulaciones (Límites físicos de carrera en grados)
LIMITES_ARTICULARES = {
    "q1": (-150.0, 150.0),
    "q2": (-45.0,  135.0),
    "q3": (-90.0,  90.0),
    "q4": (-120.0, 120.0)
}

# ==========================================
# 3. CAPTURA Y VERIFICACIÓN DE VARIABLES ARTICULARES
# ==========================================
print("=== CINEMÁTICA DIRECTA DE MANIPULADOR (4 GDL) ===")
q1_deg = float(input("Ingrese Variable Articular q1 (Base) en grados: "))
q2_deg = float(input("Ingrese Variable Articular q2 (Hombro) en grados: "))
q3_deg = float(input("Ingrese Variable Articular q3 (Codo) en grados: "))
q4_deg = float(input("Ingrese Variable Articular q4 (Muñeca) en grados: "))

entradas = [q1_deg, q2_deg, q3_deg, q4_deg]
fuera_de_limite = False

# Validación automática de restricciones
for i, q in enumerate(entradas, 1):
    lim_inf, lim_sup = LIMITES_ARTICULARES[f"q{i}"]
    if not (lim_inf <= q <= lim_sup):
        print(f"⚠️ ADVERTENCIA: q{i} ({q}°) excede el límite físico del hardware [{lim_inf}°, {lim_sup}°]")
        fuera_de_limite = True

if fuera_de_limite:
    print("❌ Operación cancelada por seguridad. Las variables exceden los límites mecánicos.")
    exit()

# ==========================================
# 4. PASO A RADIANES Y ARREGLO DE OFFSETS (Tabla DH)
# ==========================================
# Conversión a radianes de las entradas del usuario
q1 = radians(q1_deg)
q2 = radians(q2_deg)
q3 = radians(q3_deg)
q4 = radians(q4_deg)

# Definición analítica de los ángulos theta (incluyendo desfases de Home de tu tabla)
theta1 = q1 + radians(90.0)
theta2 = q2 + radians(53.88)
theta3 = q3 - radians(69.17)
theta4 = q4 - radians(13.86)

# ==========================================
# 5. DESARROLLO MATRICIAL COHERENTE (Paso a Paso)
# ==========================================
# Transformaciones individuales de eslabón respecto al anterior A_i
T01 = matriz_DH(theta1, L1_d1, 0,     radians(-90.0))
T12 = matriz_DH(theta2, 0,     L2_a2, 0)
T23 = matriz_DH(theta3, 0,     L3_a3, 0)
T34 = matriz_DH(theta4, 0,     L4_a4, 0)

# Multiplicación encadenada trazable (Cinemática acumulada)
T02 = T01 * T12
T03 = T02 * T23
T04 = T03 * T34  # Matriz de transformación homogénea total del Efector Final

# ==========================================
# 6. SALIDA ORDENADA Y DESCOMPOSICIÓN DE LA POSICIÓN
# ==========================================
# Extracción del vector de posición (Última columna del espacio homogéneo)
Px = T04[0,3]
Py = T04[1,3]
Pz = T04[2,3]

print("\n" + "="*45)
print(" DESARROLLO DE TRANSICIONES MATRICIALES (DH)")
print("="*45)

matrices = {"T01": T01, "T12": T12, "T23": T23, "T34": T34, "T04 (Total)": T04}
for nombre, m in matrices.items():
    print(f"\n🔹 Matriz Homogénea {nombre}:")
    pprint(N(m, 4))

print("\n" + "="*45)
print(" VECTOR DE POSICIÓN RESULTANTE EN EL ESPACIO")
print("="*45)
print(f" 📍 Coordenada Px (Eje X global) : {N(Px, 4)} mm")
print(f" 📍 Coordenada Py (Eje Y global) : {N(Py, 4)} mm")
print(f" 📍 Coordenada Pz (Eje Z global) : {N(Pz, 4)} mm")


from sympy import symbols, Matrix, cos, sin, pi, simplify, pprint, Float

# ==========================================
# 1. DEFINICIÓN DE VARIABLES SIMBÓLICAS
# ==========================================
q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# ==========================================
# 2. FUNCIÓN DE REDONDEO SIMBÓLICO
# ==========================================
def redondear_matriz(matriz, decimales=3):
    """
    Busca todos los números flotantes en la expresión matricial
    y los redondea a la cantidad de decimales indicada.
    """
    return matriz.xreplace({n: round(n, decimales) for n in matriz.atoms(Float)})

# ==========================================
# 3. METODOLOGÍA MATRICIAL (Denavit-Hartenberg)
# ==========================================
def matriz_DH(theta, d, a, alpha):
    """Calcula, simplifica y redondea la matriz de transformación"""
    M = Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])

    # 1. Simplificamos para aplicar identidades trigonométricas
    M_simplificada = simplify(M)

    # 2. Aplicamos la función de redondeo a 3 decimales
    M_redondeada = redondear_matriz(M_simplificada, 3)

    return M_redondeada

# ==========================================
# 4. DIMENSIONES DEL ROBOT
# ==========================================
L1_d1 = 30.78
L2_a2 = 87.00
L3_a3 = 87.00
L4_a4 = 171.14

# ==========================================
# 5. ÁNGULOS Y DESFASES (En radianes)
# ==========================================
theta1 = q1 + pi/2
theta2 = q2 + (53.88 * pi / 180)
theta3 = q3 - (69.17 * pi / 180)
theta4 = q4 - (13.86 * pi / 180)

# ==========================================
# 6. CÁLCULO DE MATRICES INDIVIDUALES
# ==========================================
T01 = matriz_DH(theta1, L1_d1, 0, -pi/2)
T12 = matriz_DH(theta2, 0, L2_a2, 0)
T23 = matriz_DH(theta3, 0, L3_a3, 0)
T34 = matriz_DH(theta4, 0, L4_a4, 0)

# ==========================================
# 7. IMPRESIÓN DE MATRICES SIMBÓLICAS
# ==========================================
print("\n=== MATRIZ T_0_1 ===")
pprint(T01)

print("\n=== MATRIZ T_1_2 ===")
pprint(T12)

print("\n=== MATRIZ T_2_3 ===")
pprint(T23)

print("\n=== MATRIZ T_3_4 ===")
pprint(T34)

from sympy import symbols, Matrix, cos, sin, pi, simplify, pprint, Float

# ==========================================
# 1. DEFINICIÓN DE VARIABLES SIMBÓLICAS
# ==========================================
q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# ==========================================
# 2. FUNCIÓN DE REDONDEO SIMBÓLICO
# ==========================================
def redondear_matriz(matriz, decimales=3):
    return matriz.xreplace({n: round(n, decimales) for n in matriz.atoms(Float)})

# ==========================================
# 3. METODOLOGÍA MATRICIAL (Denavit-Hartenberg)
# ==========================================
def matriz_DH(theta, d, a, alpha):
    M = Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])
    return redondear_matriz(simplify(M), 3)

# ==========================================
# 4. DIMENSIONES DEL ROBOT
# ==========================================
L1_d1 = 30.78
L2_a2 = 87.00
L3_a3 = 87.00
L4_a4 = 171.14

# ==========================================
# 5. ÁNGULOS Y DESFASES (En radianes)
# ==========================================
theta1 = q1 + pi/2
theta2 = q2 + (53.88 * pi / 180)
theta3 = q3 - (69.17 * pi / 180)
theta4 = q4 - (13.86 * pi / 180)

# ==========================================
# 6. CÁLCULO INTERNO (En silencio)
# ==========================================
T01 = matriz_DH(theta1, L1_d1, 0, -pi/2)
T12 = matriz_DH(theta2, 0, L2_a2, 0)
T23 = matriz_DH(theta3, 0, L3_a3, 0)
T34 = matriz_DH(theta4, 0, L4_a4, 0)

# ==========================================
# 7. CÁLCULO DE LA MATRIZ TOTAL T04
# ==========================================
print("Procesando la matriz completa T04 (esto puede tardar unos segundos)...")
T04_bruta = T01 * T12 * T23 * T34
T04 = redondear_matriz(simplify(T04_bruta), 3)

# ==========================================
# 8. IMPRESIÓN DEL RESULTADO ÚNICO
# ==========================================
print("\n=== MATRIZ COMPLETA T_0_4 (4x4) ===")
pprint(T04)

from sympy import *
from math import degrees, radians

# ==========================================
# VARIABLES SIMBÓLICAS
# ==========================================
q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# ==========================================
# PARÁMETROS DEL ROBOT
# ==========================================
d1 = 30.78
a2 = 87.00
a3 = 87.00
a4 = 171.14

# ==========================================
# MATRIZ DH
# ==========================================
def DH(theta, d, a, alpha):
    return Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])

# ==========================================
# TABLA DH DE TU ROBOT
# ==========================================
A1 = DH(q1 + pi/2, d1, 0, -pi/2)
A2 = DH(q2 + 53.88*pi/180, 0, a2, 0)
A3 = DH(q3 - 69.17*pi/180, 0, a3, 0)
A4 = DH(q4 - 13.86*pi/180, 0, a4, 0)

# ==========================================
# CINEMÁTICA DIRECTA
# ==========================================
print("Calculando cinemática directa base... (por favor espera unos segundos)")
T04 = simplify(A1*A2*A3*A4)

Pz = simplify(T04[2,3])
Px = simplify(T04[0,3])
Py = simplify(T04[1,3])

# ==========================================
# TRUCO: GENERADOR DE PUNTO 100% GARANTIZADO
# ==========================================
# Forzamos al robot a estar a aprox 57 grados (1 radián) en cada articulación
T_prueba = T04.subs({q1: 1.0, q2: 1.0, q3: 1.0, q4: 0})
print("\n" + "="*35)
print("--- PUNTO DE PRUEBA INFALIBLE ---")
print("Ingresa exactamente estos valores:")
print(f"X: {round(float(T_prueba[0,3]), 2)}")
print(f"Y: {round(float(T_prueba[1,3]), 2)}")
print(f"Z: {round(float(T_prueba[2,3]), 2)}")
print("="*35 + "\n")

# ==========================================
# PUNTO OBJETIVO
# ==========================================
print("=== CÁLCULO DE CINEMÁTICA INVERSA ===")
Xd = float(input("Ingrese X: "))
Yd = float(input("Ingrese Y: "))
Zd = float(input("Ingrese Z: "))

# ==========================================
# ORIENTACIÓN DE MUÑECA
# ==========================================
q4_fijo = 0

# ==========================================
# ECUACIONES
# ==========================================
eq1 = Px.subs(q4, q4_fijo) - Xd
eq2 = Py.subs(q4, q4_fijo) - Yd
eq3 = Pz.subs(q4, q4_fijo) - Zd

# ==========================================
# SEMILLAS DE BÚSQUEDA
# ==========================================
semillas = [
    (0.1, 0.1, 0.1),
    (0.5, 0.5, 0.5),
    (1.0, 1.0, 1.0), # Esta semilla atrapará el punto de prueba inmediatamente
    (1.5, 1.0, 0.5),
    (2.0, 1.0, 1.0),
    (3.0, 1.0, 0.5),
    (-0.5, 0.5, -0.5),
    (0.0, 1.5, -1.5)
]

solucion_valida = False

# ==========================================
# BÚSQUEDA DE SOLUCIONES
# ==========================================
print("\nBuscando soluciones...")

for semilla in semillas:
    try:
        sol = nsolve(
            (eq1, eq2, eq3),
            (q1, q2, q3),
            semilla,
            verify=False
        )

        q1_deg = degrees(float(sol[0]))
        q2_deg = degrees(float(sol[1]))
        q3_deg = degrees(float(sol[2]))

        # Normalización matemática: convierte a formato 0°-360°
        q1_deg = q1_deg % 360
        q2_deg = q2_deg % 360
        q3_deg = q3_deg % 360

        print(f" -> Intento (Semilla {semilla}): q1={q1_deg:.1f}°, q2={q2_deg:.1f}°, q3={q3_deg:.1f}°")

        # Restricciones reales
        if (0 <= q1_deg <= 360 and
            0 <= q2_deg <= 180 and
            0 <= q3_deg <= 180 and
            0 <= q4_fijo <= 180):

            solucion_valida = True
            break

    except Exception:
        pass

# ==========================================
# RESULTADOS
# ==========================================
if solucion_valida:
    print("\n===================================")
    print("SOLUCIÓN ENCONTRADA")
    print("===================================")

    print("q1 =", round(q1_deg, 2), "°")
    print("q2 =", round(q2_deg, 2), "°")
    print("q3 =", round(q3_deg, 2), "°")
    print("q4 =", q4_fijo, "°")

    T_num = T04.subs({
        q1: radians(q1_deg),
        q2: radians(q2_deg),
        q3: radians(q3_deg),
        q4: radians(q4_fijo)
    })

    print("\n===================================")
    print("VERIFICACIÓN")
    print("===================================")

    print("X calculado =", round(float(T_num[0,3]), 2))
    print("Y calculado =", round(float(T_num[1,3]), 2))
    print("Z calculado =", round(float(T_num[2,3]), 2))

else:
    print("\n===================================")
    print("ERROR DE ALCANCE")
    print("===================================")
    print("No existe una solución válida dentro de las")
    print("restricciones físicas de los servomotores.")


import math

# ==========================================
# CÁLCULO DE ERROR NUMÉRICO
# ==========================================

# 1. Extraemos las coordenadas calculadas (obtenidas) de la matriz T_num
Xo = float(T_num[0, 3])
Yo = float(T_num[1, 3])
Zo = float(T_num[2, 3])

# 2. Calculamos los errores absolutos por cada eje
ex = abs(Xd - Xo)
ey = abs(Yd - Yo)
ez = abs(Zd - Zo)

# 3. Calculamos el error total (raíz de la suma de los cuadrados)
e_total = math.sqrt(ex**2 + ey**2 + ez**2)

# ==========================================
# IMPRESIÓN DE LA TABLA DE ERRORES
# ==========================================
print("\n" + "="*35)
print(" 4. Error numérico")
print("="*35)
print(f"{'Error':<10} | {'Valor'}")
print("-" * 35)
print(f"ex         | {ex:.5f} mm")
print(f"ey         | {ey:.5f} mm")
print(f"ez         | {ez:.5f} mm")
print("-" * 35)
print(f"e (Total)  | {e_total:.5f} mm")
print("===================================")



from sympy import *
from math import degrees, radians, sqrt

# ==========================================
# VARIABLES SIMBÓLICAS
# ==========================================
q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# ==========================================
# PARÁMETROS DEL ROBOT
# ==========================================
d1 = 30.78
a2 = 87.00
a3 = 87.00
a4 = 171.14

# ==========================================
# MATRIZ DH
# ==========================================
def DH(theta, d, a, alpha):
    return Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])

# ==========================================
# TABLA DH DE TU ROBOT
# ==========================================
A1 = DH(q1 + pi/2, d1, 0, -pi/2)
A2 = DH(q2 + 53.88*pi/180, 0, a2, 0)
A3 = DH(q3 - 69.17*pi/180, 0, a3, 0)
A4 = DH(q4 - 13.86*pi/180, 0, a4, 0)

# ==========================================
# CINEMÁTICA DIRECTA
# ==========================================
print("Calculando cinemática directa base... (por favor espera unos segundos)")
T04 = simplify(A1*A2*A3*A4)

Pz = simplify(T04[2,3])
Px = simplify(T04[0,3])
Py = simplify(T04[1,3])

# ==========================================
# PUNTO OBJETIVO
# ==========================================
print("\n" + "="*35)
print("=== CÁLCULO DE CINEMÁTICA INVERSA ===")
Xd = float(input("Ingrese X: "))
Yd = float(input("Ingrese Y: "))
Zd = float(input("Ingrese Z: "))

# ==========================================
# ORIENTACIÓN DE MUÑECA
# ==========================================
q4_fijo = 0

# ==========================================
# ECUACIONES
# ==========================================
eq1 = Px.subs(q4, q4_fijo) - Xd
eq2 = Py.subs(q4, q4_fijo) - Yd
eq3 = Pz.subs(q4, q4_fijo) - Zd

# ==========================================
# SEMILLAS DE BÚSQUEDA
# ==========================================
# Añadimos semillas contrastantes para forzar las posturas de codo arriba y abajo
semillas = [
    (0.1, 0.1, 0.1),
    (0.5, 0.5, 0.5),
    (1.0, 1.0, 1.0),
    (1.5, 1.0, 0.5),
    (0.5, 2.0, 0.5),  # Semilla apuntando a codo arriba/abajo alterno
    (2.0, 1.0, 1.0),
    (3.0, 1.0, 0.5),
    (-0.5, 0.5, -0.5),
    (0.0, 1.5, -1.5)
]

soluciones_encontradas = []

# ==========================================
# BÚSQUEDA DE SOLUCIONES
# ==========================================
print("\nBuscando configuraciones posibles (Codo Arriba / Codo Abajo)...")

for semilla in semillas:
    try:
        sol = nsolve(
            (eq1, eq2, eq3),
            (q1, q2, q3),
            semilla,
            verify=False
        )

        q1_deg = degrees(float(sol[0]))
        q2_deg = degrees(float(sol[1]))
        q3_deg = degrees(float(sol[2]))

        # Normalización a formato 0°-360°
        q1_deg = q1_deg % 360
        q2_deg = q2_deg % 360
        q3_deg = q3_deg % 360

        # Restricciones físicas de tus motores
        if (0 <= q1_deg <= 360 and
            0 <= q2_deg <= 180 and
            0 <= q3_deg <= 180):

            # Verificar si esta solución es nueva o si el solver solo repitió una anterior
            es_nueva = True
            for sol_guardada in soluciones_encontradas:
                # Si la diferencia entre los ángulos es menor a 1 grado, es la misma postura
                if (abs(q1_deg - sol_guardada[0]) < 1.0 and
                    abs(q2_deg - sol_guardada[1]) < 1.0 and
                    abs(q3_deg - sol_guardada[2]) < 1.0):
                    es_nueva = False
                    break

            # Si es una postura completamente nueva, la guardamos
            if es_nueva:
                soluciones_encontradas.append((q1_deg, q2_deg, q3_deg))

    except Exception:
        pass

# ==========================================
# RESULTADOS, VERIFICACIÓN Y ERROR NUMÉRICO
# ==========================================
if len(soluciones_encontradas) > 0:
    print("\n" + "="*45)
    print(f"¡ÉXITO! SE ENCONTRARON {len(soluciones_encontradas)} CONFIGURACIONES VÁLIDAS")
    print("="*45)

    for i, config in enumerate(soluciones_encontradas):
        q1_res, q2_res, q3_res = config

        # Le ponemos nombre para diferenciar (Asumimos una diferencia en el codo)
        nombre_postura = "Codo Arriba" if i == 0 else "Codo Abajo"
        if len(soluciones_encontradas) == 1: nombre_postura = "Única posible"

        print(f"\n---> CONFIGURACIÓN {i+1} ({nombre_postura}) <---")
        print(f"q1 = {round(q1_res, 2)}°")
        print(f"q2 = {round(q2_res, 2)}°")
        print(f"q3 = {round(q3_res, 2)}°")
        print(f"q4 = {q4_fijo}°")

        # 1. Calculamos la cinemática directa con estos ángulos
        T_num = T04.subs({
            q1: radians(q1_res),
            q2: radians(q2_res),
            q3: radians(q3_res),
            q4: radians(q4_fijo)
        })

        Xo = float(T_num[0, 3])
        Yo = float(T_num[1, 3])
        Zo = float(T_num[2, 3])

        print("\n  [ Verificación de Posición ]")
        print(f"  X calculado = {Xo:.3f} mm")
        print(f"  Y calculado = {Yo:.3f} mm")
        print(f"  Z calculado = {Zo:.3f} mm")

        # 2. Bloque de Error Numérico
        ex = abs(Xd - Xo)
        ey = abs(Yd - Yo)
        ez = abs(Zd - Zo)
        e_total = sqrt(ex**2 + ey**2 + ez**2)

        print("\n  [ 4. Error Numérico ]")
        print(f"  {'Eje':<5} | {'Valor'}")
        print("  " + "-"*25)
        print(f"  {'ex':<5} | {ex:.6f} mm")
        print(f"  {'ey':<5} | {ey:.6f} mm")
        print(f"  {'ez':<5} | {ez:.6f} mm")
        print("  " + "-"*25)
        print(f"  {'e':<5} | {e_total:.6f} mm")
        print("-" * 45)

else:
    print("\n===================================")
    print("ERROR DE ALCANCE")
    print("===================================")
    print("No existe ninguna solución válida dentro de las")
    print("restricciones físicas de los servomotores [0° a 180°].")



from sympy import *
from math import radians

# =====================================================
# VARIABLES SIMBÓLICAS
# =====================================================

q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# =====================================================
# MATRIZ DH
# =====================================================

def DH(theta, d, a, alpha):
    return Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])

# =====================================================
# PARÁMETROS DEL ROBOT
# =====================================================

d1 = 30.78
a2 = 87
a3 = 87
a4 = 171.14

# =====================================================
# MATRICES DH
# =====================================================

A1 = DH(q1 + pi/2, d1, 0, -pi/2)
A2 = DH(q2 + 53.88*pi/180, 0, a2, 0)
A3 = DH(q3 - 69.17*pi/180, 0, a3, 0)
A4 = DH(q4 - 13.86*pi/180, 0, a4, 0)

# =====================================================
# TRANSFORMACIONES HOMOGÉNEAS
# =====================================================

T01 = simplify(A1)
T02 = simplify(A1*A2)
T03 = simplify(A1*A2*A3)
T04 = simplify(A1*A2*A3*A4)

# =====================================================
# ORÍGENES
# =====================================================

O0 = Matrix([0,0,0])

O1 = T01[0:3,3]
O2 = T02[0:3,3]
O3 = T03[0:3,3]
O4 = T04[0:3,3]

# =====================================================
# EJES Z
# =====================================================

Z0 = Matrix([0,0,1])

Z1 = T01[0:3,2]
Z2 = T02[0:3,2]
Z3 = T03[0:3,2]

# =====================================================
# JACOBIANO LINEAL
# Ji = Zi-1 × (On - Oi-1)
# =====================================================

Jv1 = simplify(Z0.cross(O4 - O0))
Jv2 = simplify(Z1.cross(O4 - O1))
Jv3 = simplify(Z2.cross(O4 - O2))
Jv4 = simplify(Z3.cross(O4 - O3))

Jv = Matrix.hstack(Jv1, Jv2, Jv3, Jv4)

# =====================================================
# JACOBIANO ANGULAR
# Revolutas -> Zi-1
# =====================================================

Jw1 = Z0
Jw2 = Z1
Jw3 = Z2
Jw4 = Z3

Jw = Matrix.hstack(Jw1, Jw2, Jw3, Jw4)

# =====================================================
# JACOBIANO COMPLETO
# =====================================================

J = Matrix.vstack(Jv, Jw)

# =====================================================
# RESULTADOS SIMBÓLICOS
# =====================================================

print("\n========================================")
print("ORÍGENES")
print("========================================")

print("\nO0 =")
pprint(O0)

print("\nO1 =")
pprint(simplify(O1))

print("\nO2 =")
pprint(simplify(O2))

print("\nO3 =")
pprint(simplify(O3))

print("\nO4 =")
pprint(simplify(O4))

print("\n========================================")
print("VECTORES Z")
print("========================================")

print("\nZ0 =")
pprint(Z0)

print("\nZ1 =")
pprint(simplify(Z1))

print("\nZ2 =")
pprint(simplify(Z2))

print("\nZ3 =")
pprint(simplify(Z3))

print("\n========================================")
print("JACOBIANO LINEAL Jv")
print("========================================")

pprint(simplify(Jv))

print("\nDimensiones Jv =", Jv.shape)

print("\n========================================")
print("JACOBIANO ANGULAR Jw")
print("========================================")

pprint(simplify(Jw))

print("\nDimensiones Jw =", Jw.shape)

print("\n========================================")
print("JACOBIANO COMPLETO")
print("========================================")

pprint(simplify(J))

print("\nDimensiones J =", J.shape)

# =====================================================
# EVALUACIÓN NUMÉRICA
# =====================================================

print("\n========================================")
print("EVALUACIÓN NUMÉRICA")
print("========================================")

q1g = float(input("Ingrese q1 (grados): "))
q2g = float(input("Ingrese q2 (grados): "))
q3g = float(input("Ingrese q3 (grados): "))
q4g = float(input("Ingrese q4 (grados): "))

valores = {
    q1:radians(q1g),
    q2:radians(q2g),
    q3:radians(q3g),
    q4:radians(q4g)
}

J_num = N(J.subs(valores),4)

print("\nJacobiano Evaluado:")

pprint(J_num)

from sympy import *
from math import radians

# =====================================================
# VARIABLES SIMBÓLICAS
# =====================================================

q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# =====================================================
# MATRIZ DH
# =====================================================

def DH(theta, d, a, alpha):
    return Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])

# =====================================================
# PARÁMETROS DEL ROBOT
# =====================================================

d1 = 30.78
a2 = 87
a3 = 87
a4 = 171.14

# =====================================================
# MATRICES DH
# =====================================================

A1 = DH(q1 + pi/2, d1, 0, -pi/2)
A2 = DH(q2 + 53.88*pi/180, 0, a2, 0)
A3 = DH(q3 - 69.17*pi/180, 0, a3, 0)
A4 = DH(q4 - 13.86*pi/180, 0, a4, 0)

# =====================================================
# TRANSFORMACIONES HOMOGÉNEAS
# =====================================================

T01 = simplify(A1)
T02 = simplify(A1*A2)
T03 = simplify(A1*A2*A3)
T04 = simplify(A1*A2*A3*A4)

# =====================================================
# ORÍGENES
# =====================================================

O0 = Matrix([0,0,0])

O1 = T01[0:3,3]
O2 = T02[0:3,3]
O3 = T03[0:3,3]
O4 = T04[0:3,3]

# =====================================================
# EJES Z
# =====================================================

Z0 = Matrix([0,0,1])

Z1 = T01[0:3,2]
Z2 = T02[0:3,2]
Z3 = T03[0:3,2]

# =====================================================
# JACOBIANO LINEAL
# Ji = Zi-1 × (On - Oi-1)
# =====================================================

Jv1 = simplify(Z0.cross(O4 - O0))
Jv2 = simplify(Z1.cross(O4 - O1))
Jv3 = simplify(Z2.cross(O4 - O2))
Jv4 = simplify(Z3.cross(O4 - O3))

Jv = Matrix.hstack(Jv1, Jv2, Jv3, Jv4)

# =====================================================
# JACOBIANO ANGULAR
# Revolutas -> Zi-1
# =====================================================

Jw1 = Z0
Jw2 = Z1
Jw3 = Z2
Jw4 = Z3

Jw = Matrix.hstack(Jw1, Jw2, Jw3, Jw4)

# =====================================================
# JACOBIANO COMPLETO
# =====================================================

J = Matrix.vstack(Jv, Jw)

# =====================================================
# RESULTADOS SIMBÓLICOS
# =====================================================

print("\n========================================")
print("ORÍGENES")
print("========================================")

print("\nO0 =")
pprint(O0)

print("\nO1 =")
pprint(simplify(O1))

print("\nO2 =")
pprint(simplify(O2))

print("\nO3 =")
pprint(simplify(O3))

print("\nO4 =")
pprint(simplify(O4))

print("\n========================================")
print("VECTORES Z")
print("========================================")

print("\nZ0 =")
pprint(Z0)

print("\nZ1 =")
pprint(simplify(Z1))

print("\nZ2 =")
pprint(simplify(Z2))

print("\nZ3 =")
pprint(simplify(Z3))

print("\n========================================")
print("JACOBIANO LINEAL Jv")
print("========================================")

pprint(simplify(Jv))

print("\nDimensiones Jv =", Jv.shape)

print("\n========================================")
print("JACOBIANO ANGULAR Jw")
print("========================================")

pprint(simplify(Jw))

print("\nDimensiones Jw =", Jw.shape)

print("\n========================================")
print("JACOBIANO COMPLETO")
print("========================================")

pprint(simplify(J))

print("\nDimensiones J =", J.shape)

# =====================================================
# EVALUACIÓN NUMÉRICA
# =====================================================

print("\n========================================")
print("EVALUACIÓN NUMÉRICA")
print("========================================")

q1g = float(input("Ingrese q1 (grados): "))
q2g = float(input("Ingrese q2 (grados): "))
q3g = float(input("Ingrese q3 (grados): "))
q4g = float(input("Ingrese q4 (grados): "))

valores = {
    q1: radians(q1g),
    q2: radians(q2g),
    q3: radians(q3g),
    q4: radians(q4g)
}

# Evalúa la matriz con los valores ingresados y redondea cada elemento a 3 decimales exactos
J_num = J.subs(valores).evalf().applyfunc(lambda x: round(x, 3))

print("\nJacobiano Evaluado (Redondeado a 3 decimales):")
pprint(J_num)


from sympy import *
from math import radians

# =====================================================
# VARIABLES SIMBÓLICAS
# =====================================================

q1, q2, q3, q4 = symbols('q1 q2 q3 q4')

# =====================================================
# MATRIZ DH
# =====================================================

def DH(theta, d, a, alpha):
    return Matrix([
        [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
        [0,           sin(alpha),             cos(alpha),            d],
        [0,           0,                      0,                     1]
    ])

# =====================================================
# PARÁMETROS DEL ROBOT
# =====================================================

d1 = 30.78
a2 = 87
a3 = 87
a4 = 171.14

# =====================================================
# MATRICES DH
# =====================================================

A1 = DH(q1 + pi/2, d1, 0, -pi/2)
A2 = DH(q2 + 53.88*pi/180, 0, a2, 0)
A3 = DH(q3 - 69.17*pi/180, 0, a3, 0)
A4 = DH(q4 - 13.86*pi/180, 0, a4, 0)

# =====================================================
# TRANSFORMACIONES HOMOGÉNEAS
# =====================================================

T01 = simplify(A1)
T02 = simplify(A1*A2)
T03 = simplify(A1*A2*A3)
T04 = simplify(A1*A2*A3*A4)

# =====================================================
# ORÍGENES
# =====================================================

O0 = Matrix([0,0,0])

O1 = T01[0:3,3]
O2 = T02[0:3,3]
O3 = T03[0:3,3]
O4 = T04[0:3,3]

# =====================================================
# EJES Z
# =====================================================

Z0 = Matrix([0,0,1])

Z1 = T01[0:3,2]
Z2 = T02[0:3,2]
Z3 = T03[0:3,2]

# =====================================================
# JACOBIANO LINEAL
# Ji = Zi-1 × (On - Oi-1)
# =====================================================

Jv1 = simplify(Z0.cross(O4 - O0))
Jv2 = simplify(Z1.cross(O4 - O1))
Jv3 = simplify(Z2.cross(O4 - O2))
Jv4 = simplify(Z3.cross(O4 - O3))

Jv = Matrix.hstack(Jv1, Jv2, Jv3, Jv4)

# =====================================================
# JACOBIANO ANGULAR
# Revolutas -> Zi-1
# =====================================================

Jw1 = Z0
Jw2 = Z1
Jw3 = Z2
Jw4 = Z3

Jw = Matrix.hstack(Jw1, Jw2, Jw3, Jw4)

# =====================================================
# JACOBIANO COMPLETO
# =====================================================

J = Matrix.vstack(Jv, Jw)

# =====================================================
# RESULTADOS SIMBÓLICOS
# =====================================================

print("\n========================================")
print("ORÍGENES")
print("========================================")

print("\nO0 =")
pprint(O0)

print("\nO1 =")
pprint(simplify(O1))

print("\nO2 =")
pprint(simplify(O2))

print("\nO3 =")
pprint(simplify(O3))

print("\nO4 =")
pprint(simplify(O4))

print("\n========================================")
print("VECTORES Z")
print("========================================")

print("\nZ0 =")
pprint(Z0)

print("\nZ1 =")
pprint(simplify(Z1))

print("\nZ2 =")
pprint(simplify(Z2))

print("\nZ3 =")
pprint(simplify(Z3))

print("\n========================================")
print("JACOBIANO LINEAL Jv")
print("========================================")

pprint(simplify(Jv))

print("\nDimensiones Jv =", Jv.shape)

print("\n========================================")
print("JACOBIANO ANGULAR Jw")
print("========================================")

pprint(simplify(Jw))

print("\nDimensiones Jw =", Jw.shape)

print("\n========================================")
print("JACOBIANO COMPLETO")
print("========================================")

pprint(simplify(J))

print("\nDimensiones J =", J.shape)

# =====================================================
# EVALUACIÓN NUMÉRICA
# =====================================================

print("\n========================================")
print("EVALUACIÓN NUMÉRICA")
print("========================================")

q1g = float(input("Ingrese q1 (grados): "))
q2g = float(input("Ingrese q2 (grados): "))
q3g = float(input("Ingrese q3 (grados): "))
q4g = float(input("Ingrese q4 (grados): "))

valores = {
    q1: radians(q1g),
    q2: radians(q2g),
    q3: radians(q3g),
    q4: radians(q4g)
}

# Evalúa la matriz con los valores ingresados y redondea cada elemento a 3 decimales exactos
J_num = J.subs(valores).evalf().applyfunc(lambda x: round(x, 3))

print("\nJacobiano Evaluado (Redondeado a 3 decimales):")
pprint(J_num)


import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# 1. PARÁMETROS DEL ROBOT
# =====================================================================

L1 = 1.2
L2 = 0.8

# =====================================================================
# 2. CINEMÁTICA DIRECTA
# =====================================================================

def cinematica_directa(q1, q2):
    x = L1*np.cos(q1) + L2*np.cos(q1 + q2)
    y = L1*np.sin(q1) + L2*np.sin(q1 + q2)
    return x, y

# =====================================================================
# 3. JACOBIANO DEL ROBOT 2R
# =====================================================================

def jacobiano(q1, q2):
    J = np.array([
        [-L1*np.sin(q1) - L2*np.sin(q1 + q2), -L2*np.sin(q1 + q2)],
        [ L1*np.cos(q1) + L2*np.cos(q1 + q2),  L2*np.cos(q1 + q2)]
    ])
    return J

# =====================================================================
# 4. DETERMINANTE DEL JACOBIANO
# =====================================================================

def determinante_jacobiano(q1, q2):
    J = jacobiano(q1, q2)
    return np.linalg.det(J)

# =====================================================================
# 5. MAPA DE SINGULARIDADES EN EL ESPACIO ARTICULAR
# =====================================================================

q1_vals = np.linspace(-np.pi, np.pi, 200)
q2_vals = np.linspace(-np.pi, np.pi, 200)

Q1, Q2 = np.meshgrid(q1_vals, q2_vals)

DET = np.zeros_like(Q1)

for i in range(Q1.shape[0]):
    for j in range(Q1.shape[1]):
        DET[i, j] = determinante_jacobiano(Q1[i, j], Q2[i, j])

plt.figure(figsize=(8, 6))
plt.contourf(Q1, Q2, DET, levels=50)
plt.colorbar(label="Determinante del Jacobiano")
plt.contour(Q1, Q2, DET, levels=[0], linewidths=3)
plt.xlabel("q1 [rad]")
plt.ylabel("q2 [rad]")
plt.title("Mapa de singularidades del robot planar 2R")
plt.grid(True)
plt.show()

# =====================================================================
# 6. CINEMÁTICA INVERSA PARA ROBOT 2R
# =====================================================================

def cinematica_inversa(x, y):
    r2 = x**2 + y**2

    cos_q2 = (r2 - L1**2 - L2**2) / (2*L1*L2)

    # Se limita el valor para evitar errores numéricos
    cos_q2 = np.clip(cos_q2, -1, 1)

    q2 = np.arccos(cos_q2)

    k1 = L1 + L2*np.cos(q2)
    k2 = L2*np.sin(q2)

    q1 = np.arctan2(y, x) - np.arctan2(k2, k1)

    return q1, q2

# =====================================================================
# 7. TRAYECTORIA CIRCULAR DEL EFECTOR FINAL
# =====================================================================

centro_x = 0.9
centro_y = 0.4
radio = 0.25

t = np.linspace(0, 2*np.pi, 150)

x_tray = centro_x + radio*np.cos(t)
y_tray = centro_y + radio*np.sin(t)

q1_tray = []
q2_tray = []
det_tray = []

for x, y in zip(x_tray, y_tray):
    q1, q2 = cinematica_inversa(x, y)
    q1_tray.append(q1)
    q2_tray.append(q2)
    det_tray.append(determinante_jacobiano(q1, q2))

q1_tray = np.array(q1_tray)
q2_tray = np.array(q2_tray)
det_tray = np.array(det_tray)

# =====================================================================
# 8. GRÁFICA DE LA TRAYECTORIA EN EL ESPACIO CARTESIANO
# =====================================================================

plt.figure(figsize=(7, 7))
plt.plot(x_tray, y_tray, linewidth=3, label="Trayectoria deseada")
plt.scatter(x_tray[0], y_tray[0], label="Inicio")
plt.scatter(x_tray[-1], y_tray[-1], label="Final")
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.title("Trayectoria circular del efector final")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.show()