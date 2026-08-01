"""Datos de demostración.

La siembra cuenta la historia del producto: **un profesor, dos materias, cinco
grupos, cinco puntos distintos del temario**. El 1CV1 de Cálculo va al corriente,
el 2CV2 perdió una sesión por un puente y el 3CV3 se quedó a medias de un tema
por un simulacro. Encima, el grupo 1CV1 lleva las dos materias con el mismo
profesor, así que el ciclo se ve como un sistema y no como asignaturas sueltas.

Las fechas se generan **relativas a hoy**: la última sesión de cada grupo cae en
la semana en curso, para que la agenda semanal siempre tenga contenido vivo sin
importar cuándo se ejecute la demostración.

En Render el disco es efímero, así que esto corre en cada arranque si la base
está vacía.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from sqlmodel import Session, select

from .db import motor
from .models import Cobertura, Grupo, Materia, MensajeChat, Sesion, Tema

SEMANAS_DE_HISTORIA = 10

DIAS_NOMBRE = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}

# (título de la clase, [(orden_tema, nivel)], resumen, puntos, dónde quedó, pendientes, transcripción)
CALCULO_1CV1 = [
    ("Desigualdades y notación de intervalos", [(1, "cubierto")],
     "Arrancamos el curso con las propiedades de orden de los números reales y la notación "
     "de intervalos. Se resolvieron desigualdades lineales y una cuadrática por el método de "
     "la recta numérica con puntos críticos.",
     ["Al multiplicar por un negativo se invierte el sentido de la desigualdad",
      "La solución de una desigualdad es un conjunto, no un número",
      "Los puntos críticos parten la recta en regiones de signo constante"],
     "Terminamos con la desigualdad cuadrática x²-5x+6>0 resuelta por regiones.",
     ["Traer ejercicios 1 a 15 de la guía"],
     "Buenos días. Vamos a empezar Cálculo con algo que ya vieron en el propedéutico pero que "
     "aquí usamos todo el semestre: desigualdades. Si a es menor que b y multiplico ambos lados "
     "por menos dos, el sentido se invierte, eso es lo que más se les olvida. La notación de "
     "intervalo abierto usa paréntesis, el cerrado usa corchete. Ahora x cuadrada menos cinco x "
     "más seis mayor que cero. Factorizo: x menos dos por x menos tres. Los puntos críticos son "
     "dos y tres. Pruebo un valor en cada región y me quedo con las que dan positivo: menos "
     "infinito a dos, unión, tres a infinito."),
    ("Valor absoluto y distancia", [(2, "cubierto")],
     "Se definió el valor absoluto como distancia al origen y se resolvieron desigualdades del "
     "tipo |x-a|<r interpretándolas geométricamente.",
     ["|x| es la distancia de x al cero, nunca es negativo",
      "|x-a|<r equivale a que x esté a menos de r unidades de a",
      "|x|>r se parte en dos casos"],
     "Quedamos en la interpretación geométrica de |x-3|<2 como el intervalo (1,5).",
     [],
     "El valor absoluto no es quitar el signo, es la distancia al origen. Si les digo valor "
     "absoluto de x menos tres menor que dos, no memoricen la fórmula: pregúntense qué números "
     "están a menos de dos unidades del tres. Del uno al cinco. Ya está, ese es el intervalo. "
     "Cuando es mayor que, es al revés, se van para afuera y son dos intervalos separados."),
    ("Concepto de función, dominio y rango", [(3, "cubierto")],
     "Definición de función como regla de correspondencia, criterio de la recta vertical, y "
     "cálculo de dominio para funciones con radical y con denominador.",
     ["Una función asigna a cada entrada exactamente una salida",
      "El dominio se restringe donde el denominador se anula o el radicando es negativo",
      "El criterio de la recta vertical decide si una gráfica es función"],
     "Terminamos calculando el dominio de f(x)=√(x-4)/(x-7).",
     ["Repasar dominios con radical par"],
     "Una función es una regla que a cada entrada le asigna una y solo una salida. Si trazo una "
     "recta vertical y toca la gráfica dos veces, no es función. Para el dominio hay dos "
     "preguntas: qué anula el denominador y qué hace negativo lo de adentro de una raíz par. En "
     "raíz de x menos cuatro sobre x menos siete, necesito x mayor o igual que cuatro, pero "
     "además x distinto de siete. El dominio es de cuatro a siete, unión, siete a infinito."),
    ("Tipos de funciones y transformaciones", [(4, "cubierto")],
     "Clasificación entre funciones algebraicas y trascendentes, paridad, y el efecto de las "
     "traslaciones y reflexiones sobre la gráfica.",
     ["f(x)+c sube la gráfica, f(x+c) la mueve a la izquierda",
      "Una función par es simétrica respecto al eje y; una impar, respecto al origen",
      "El signo menos por fuera refleja sobre el eje x"],
     "Quedamos graficando f(x)=-(x+2)²+3 por transformaciones sucesivas.",
     [],
     "Fíjense en lo contraintuitivo: el más c por dentro mueve la gráfica a la izquierda, no a "
     "la derecha. Con la parábola menos x más dos al cuadrado más tres: parto de x cuadrada, la "
     "corro dos a la izquierda, la reflejo porque hay un menos, y la subo tres. El vértice queda "
     "en menos dos, tres, y abre hacia abajo. Los que llevan Geometría conmigo van a reconocer "
     "esta parábola cuando veamos foco y directriz."),
    ("Álgebra de funciones y composición", [(5, "cubierto")],
     "Operaciones entre funciones, composición y su dominio, e introducción a la función inversa "
     "a partir del criterio de la recta horizontal.",
     ["El dominio de f∘g exige que g(x) esté en el dominio de f",
      "La composición no es conmutativa",
      "Solo las funciones inyectivas tienen inversa"],
     "Cerramos con f∘g y g∘f para f(x)=√x y g(x)=x-3, comparando dominios.",
     ["Ejercicios de composición de la guía"],
     "Componer no es multiplicar. F de g de x significa que primero aplico g y el resultado se "
     "lo doy a f. Con f igual a raíz de x y g igual a x menos tres, f de g de x es raíz de x "
     "menos tres, y su dominio es x mayor o igual que tres. Al revés, g de f de x es raíz de x "
     "menos tres, con dominio x mayor o igual que cero. Distinto resultado y distinto dominio: "
     "por eso el orden importa."),
    ("Noción intuitiva de límite", [(6, "cubierto")],
     "Aproximación numérica por tablas y lectura gráfica del límite. Se insistió en que el "
     "límite describe la tendencia, no el valor de la función en el punto.",
     ["El límite no exige que la función esté definida en el punto",
      "Se puede aproximar por tablas desde ambos lados",
      "Si los lados no coinciden, el límite no existe"],
     "Terminamos con la tabla de (x²-1)/(x-1) acercándose a 1 desde ambos lados.",
     [],
     "El límite pregunta a dónde tiende la función cuando x se acerca, no cuánto vale cuando "
     "llega. En x cuadrada menos uno sobre x menos uno, si sustituyo uno me da cero sobre cero, "
     "indefinido. Pero hago la tabla: con nueve décimos me da uno punto nueve, con noventa y "
     "nueve centésimos me da uno punto noventa y nueve. Por arriba, igual. La función tiende a "
     "dos aunque en el uno tenga un hoyo."),
    ("Leyes de los límites e indeterminación 0/0", [(7, "cubierto")],
     "Se enunciaron las leyes de los límites y se trabajó la indeterminación 0/0 con "
     "factorización y con racionalización del numerador.",
     ["0/0 no es un resultado, es una señal de que hay que transformar la expresión",
      "Factorizar y cancelar el factor problemático resuelve la mayoría de los casos",
      "Con raíces se multiplica por el conjugado"],
     "Cerramos con lím(x→0) (√(x+9)-3)/x resuelto por conjugado, que da 1/6.",
     ["Estudiar racionalización para la próxima"],
     "Cuando sustituyen y les sale cero sobre cero, eso no es la respuesta, es un aviso: hay un "
     "factor común escondido. En raíz de x más nueve menos tres, sobre x, multiplico arriba y "
     "abajo por el conjugado, raíz de x más nueve más tres. Arriba me queda x más nueve menos "
     "nueve, o sea x, y se cancela con la x de abajo. Queda uno sobre raíz de x más nueve más "
     "tres, sustituyo cero y da uno sobre seis. La próxima clase vemos límites laterales, que es "
     "donde se decide si el límite existe o no."),
]

CALCULO_2CV2 = [
    ("Desigualdades y notación de intervalos", [(1, "cubierto")],
     "Propiedades de orden, intervalos y desigualdades lineales y cuadráticas resueltas por "
     "regiones en la recta numérica.",
     ["Multiplicar por un negativo invierte la desigualdad",
      "La solución es un conjunto de números",
      "Los puntos críticos definen las regiones de prueba"],
     "Terminamos con desigualdades cuadráticas por el método de regiones.", [],
     "Propiedades de orden primero. Si multiplican por un número negativo, el símbolo se voltea. "
     "Notación de intervalos: paréntesis para abierto, corchete para cerrado. Con la cuadrática "
     "factorizo, saco puntos críticos y pruebo signos por región."),
    ("Valor absoluto", [(2, "cubierto")],
     "Valor absoluto como distancia, propiedades y desigualdades con valor absoluto.",
     ["|x| es distancia al origen", "|x-a|<r es un intervalo centrado en a",
      "El caso 'mayor que' produce dos intervalos"],
     "Quedamos resolviendo |2x-1|≥5.", [],
     "Valor absoluto es distancia, no es quitar signos. Menor que se convierte en un intervalo "
     "centrado; mayor que se abre en dos. En dos x menos uno, mayor o igual que cinco, planteo "
     "los dos casos y me quedan dos rayos."),
    ("Concepto de función, dominio y rango", [(3, "cubierto")],
     "Definición de función, criterio de la recta vertical y cálculo de dominios con radicales "
     "y denominadores.",
     ["Cada entrada tiene exactamente una salida",
      "Denominador distinto de cero y radicando no negativo",
      "El rango se lee en el eje vertical"],
     "Terminamos con el dominio de funciones racionales con radical.",
     ["Repasar factorización para dominios"],
     "Función es una regla que asigna una sola salida a cada entrada. Recta vertical para "
     "verificar. Para el dominio, dos preguntas: qué anula el denominador y qué vuelve negativo "
     "el radicando de una raíz par."),
    ("Tipos de funciones y transformaciones", [(4, "cubierto")],
     "Clasificación de funciones, paridad y transformaciones de la gráfica.",
     ["f(x)+c traslada verticalmente",
      "f(x+c) traslada horizontalmente en sentido opuesto",
      "Par es simétrica al eje y, impar al origen"],
     "Cerramos graficando parábolas por transformaciones.", [],
     "El más c por dentro mueve a la izquierda, es lo que siempre confunde. Par significa "
     "simetría respecto al eje y; impar, respecto al origen. Practiquen graficando parábolas "
     "corridas y reflejadas."),
    ("Álgebra de funciones y composición", [(5, "cubierto")],
     "Operaciones entre funciones y composición, con énfasis en el dominio del resultado. La "
     "sesión anterior se perdió por el puente, así que se retomó con un repaso breve de dominios "
     "antes de entrar al tema.",
     ["f∘g exige que g(x) caiga en el dominio de f",
      "La composición no es conmutativa",
      "El dominio de la composición puede ser más chico que el de ambas"],
     "Terminamos con el dominio de f∘g para f(x)=1/x y g(x)=x-2. Falta la función inversa.",
     ["Ver función inversa la próxima sesión", "Recuperar el ritmo perdido por el puente"],
     "Perdimos la del martes por el puente, así que vamos a apretar un poco. Repaso rápido de "
     "dominios y entramos a composición. F de g de x quiere decir que primero aplico g. Con f "
     "igual a uno sobre x y g igual a x menos dos, la composición es uno sobre x menos dos, y el "
     "dominio excluye el dos. Nos faltó función inversa, la vemos la próxima clase antes de "
     "entrar a límites."),
]

CALCULO_3CV3 = [
    ("Desigualdades y notación de intervalos", [(1, "cubierto")],
     "Propiedades de orden, intervalos y desigualdades resueltas por regiones.",
     ["El sentido se invierte al multiplicar por negativos", "La solución es un conjunto",
      "Puntos críticos y prueba de signos"],
     "Terminamos con desigualdades cuadráticas.", [],
     "Orden en los reales, notación de intervalos y desigualdades. Con la cuadrática, factorizo, "
     "ubico puntos críticos y pruebo el signo en cada región."),
    ("Valor absoluto y distancia", [(2, "cubierto")],
     "Valor absoluto como distancia al origen y desigualdades asociadas.",
     ["|x| nunca es negativo", "|x-a|<r es un intervalo centrado",
      "Mayor que abre dos intervalos"],
     "Quedamos en la interpretación geométrica de las desigualdades.", [],
     "Piénsenlo como distancia. Valor absoluto de x menos tres menor que dos son los números a "
     "menos de dos unidades del tres, o sea del uno al cinco."),
    ("Concepto de función, dominio y rango", [(3, "cubierto")],
     "Definición de función, recta vertical y cálculo de dominios.",
     ["Una salida por entrada", "Denominador no nulo, radicando no negativo",
      "Rango en el eje vertical"],
     "Terminamos con dominios de funciones con radical.", [],
     "Función, dominio y rango. Recta vertical para verificar si una gráfica lo es. Dominio: "
     "cuidado con denominadores y con raíces pares."),
    ("Transformaciones y álgebra de funciones", [(4, "cubierto"), (5, "cubierto")],
     "Se juntaron transformaciones y álgebra de funciones en una sola sesión para compensar el "
     "ritmo. Se cubrió composición y su dominio.",
     ["f(x+c) traslada en sentido contrario al signo",
      "La composición no es conmutativa",
      "El dominio de la composición se hereda de ambas funciones"],
     "Cerramos con composiciones y sus dominios; la función inversa quedó apenas mencionada.",
     ["Retomar función inversa con calma"],
     "Vamos a ver dos temas hoy porque traemos el calendario apretado. Transformaciones: el más "
     "c por dentro corre a la izquierda. Y componer no es multiplicar: f de g de x significa "
     "aplicar primero g. Con raíz de x y x menos tres, la composición es raíz de x menos tres "
     "con dominio x mayor o igual que tres. De inversa solo les adelanto que necesita que la "
     "función sea inyectiva, lo vemos bien después."),
    ("Noción intuitiva de límite", [(6, "cubierto")],
     "Aproximación numérica y gráfica al concepto de límite, con tablas desde ambos lados.",
     ["El límite es tendencia, no el valor en el punto",
      "Se aproxima desde la izquierda y desde la derecha",
      "Si los lados difieren, el límite no existe"],
     "Terminamos con la tabla de (x²-1)/(x-1) cerca de x=1.", [],
     "El límite pregunta hacia dónde va la función, no cuánto vale al llegar. En x cuadrada menos "
     "uno sobre x menos uno, sustituir uno da cero sobre cero. Pero la tabla muestra que se "
     "acerca a dos por los dos lados. Hay un hueco en la gráfica, pero el límite existe y vale dos."),
    ("Inicio de leyes de los límites (sesión interrumpida)", [(7, "introducido")],
     "La sesión se cortó a los veinte minutos por el simulacro de evacuación. Solo alcanzó a "
     "enunciarse la lista de leyes de los límites y a plantearse la indeterminación 0/0, sin "
     "resolver ningún ejercicio completo.",
     ["Las leyes permiten separar límites de sumas, productos y cocientes",
      "0/0 es una indeterminación, no un resultado"],
     "Quedamos justo en el planteamiento de 0/0, sin alcanzar a resolver ejemplos.",
     ["Retomar cálculo de límites desde el principio",
      "Falta por completo factorización y racionalización"],
     "Antes de que suene la alarma del simulacro les dejo planteadas las leyes de los límites: el "
     "límite de una suma es la suma de los límites, y lo mismo con producto y cociente, siempre "
     "que el de abajo no sea cero. Cuando al sustituir les salga cero sobre cero, eso es una "
     "indeterminación, no una respuesta. Ahí es donde entra factorizar o racionalizar, pero eso "
     "ya no nos va a dar tiempo... ahí está la alarma. Salgan en orden por la puerta de atrás, "
     "seguimos la próxima clase."),
]

GEOMETRIA_1CV1 = [
    ("Sistema coordenado y lugar geométrico", [(1, "cubierto")],
     "Coordenadas cartesianas, distancia entre dos puntos y división de un segmento en una razón "
     "dada. Se introdujo la idea de lugar geométrico como conjunto de puntos que cumplen una "
     "condición.",
     ["La distancia sale del teorema de Pitágoras aplicado a las diferencias de coordenadas",
      "Un lugar geométrico es una condición traducida a ecuación",
      "El punto medio es el caso particular de razón 1:1"],
     "Terminamos con la fórmula de división de un segmento en razón r.", [],
     "Geometría analítica es traducir geometría a álgebra. La distancia entre dos puntos no es "
     "una fórmula que memoricen, es Pitágoras: la diferencia en x al cuadrado más la diferencia "
     "en y al cuadrado, todo bajo raíz. Y un lugar geométrico es una condición: si les digo los "
     "puntos que están a cinco unidades del origen, eso es una condición y su traducción es una "
     "ecuación."),
    ("La recta: pendiente y formas de la ecuación", [(2, "cubierto")],
     "Pendiente como razón de cambio, formas punto-pendiente y general de la ecuación de la "
     "recta, y condiciones de paralelismo y perpendicularidad.",
     ["La pendiente es el cambio en y entre el cambio en x",
      "Dos rectas son perpendiculares si el producto de sus pendientes es -1",
      "La forma general se obtiene igualando a cero"],
     "Quedamos obteniendo la ecuación de la perpendicular a 2x-3y+6=0 por un punto dado.", [],
     "La pendiente es una razón de cambio, y eso les va a sonar cuando en Cálculo lleguemos a la "
     "derivada: es exactamente la misma idea, pero para curvas. Punto pendiente: y menos y uno "
     "igual a m por x menos x uno. Para perpendicular, invierten la pendiente y le cambian el "
     "signo."),
    ("La circunferencia", [(3, "cubierto")],
     "Ecuación ordinaria y general de la circunferencia, obtención de centro y radio completando "
     "el trinomio cuadrado perfecto.",
     ["La ecuación ordinaria expone centro y radio de inmediato",
      "Completar el cuadrado convierte la forma general en ordinaria",
      "Si el radio al cuadrado sale negativo, no hay lugar geométrico real"],
     "Terminamos convirtiendo x²+y²-6x+4y-12=0 a su forma ordinaria.",
     ["Practicar completar el trinomio cuadrado perfecto"],
     "La circunferencia es el lugar geométrico de los puntos que equidistan de un centro. Si me "
     "dan la forma general, completo cuadrados: agrupo las x, agrupo las y, y lo que le sumo de "
     "un lado se lo sumo del otro. De x cuadrada más y cuadrada menos seis x más cuatro y menos "
     "doce igual a cero me sale centro en tres, menos dos, y radio cinco."),
    ("La parábola: foco, directriz y ecuación", [(4, "cubierto")],
     "La parábola como lugar geométrico, elementos (foco, directriz, lado recto) y ecuación con "
     "vértice en el origen y con vértice trasladado.",
     ["La parábola equidista del foco y de la directriz",
      "El parámetro p es la distancia del vértice al foco",
      "La traslación de ejes reutiliza lo visto en transformaciones de funciones"],
     "Cerramos con la parábola de vértice (2,-1) y foco (2,1), obteniendo su ecuación.", [],
     "Aquí se juntan mis dos materias. En Cálculo vimos que menos x más dos al cuadrado más tres "
     "es una parábola corrida y reflejada; aquí le vamos a poner nombre a sus partes: vértice, "
     "foco, directriz. La parábola es el lugar geométrico de los puntos que están a la misma "
     "distancia de un punto fijo y de una recta fija. El parámetro p es la distancia del vértice "
     "al foco, y define qué tan abierta es."),
]

GEOMETRIA_4CM2 = [
    ("Sistema coordenado y lugar geométrico", [(1, "cubierto")],
     "Coordenadas cartesianas, distancia entre dos puntos y punto medio. Introducción al concepto "
     "de lugar geométrico.",
     ["La distancia es Pitágoras sobre las diferencias de coordenadas",
      "El punto medio promedia coordenadas",
      "Un lugar geométrico traduce una condición a una ecuación"],
     "Terminamos con ejercicios de distancia y punto medio.", [],
     "Vamos a traducir geometría a álgebra. Distancia entre dos puntos: Pitágoras. Punto medio: "
     "promedio de las coordenadas. Y un lugar geométrico es el conjunto de puntos que cumplen "
     "una condición."),
    ("La recta: pendiente y formas de la ecuación", [(2, "cubierto")],
     "Pendiente, formas punto-pendiente y general, paralelismo y perpendicularidad.",
     ["La pendiente mide inclinación como razón de cambio",
      "Paralelas comparten pendiente",
      "Perpendiculares tienen pendientes con producto -1"],
     "Quedamos con la forma general de la recta.",
     ["Ejercicios de rectas paralelas y perpendiculares"],
     "La pendiente es el cambio en y sobre el cambio en x. De ahí sale punto pendiente. Para "
     "pasar a la forma general, paso todo de un lado e igualo a cero."),
    ("La circunferencia", [(3, "cubierto")],
     "Ecuación ordinaria y general, centro y radio por completación de cuadrados.",
     ["La forma ordinaria muestra centro y radio directo",
      "Completar cuadrados es la herramienta clave",
      "Un radio imaginario significa que no existe el lugar geométrico"],
     "Terminamos identificando centro y radio desde la forma general.", [],
     "Circunferencia: puntos que equidistan del centro. Si me dan la forma general, completo el "
     "trinomio cuadrado perfecto en x y en y para llegar a la ordinaria, y de ahí leo el centro "
     "y el radio."),
    ("Repaso y ejercicios de recta y circunferencia", [(2, "reforzado"), (3, "reforzado")],
     "Sesión de repaso previa al primer parcial, con ejercicios mixtos de recta y circunferencia. "
     "No se avanzó en temas nuevos.",
     ["Identificar qué dato falta es la mitad del problema",
      "Las condiciones de tangencia mezclan recta y circunferencia"],
     "Cerramos resolviendo la recta tangente a una circunferencia en un punto dado.",
     ["Entrar a la parábola la próxima sesión"],
     "Hoy no vemos tema nuevo, hoy resolvemos. Este grupo viene bien pero le falta soltura en "
     "ejercicios mixtos. La tangente a una circunferencia en un punto es perpendicular al radio "
     "en ese punto: con eso sale todo."),
]

MATERIAS = [
    {
        "nombre": "Cálculo Diferencial",
        "clave": "MAT-1201",
        "ciclo": "2026/1",
        "sesiones_planeadas": 32,
        "relacion": (
            "El grupo 1CV1 lleva también Geometría Analítica con la misma profesora. Las "
            "transformaciones de funciones de la Unidad 2 preparan el terreno para la traslación "
            "de ejes en cónicas, y la pendiente de la recta anticipa la derivada."
        ),
        "temario": [
            ("Unidad 1. Números reales", "Los números reales y desigualdades",
             ["Propiedades de orden", "Intervalos", "Desigualdades lineales y cuadráticas"]),
            ("Unidad 1. Números reales", "Valor absoluto",
             ["Definición y propiedades", "Desigualdades con valor absoluto", "Distancia en la recta"]),
            ("Unidad 2. Funciones", "Concepto de función",
             ["Dominio y rango", "Notación funcional", "Gráfica de una función"]),
            ("Unidad 2. Funciones", "Tipos de funciones y transformaciones",
             ["Algebraicas y trascendentes", "Funciones par e impar", "Traslaciones y reflexiones"]),
            ("Unidad 2. Funciones", "Álgebra de funciones y composición",
             ["Suma, producto y cociente", "Composición", "Función inversa"]),
            ("Unidad 3. Límites", "Noción intuitiva de límite",
             ["Aproximación numérica", "Límite por tablas y gráficas", "Notación de límite"]),
            ("Unidad 3. Límites", "Cálculo de límites",
             ["Leyes de los límites", "Indeterminación 0/0", "Factorización y racionalización"]),
            ("Unidad 3. Límites", "Límites laterales e infinitos",
             ["Límites laterales", "Asíntotas verticales", "Límites al infinito"]),
            ("Unidad 3. Límites", "Continuidad",
             ["Definición de continuidad", "Tipos de discontinuidad", "Teorema del valor intermedio"]),
            ("Unidad 4. La derivada", "La derivada",
             ["Razón de cambio", "Definición por límite", "Interpretación geométrica"]),
            ("Unidad 4. La derivada", "Reglas de derivación",
             ["Potencia, producto y cociente", "Regla de la cadena", "Derivadas de orden superior"]),
            ("Unidad 5. Aplicaciones", "Aplicaciones de la derivada",
             ["Máximos y mínimos", "Criterio de la primera derivada", "Optimización"]),
        ],
        "grupos": [
            {"nombre": "1CV1", "dias": [1, 3], "inicio": "07:00", "fin": "08:30",
             "alumnos": 42, "clases": CALCULO_1CV1, "saltos": []},
            # El 2CV2 perdió la quinta sesión del calendario por el puente.
            {"nombre": "2CV2", "dias": [2, 4], "inicio": "12:30", "fin": "14:00",
             "alumnos": 38, "clases": CALCULO_2CV2, "saltos": [4]},
            {"nombre": "3CV3", "dias": [1, 5], "inicio": "18:00", "fin": "19:30",
             "alumnos": 45, "clases": CALCULO_3CV3, "saltos": []},
        ],
    },
    {
        "nombre": "Geometría Analítica",
        "clave": "MAT-1202",
        "ciclo": "2026/1",
        "sesiones_planeadas": 28,
        "relacion": (
            "Comparte el grupo 1CV1 con Cálculo Diferencial: son los mismos alumnos en las dos "
            "materias. La traslación de ejes en cónicas se apoya en las transformaciones de "
            "funciones que ese grupo ya vio en Cálculo."
        ),
        "temario": [
            ("Unidad 1. El plano", "Sistema coordenado y lugar geométrico",
             ["Coordenadas cartesianas", "Distancia entre dos puntos", "División de un segmento"]),
            ("Unidad 1. El plano", "La recta",
             ["Pendiente", "Formas de la ecuación", "Rectas paralelas y perpendiculares"]),
            ("Unidad 2. Cónicas", "La circunferencia",
             ["Ecuación ordinaria y general", "Centro y radio", "Condiciones de tangencia"]),
            ("Unidad 2. Cónicas", "La parábola",
             ["Foco y directriz", "Lado recto", "Traslación de ejes"]),
            ("Unidad 2. Cónicas", "La elipse",
             ["Ecuación y elementos", "Excentricidad", "Traslación de ejes"]),
            ("Unidad 2. Cónicas", "La hipérbola",
             ["Ecuación y elementos", "Asíntotas", "Excentricidad"]),
            ("Unidad 3. Segundo grado", "Ecuación general de segundo grado",
             ["Identificación de cónicas", "Rotación de ejes", "Discriminante"]),
        ],
        "grupos": [
            {"nombre": "1CV1", "dias": [2, 4], "inicio": "07:00", "fin": "08:30",
             "alumnos": 42, "clases": GEOMETRIA_1CV1, "saltos": []},
            {"nombre": "4CM2", "dias": [3, 5], "inicio": "10:00", "fin": "11:30",
             "alumnos": 40, "clases": GEOMETRIA_4CM2, "saltos": []},
        ],
    },
]

# Preguntas reales que los alumnos ya le hicieron al chat. Alimentan el panel de
# dudas del grupo, que a su vez le dice al profesor dónde se está atorando la gente.
# (materia, grupo, índice de clase o None para pregunta general, pregunta, respuesta)
DUDAS = [
    ("Cálculo Diferencial", "3CV3", 5,
     "¿Por qué 0/0 no es una respuesta? A mí me sale un número al dividir.",
     "Porque cero sobre cero no determina un valor único: hay expresiones que dan cero sobre "
     "cero y tienden a 2, otras a 6 y otras a infinito. Tu profesora lo dijo tal cual antes del "
     "simulacro: es un aviso de que hay un factor común escondido, no un resultado. En tu grupo "
     "todavía no se resolvió ningún ejemplo completo, quedó justo en el planteamiento."),
    ("Cálculo Diferencial", "3CV3", None,
     "Falté el día del simulacro, ¿qué me perdí?",
     "Poco, y por buena razón: la sesión se cortó a los veinte minutos. Solo se enunciaron las "
     "leyes de los límites y se planteó la indeterminación 0/0. No se resolvió ningún ejercicio, "
     "así que tu grupo va a retomar cálculo de límites desde el principio."),
    ("Cálculo Diferencial", "1CV1", 6,
     "No entendí de dónde sale multiplicar por el conjugado.",
     "El conjugado sirve para quitar la raíz del numerador. Tu profesora lo hizo con raíz de x "
     "más nueve menos tres: al multiplicar arriba y abajo por raíz de x más nueve MÁS tres, el "
     "numerador se vuelve una diferencia de cuadrados y las raíces desaparecen. Queda x más "
     "nueve menos nueve, o sea x, que se cancela con la x del denominador."),
    ("Cálculo Diferencial", "1CV1", None,
     "¿La composición f∘g es lo mismo que multiplicar las funciones?",
     "No, y es la confusión más común. Componer es aplicar una función al resultado de la otra. "
     "En tu clase se comparó f∘g con g∘f para raíz de x y x menos tres: dan expresiones "
     "distintas y dominios distintos. Multiplicarlas sería otra operación completamente."),
    ("Cálculo Diferencial", "2CV2", 4,
     "¿Ya vamos atrasados por el puente?",
     "Van una sesión abajo del calendario original, y tu profesora lo compensó retomando "
     "dominios rápido para entrar a composición el mismo día. Quedó pendiente función inversa "
     "antes de arrancar límites."),
    ("Geometría Analítica", "1CV1", 3,
     "¿Por qué la parábola de Geometría se parece a la de Cálculo?",
     "Porque es la misma curva vista desde dos ángulos. En Cálculo la construyeron por "
     "transformaciones —corrida, reflejada y subida— y en Geometría le están poniendo nombre a "
     "sus partes: vértice, foco y directriz. Tu profesora lo señaló en las dos clases."),
    ("Geometría Analítica", "4CM2", 2,
     "¿Cómo sé si completé bien el cuadrado?",
     "Verifica hacia atrás: desarrolla el binomio que obtuviste y debe regresarte los términos "
     "originales. Y cuida lo que sumas de un lado, súmalo también del otro. En tu clase se hizo "
     "con x²+y²-6x+4y-12=0 y salió centro en (3,-2) con radio 5."),
]


def _fechas_de_clase(dias: list[int], desde: date, hasta: date, cantidad: int) -> list[date]:
    """Las últimas `cantidad` fechas de clase del grupo, terminando en `hasta`.

    Se cuenta hacia atrás en vez de hacia adelante para que el historial sembrado
    siempre termine pegado a la fecha de hoy: así la agenda de la semana en curso
    tiene clases ya impartidas y clases todavía pendientes, sin importar cuándo se
    ejecute la demostración.
    """
    todas: list[date] = []
    cursor = desde
    while cursor <= hasta:
        if cursor.isoweekday() in dias:
            todas.append(cursor)
        cursor += timedelta(days=1)
    return todas[-cantidad:]


def _horario_legible(dias: list[int], inicio: str, fin: str) -> str:
    nombres = [DIAS_NOMBRE.get(dia, str(dia)) for dia in dias]
    if len(nombres) == 2:
        etiqueta = f"{nombres[0]} y {nombres[1]}"
    else:
        etiqueta = ", ".join(nombres)
    return f"{etiqueta}, {inicio}–{fin}"


def sembrar_si_esta_vacia() -> None:
    """Crea las materias de demostración solo si no hay nada en la base."""
    with Session(motor) as db:
        if db.exec(select(Materia)).first():
            return

        hoy = date.today()
        inicio_ciclo = hoy - timedelta(weeks=SEMANAS_DE_HISTORIA)
        # El historial llega hasta ayer: las clases de hoy quedan pendientes en la
        # agenda, que es como el profesor abre la app por la mañana.
        fin_historial = hoy - timedelta(days=1)

        indice_grupos: dict[tuple[str, str], int] = {}
        indice_sesiones: dict[tuple[str, str], list[int]] = {}

        for definicion in MATERIAS:
            materia = Materia(
                nombre=definicion["nombre"],
                profesor="Ing. Leticia Ramírez",
                clave=definicion["clave"],
                ciclo=definicion["ciclo"],
                sesiones_planeadas=definicion["sesiones_planeadas"],
                relacion=definicion["relacion"],
            )
            db.add(materia)
            db.commit()
            db.refresh(materia)

            temas_por_orden: dict[int, Tema] = {}
            for indice, (unidad, titulo, subtemas) in enumerate(definicion["temario"], start=1):
                tema = Tema(
                    materia_id=materia.id,
                    orden=indice,
                    unidad=unidad,
                    titulo=titulo,
                    subtemas_json=json.dumps(subtemas, ensure_ascii=False),
                )
                db.add(tema)
                temas_por_orden[indice] = tema
            db.commit()
            for tema in temas_por_orden.values():
                db.refresh(tema)

            for definicion_grupo in definicion["grupos"]:
                grupo = Grupo(
                    materia_id=materia.id,
                    nombre=definicion_grupo["nombre"],
                    horario=_horario_legible(
                        definicion_grupo["dias"],
                        definicion_grupo["inicio"],
                        definicion_grupo["fin"],
                    ),
                    alumnos=definicion_grupo["alumnos"],
                    dias_json=json.dumps(definicion_grupo["dias"]),
                    hora_inicio=definicion_grupo["inicio"],
                    hora_fin=definicion_grupo["fin"],
                )
                db.add(grupo)
                db.commit()
                db.refresh(grupo)
                indice_grupos[(materia.nombre, grupo.nombre)] = grupo.id

                clases = definicion_grupo["clases"]
                saltos = set(definicion_grupo["saltos"])
                # Se piden fechas de más para poder saltar las sesiones perdidas.
                calendario = _fechas_de_clase(
                    definicion_grupo["dias"],
                    inicio_ciclo,
                    fin_historial,
                    len(clases) + len(saltos),
                )
                fechas = [f for i, f in enumerate(calendario) if i not in saltos]

                ids_sesiones: list[int] = []
                for fecha, clase in zip(fechas, clases):
                    titulo, coberturas, resumen, puntos, donde_quedo, pendientes, transcripcion = clase
                    sesion = Sesion(
                        grupo_id=grupo.id,
                        fecha=fecha,
                        estado="cerrada",
                        titulo=titulo,
                        transcripcion=transcripcion,
                        duracion_min=90,
                        resumen_json=json.dumps(
                            {
                                "titulo": titulo,
                                "resumen": resumen,
                                "puntos_clave": puntos,
                                "donde_quedo": donde_quedo,
                                "pendientes": pendientes,
                                "dudas_detectadas": [],
                            },
                            ensure_ascii=False,
                        ),
                    )
                    db.add(sesion)
                    db.commit()
                    db.refresh(sesion)
                    ids_sesiones.append(sesion.id)

                    for orden, nivel in coberturas:
                        db.add(
                            Cobertura(
                                sesion_id=sesion.id,
                                grupo_id=grupo.id,
                                tema_id=temas_por_orden[orden].id,
                                nivel=nivel,
                                evidencia=transcripcion[:200],
                            )
                        )
                    db.commit()

                indice_sesiones[(materia.nombre, grupo.nombre)] = ids_sesiones

        for materia_nombre, grupo_nombre, indice_clase, pregunta, respuesta in DUDAS:
            grupo_id = indice_grupos.get((materia_nombre, grupo_nombre))
            if grupo_id is None:
                continue
            sesiones = indice_sesiones.get((materia_nombre, grupo_nombre), [])
            sesion_id = (
                sesiones[indice_clase]
                if indice_clase is not None and indice_clase < len(sesiones)
                else None
            )
            db.add(
                MensajeChat(
                    grupo_id=grupo_id, sesion_id=sesion_id, rol="alumno", contenido=pregunta
                )
            )
            db.add(
                MensajeChat(
                    grupo_id=grupo_id, sesion_id=sesion_id, rol="asistente", contenido=respuesta
                )
            )
        db.commit()
