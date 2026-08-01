"""Contenido de las clases de demostración.

Vive aparte de `seed.py` porque es material didáctico, no lógica: son los
resúmenes, los puntos clave y las transcripciones de las sesiones que ya se
impartieron. Tenerlo separado permite que los resúmenes sean tan extensos como
lo sería el trabajo real de un profesor sin volver ilegible el sembrador.

Estructura de cada clase:
    (título, [(orden_tema, nivel)], resumen, puntos_clave, dónde_quedó,
     pendientes, transcripción)
"""

from __future__ import annotations

TEMARIO_CALCULO: list[tuple[str, str, list[str]]] = [
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
]

TEMARIO_GEOMETRIA: list[tuple[str, str, list[str]]] = [
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
]


CALCULO_1CV1 = [
    ("Desigualdades y notación de intervalos", [(1, "cubierto")],
     "La primera sesión del curso arrancó con un repaso deliberadamente lento de las "
     "propiedades de orden de los números reales. La profesora abrió advirtiendo que, aunque "
     "el tema ya se vio en el propedéutico, aquí deja de ser un ejercicio aislado: las "
     "desigualdades van a reaparecer en el cálculo de dominios, en la definición formal de "
     "límite y en los criterios de crecimiento, así que conviene dejarlas firmes desde el "
     "primer día.\n\n"
     "El bloque central se dedicó a la propiedad que más errores genera en el examen: al "
     "multiplicar o dividir ambos lados de una desigualdad por una cantidad negativa, el "
     "sentido se invierte. En lugar de enunciarla y seguir, se verificó primero de forma "
     "numérica —partiendo de que dos es menor que cinco y multiplicando ambos lados por menos "
     "dos para llegar a que menos cuatro es mayor que menos diez— y solo después se escribió "
     "como regla general. Varios alumnos comentaron que era la primera vez que veían de dónde "
     "salía la regla en lugar de memorizarla.\n\n"
     "Enseguida se formalizó la notación de intervalos, distinguiendo el paréntesis del "
     "corchete y trabajando la unión de intervalos como forma de escribir soluciones que no "
     "son continuas. La profesora insistió en un punto conceptual: la solución de una "
     "desigualdad no es un número, es un conjunto, y escribir un solo valor como respuesta "
     "revela que no se entendió la pregunta.\n\n"
     "El cierre fue una desigualdad cuadrática resuelta por el método de regiones. Se "
     "factorizó, se ubicaron los puntos críticos sobre la recta numérica, se probó un valor de "
     "cada región y se conservaron las que producían el signo pedido. Quedó como advertencia "
     "que este método falla si primero se despeja como si fuera una ecuación.",
     ["Al multiplicar o dividir por un negativo se invierte el sentido de la desigualdad",
      "La solución de una desigualdad es un conjunto, no un número",
      "Los puntos críticos parten la recta en regiones donde el signo no cambia",
      "El paréntesis excluye el extremo, el corchete lo incluye"],
     "Terminamos con la desigualdad cuadrática x²-5x+6>0 resuelta por regiones, con solución "
     "(-∞,2) ∪ (3,∞).",
     ["Traer resueltos los ejercicios 1 a 15 de la guía",
      "Repasar factorización de trinomios para la próxima sesión"],
     "Buenos días. Vamos a empezar Cálculo con algo que ya vieron en el propedéutico pero que "
     "aquí usamos todo el semestre: desigualdades. Si a es menor que b y multiplico ambos lados "
     "por menos dos, el sentido se invierte, eso es lo que más se les olvida. Véanlo con "
     "números: dos es menor que cinco, ¿verdad? Multiplico los dos lados por menos dos: menos "
     "cuatro y menos diez. ¿Cuál es mayor? Menos cuatro. Se volteó el símbolo. No lo memoricen, "
     "compruébenlo así cada vez que duden. La notación de intervalo abierto usa paréntesis, el "
     "cerrado usa corchete, y cuando la solución viene en dos pedazos separados usamos la "
     "unión. Y ojo con algo: la solución de una desigualdad no es un número, es un conjunto de "
     "números. Si me entregan un solo valor ya sé que no entendieron la pregunta. Ahora x "
     "cuadrada menos cinco x más seis mayor que cero. No despejen como ecuación, eso falla. "
     "Factorizo: x menos dos por x menos tres. Los puntos críticos son dos y tres. Pruebo un "
     "valor en cada región y me quedo con las que dan positivo: menos infinito a dos, unión, "
     "tres a infinito."),

    ("Valor absoluto y distancia", [(2, "cubierto")],
     "La sesión se dedicó por completo al valor absoluto, con una decisión pedagógica "
     "explícita: no presentarlo como la operación de quitar el signo, sino como la distancia "
     "de un número al origen. La profesora argumentó que la definición por casos es correcta "
     "pero inútil para resolver desigualdades con rapidez, mientras que la interpretación "
     "geométrica permite leer la respuesta casi sin álgebra.\n\n"
     "Se trabajaron primero las propiedades básicas: el valor absoluto nunca es negativo, el "
     "valor absoluto de un producto es el producto de los valores absolutos, y el valor "
     "absoluto de una diferencia mide la distancia entre dos puntos de la recta. Este último "
     "punto se convirtió en la herramienta central del resto de la clase.\n\n"
     "Con esa lectura se atacaron las desigualdades del tipo menor que. Ante el planteamiento "
     "de que el valor absoluto de x menos tres sea menor que dos, en lugar de partir en casos "
     "se preguntó al grupo qué números están a menos de dos unidades del tres. La respuesta "
     "salió del salón sin necesidad de despejar, y de ahí se escribió el intervalo. Se "
     "generalizó después: toda desigualdad de esa forma describe un intervalo centrado en el "
     "punto, con radio igual a la cota.\n\n"
     "El caso mayor que se presentó como el complemento del anterior: en lugar de un intervalo "
     "centrado, dos rayos que se van hacia afuera. Se resolvieron dos ejemplos y se dejó "
     "asentado que este caso siempre produce dos regiones separadas, nunca una sola.",
     ["El valor absoluto es la distancia al origen, no la operación de quitar el signo",
      "|x-a| es la distancia entre x y a sobre la recta",
      "|x-a|<r describe un intervalo centrado en a con radio r",
      "El caso |x-a|>r siempre produce dos intervalos separados"],
     "Quedamos en la interpretación geométrica de |x-3|<2 como el intervalo abierto (1,5), y "
     "en su contraparte |x-3|>2.",
     ["Resolver los ejercicios de valor absoluto con desigualdades dobles"],
     "El valor absoluto no es quitar el signo, es la distancia al origen. Guarden esa frase "
     "porque de ahí sale todo lo demás. Si les digo valor absoluto de x menos tres menor que "
     "dos, no memoricen la fórmula ni partan en casos: pregúntense qué números están a menos de "
     "dos unidades del tres. Del uno al cinco. Ya está, ese es el intervalo, y es abierto "
     "porque dice menor estricto. Fíjense que el tres es el centro y el dos es el radio, "
     "siempre va a ser así. Cuando es mayor que, es al revés, se van para afuera y son dos "
     "intervalos separados, nunca uno solo. Y una propiedad que van a usar mucho: el valor "
     "absoluto de x menos a mide la distancia entre x y a. Con eso pueden traducir cualquier "
     "enunciado de distancia a una desigualdad y al revés."),

    ("Concepto de función, dominio y rango", [(3, "cubierto")],
     "Con esta sesión se abrió la Unidad 2 y, según la profesora, el concepto que sostiene el "
     "resto de la carrera. Se definió función como una regla de correspondencia que asigna a "
     "cada elemento del dominio uno y solo un elemento del contradominio, y se hizo hincapié "
     "en la parte que suele pasarse por alto: la unicidad de la salida.\n\n"
     "Para volver operativa la definición se presentó el criterio de la recta vertical. Se "
     "graficaron tres relaciones en el pizarrón —una parábola vertical, una circunferencia y "
     "una parábola horizontal— y se pidió al grupo decidir cuáles eran función. El ejercicio "
     "dejó claro que la circunferencia falla porque una misma abscisa tiene dos ordenadas.\n\n"
     "La segunda mitad se dedicó al cálculo de dominios, que se planteó como una rutina de dos "
     "preguntas: qué valores anulan un denominador y qué valores vuelven negativo el radicando "
     "de una raíz de índice par. Se resolvieron casos con denominador, casos con radical, y "
     "finalmente un caso combinado donde había que intersectar ambas restricciones.\n\n"
     "El ejemplo de cierre fue una función con raíz en el numerador y un binomio en el "
     "denominador. Varios alumnos entregaron como dominio solo la condición del radical y "
     "olvidaron excluir el valor que anula el denominador, así que se repitió el procedimiento "
     "completo señalando que ambas condiciones deben cumplirse a la vez, no una u otra. El "
     "rango se abordó de forma preliminar, leyéndolo sobre la gráfica, y se anunció que se "
     "retomará con más herramientas cuando se vea la derivada.",
     ["Una función asigna a cada entrada exactamente una salida",
      "El criterio de la recta vertical decide si una gráfica representa una función",
      "El dominio se restringe donde el denominador se anula o el radicando de índice par es negativo",
      "Cuando hay varias restricciones, el dominio es la intersección de todas"],
     "Terminamos calculando el dominio de f(x)=√(x-4)/(x-7), que es [4,7) ∪ (7,∞).",
     ["Repasar dominios con radical de índice par",
      "Traer graficadas las funciones del ejercicio 8"],
     "Una función es una regla que a cada entrada le asigna una y solo una salida. Subrayen el "
     "solo una, porque ahí es donde se cae la mitad de los ejemplos. Si trazo una recta "
     "vertical y toca la gráfica dos veces, no es función. Vean la circunferencia: para una "
     "misma x tengo dos valores de y, entonces no es función, aunque sea una curva perfectamente "
     "respetable. Para el dominio hay dos preguntas nada más: qué anula el denominador y qué "
     "hace negativo lo de adentro de una raíz par. En raíz de x menos cuatro sobre x menos "
     "siete, necesito x mayor o igual que cuatro por el radical, pero además x distinto de "
     "siete por el denominador. Y son las dos cosas al mismo tiempo, no una o la otra. El "
     "dominio es de cuatro a siete, unión, siete a infinito. El rango por ahora lo leemos en la "
     "gráfica; cuando lleguemos a derivada vamos a tener herramientas para calcularlo bien."),

    ("Tipos de funciones y transformaciones", [(4, "cubierto")],
     "La sesión clasificó primero el universo de funciones con el que se va a trabajar: "
     "algebraicas —polinomiales, racionales e irracionales— frente a trascendentes "
     "—exponenciales, logarítmicas y trigonométricas—. La profesora aclaró que la distinción no "
     "es decorativa: las reglas de derivación que se verán en la Unidad 4 se organizan "
     "exactamente con ese criterio.\n\n"
     "Después se trabajó la paridad. Se definió función par como aquella que cumple f(-x)=f(x), "
     "con simetría respecto al eje vertical, e impar como la que cumple f(-x)=-f(x), con "
     "simetría respecto al origen. Se probaron algebraicamente tres casos y se insistió en que "
     "la mayoría de las funciones no son ni una cosa ni la otra, algo que el grupo tendía a "
     "olvidar.\n\n"
     "El bloque más largo fue el de transformaciones. Se estableció que sumar una constante por "
     "fuera desplaza verticalmente, mientras que sumarla por dentro del argumento desplaza "
     "horizontalmente en sentido contrario al signo, que es el punto contraintuitivo del tema. "
     "También se cubrieron las reflexiones: el signo negativo por fuera refleja sobre el eje "
     "horizontal y por dentro sobre el vertical.\n\n"
     "El ejercicio final construyó una parábola por transformaciones sucesivas a partir de la "
     "función cuadrática básica: primero el corrimiento horizontal, luego la reflexión y al "
     "final el desplazamiento vertical, verificando en cada paso dónde quedaba el vértice. La "
     "profesora cerró conectando el tema con Geometría Analítica, donde el mismo grupo verá esa "
     "parábola descrita por foco y directriz.",
     ["f(x)+c desplaza la gráfica verticalmente, f(x+c) la desplaza horizontalmente en sentido contrario",
      "Una función par es simétrica respecto al eje y; una impar, respecto al origen",
      "La mayoría de las funciones no son ni pares ni impares",
      "El signo negativo por fuera refleja sobre el eje x; por dentro, sobre el eje y"],
     "Quedamos graficando f(x)=-(x+2)²+3 por transformaciones sucesivas, con vértice en (-2,3) "
     "y abriendo hacia abajo.",
     ["Practicar transformaciones con funciones radicales y racionales"],
     "Primero clasifiquemos: algebraicas y trascendentes. No es una etiqueta nada más, cuando "
     "lleguemos a derivar las reglas se organizan justo así. Ahora paridad: par es cuando f de "
     "menos x es igual a f de x, simetría respecto al eje y. Impar es cuando f de menos x es "
     "menos f de x, simetría respecto al origen. Y ojo, la mayoría de las funciones no son ni "
     "par ni impar, no se sientan obligados a clasificar todo. Fíjense en lo contraintuitivo de "
     "las transformaciones: el más c por dentro mueve la gráfica a la izquierda, no a la "
     "derecha. Con la parábola menos x más dos al cuadrado más tres: parto de x cuadrada, la "
     "corro dos a la izquierda, la reflejo porque hay un menos por fuera, y la subo tres. El "
     "vértice queda en menos dos, tres, y abre hacia abajo. Los que llevan Geometría conmigo van "
     "a reconocer esta misma parábola cuando veamos foco y directriz; es la misma curva, "
     "descrita de otra manera."),

    ("Álgebra de funciones y composición", [(5, "cubierto")],
     "La sesión cerró la Unidad 2 con las operaciones entre funciones. Se comenzó por las "
     "operaciones directas —suma, resta, producto y cociente— señalando que el dominio del "
     "resultado es la intersección de los dominios originales, con la restricción adicional de "
     "que en el cociente hay que excluir los ceros del denominador.\n\n"
     "El grueso de la clase fue la composición, que la profesora identificó como el tema con "
     "más confusión histórica del curso. Se enfatizó que componer no es multiplicar: f de g de "
     "x significa aplicar primero g y entregarle su resultado a f. Se representó con un "
     "diagrama de máquinas encadenadas para fijar el orden.\n\n"
     "Se resolvió después el ejemplo que da sentido al tema: con la raíz cuadrada y un binomio "
     "lineal se calcularon las dos composiciones posibles y se compararon. No solo salieron "
     "expresiones distintas, sino dominios distintos, lo que dejó demostrado de manera "
     "concreta que la composición no es conmutativa. La profesora hizo notar que el dominio de "
     "una composición puede ser más pequeño que el de ambas funciones por separado, algo que "
     "casi nadie anticipa.\n\n"
     "Los últimos minutos introdujeron la función inversa a partir del criterio de la recta "
     "horizontal: solo las funciones inyectivas admiten inversa. Se planteó la idea de que la "
     "inversa deshace lo que la función hizo y que su gráfica es la reflexión respecto a la "
     "recta identidad, pero no se alcanzaron a hacer ejercicios de cálculo de inversas.",
     ["Componer no es multiplicar: f∘g aplica primero g y su resultado se lo entrega a f",
      "La composición no es conmutativa: f∘g y g∘f dan expresiones y dominios distintos",
      "El dominio de una composición puede ser más pequeño que el de ambas funciones",
      "Solo las funciones inyectivas tienen inversa"],
     "Cerramos comparando f∘g y g∘f para f(x)=√x y g(x)=x-3, y con la introducción del criterio "
     "de la recta horizontal.",
     ["Ejercicios de composición de la guía", "Practicar cálculo de funciones inversas"],
     "Componer no es multiplicar. Escríbanlo. F de g de x significa que primero aplico g y el "
     "resultado se lo doy a f, como dos máquinas encadenadas. Con f igual a raíz de x y g igual "
     "a x menos tres, f de g de x es raíz de x menos tres, y su dominio es x mayor o igual que "
     "tres. Al revés, g de f de x es raíz de x, menos tres, con dominio x mayor o igual que "
     "cero. Distinto resultado y distinto dominio: por eso el orden importa. Y fíjense en algo "
     "que casi nadie anticipa: el dominio de la composición puede ser más chico que el de las "
     "dos funciones por separado. De inversa nada más les dejo la idea: si trazo una recta "
     "horizontal y toca la gráfica dos veces, esa función no tiene inversa. La inversa deshace "
     "lo que hizo la función, y su gráfica es el reflejo respecto a la recta y igual a x."),

    ("Noción intuitiva de límite", [(6, "cubierto")],
     "Primera sesión de la Unidad 3 y, según la profesora, el cambio de mentalidad más grande "
     "del semestre. Se planteó desde el arranque que el límite responde una pregunta distinta a "
     "la de evaluar: no interesa cuánto vale la función en el punto, sino hacia dónde tiende "
     "cuando la variable se acerca.\n\n"
     "Para separar ambas ideas se usó una función racional con una discontinuidad removible. Al "
     "sustituir directamente el valor de interés se obtuvo la forma cero sobre cero, que no "
     "está definida, y de ahí se pasó a la aproximación numérica. Se construyó una tabla de "
     "valores acercándose por la izquierda y otra por la derecha, y el grupo observó que ambas "
     "columnas se acercaban al mismo número aunque la función no estuviera definida en el "
     "punto.\n\n"
     "El resultado se contrastó con la gráfica, donde la discontinuidad aparece como un hueco. "
     "La profesora fue explícita: el hueco no impide que el límite exista, porque el límite "
     "solo mira los alrededores. Este punto generó varias preguntas y se dedicó tiempo extra a "
     "aclararlo con un segundo ejemplo.\n\n"
     "Se cerró introduciendo la notación formal de límite y adelantando el criterio que se "
     "formalizará la siguiente clase: si la aproximación por la izquierda y por la derecha no "
     "coinciden, el límite no existe. Se dejó planteado, sin desarrollarlo, que hay funciones "
     "donde los dos lados difieren y ese será el tema de límites laterales.",
     ["El límite describe la tendencia, no el valor de la función en el punto",
      "El límite puede existir aunque la función no esté definida ahí",
      "Se aproxima construyendo tablas desde la izquierda y desde la derecha",
      "Si los dos lados no coinciden, el límite no existe"],
     "Terminamos con la tabla de (x²-1)/(x-1) acercándose a x=1 desde ambos lados, tendiendo a 2.",
     ["Construir tablas de aproximación para los ejercicios 1 a 6"],
     "El límite pregunta a dónde tiende la función cuando x se acerca, no cuánto vale cuando "
     "llega. Es otra pregunta, y ese cambio de chip es lo más difícil de la unidad. En x "
     "cuadrada menos uno sobre x menos uno, si sustituyo uno me da cero sobre cero, indefinido. "
     "Pero hago la tabla: con nueve décimos me da uno punto nueve, con noventa y nueve "
     "centésimos me da uno punto noventa y nueve. Por arriba, igual, me acerco a dos desde el "
     "otro lado. La función tiende a dos aunque en el uno tenga un hoyo. Véanlo en la gráfica: "
     "ahí está el hueco, y aun así el límite existe y vale dos, porque el límite solo mira "
     "alrededor, no mira el punto. La próxima clase formalizamos, y les adelanto que hay "
     "funciones donde por la izquierda me da una cosa y por la derecha otra. Ahí el límite no "
     "va a existir, y eso es límites laterales."),

    ("Leyes de los límites e indeterminación 0/0", [(7, "cubierto")],
     "La sesión formalizó lo que la clase anterior se había hecho por tablas. Se enunciaron las "
     "leyes de los límites —el límite de una suma es la suma de los límites, y lo análogo para "
     "producto, cociente y potencia— con la advertencia de que la ley del cociente exige que el "
     "límite del denominador sea distinto de cero.\n\n"
     "Con las leyes disponibles se estableció el procedimiento estándar: intentar la sustitución "
     "directa. Si el resultado es un número, ese es el límite y no hay más que hacer. La "
     "profesora insistió en que la sustitución directa resuelve la mayoría de los ejercicios y "
     "que el alumno suele complicarse buscando trucos donde no hacen falta.\n\n"
     "El resto de la clase se dedicó al caso en que la sustitución falla. Se explicó que cero "
     "sobre cero no es un resultado sino una indeterminación: una señal de que numerador y "
     "denominador comparten un factor que se anula. Se resolvieron varios casos por "
     "factorización, cancelando el factor problemático y evaluando la expresión simplificada.\n\n"
     "El bloque final introdujo la racionalización para expresiones con radicales. Se trabajó "
     "multiplicando numerador y denominador por el conjugado, mostrando cómo la diferencia de "
     "cuadrados elimina la raíz y libera el factor que se cancela. Varios alumnos preguntaron "
     "de dónde salía la idea del conjugado, así que se detalló el desarrollo algebraico paso a "
     "paso antes de evaluar el límite.",
     ["Cero sobre cero no es un resultado, es una indeterminación",
      "La sustitución directa resuelve la mayoría de los límites: hay que intentarla primero",
      "Factorizar y cancelar el factor común resuelve la mayor parte de las indeterminaciones",
      "Con radicales se multiplica por el conjugado para generar una diferencia de cuadrados"],
     "Cerramos con el límite de (√(x+9)-3)/x cuando x tiende a 0, resuelto por conjugado, con "
     "resultado 1/6.",
     ["Estudiar racionalización para la próxima sesión",
      "Resolver los límites con radicales de la guía"],
     "Primero las leyes: el límite de una suma es la suma de los límites, y lo mismo con "
     "producto y cociente, con la condición de que el de abajo no sea cero. Con eso ya pueden "
     "resolver casi todo por sustitución directa, y les recomiendo intentar eso siempre antes "
     "de buscar trucos. Ahora, cuando sustituyen y les sale cero sobre cero, eso no es la "
     "respuesta, es un aviso: hay un factor común escondido. Con polinomios factorizo y "
     "cancelo. Con raíces es distinto. En raíz de x más nueve menos tres, sobre x, multiplico "
     "arriba y abajo por el conjugado, raíz de x más nueve más tres. ¿Por qué el conjugado? "
     "Porque me genera una diferencia de cuadrados y la raíz desaparece. Arriba me queda x más "
     "nueve menos nueve, o sea x, y se cancela con la x de abajo. Queda uno sobre raíz de x más "
     "nueve más tres, sustituyo cero y da uno sobre seis. La próxima clase vemos límites "
     "laterales, que es donde se decide si el límite existe o no."),
]


CALCULO_2CV2 = [
    ("Desigualdades y notación de intervalos", [(1, "cubierto")],
     "Sesión inaugural del curso con este grupo. Se repasaron las propiedades de orden de los "
     "números reales, con énfasis en la que provoca más errores: multiplicar o dividir por una "
     "cantidad negativa invierte el sentido de la desigualdad. La profesora la comprobó con "
     "valores concretos antes de enunciarla en general.\n\n"
     "Se formalizó después la notación de intervalos, distinguiendo abiertos de cerrados y "
     "practicando la escritura de soluciones que constan de dos regiones separadas mediante la "
     "unión. Se recalcó que la solución de una desigualdad es siempre un conjunto y no un valor "
     "aislado.\n\n"
     "El último bloque trabajó desigualdades cuadráticas por el método de regiones: factorizar, "
     "ubicar los puntos críticos sobre la recta numérica, probar el signo en cada región y "
     "conservar las que cumplen la condición. Se advirtió expresamente que despejar como si "
     "fuera una ecuación conduce a respuestas incorrectas, y se mostró un caso donde ese error "
     "produce la mitad de la solución.",
     ["Multiplicar por un negativo invierte el sentido de la desigualdad",
      "La solución es un conjunto de números, no un valor único",
      "Los puntos críticos definen las regiones donde se prueba el signo",
      "Despejar una desigualdad cuadrática como ecuación pierde parte de la solución"],
     "Terminamos resolviendo desigualdades cuadráticas por el método de regiones.",
     ["Ejercicios 1 a 12 de la guía"],
     "Propiedades de orden primero. Si multiplican por un número negativo, el símbolo se "
     "voltea, y compruébenlo con números cada vez que duden. Notación de intervalos: paréntesis "
     "para abierto, corchete para cerrado, y unión cuando la solución viene en dos pedazos. La "
     "solución es un conjunto, no un número. Con la cuadrática factorizo, saco puntos críticos "
     "y pruebo signos por región. Y no me la despejen como ecuación, porque pierden la mitad de "
     "la respuesta; ahorita se los muestro con un ejemplo."),

    ("Valor absoluto", [(2, "cubierto")],
     "La clase se construyó alrededor de una sola idea: el valor absoluto es una distancia. La "
     "profesora rechazó explícitamente la definición operativa de quitar el signo, "
     "argumentando que impide resolver desigualdades con soltura, y presentó en cambio la "
     "lectura geométrica sobre la recta numérica.\n\n"
     "Se revisaron las propiedades fundamentales —el valor absoluto nunca es negativo, es "
     "multiplicativo, y la diferencia en valor absoluto mide la separación entre dos puntos— y "
     "se aplicaron de inmediato a desigualdades.\n\n"
     "El caso menor que se resolvió como un intervalo centrado, identificando el centro y el "
     "radio directamente del planteamiento. El caso mayor que se presentó como su complemento: "
     "dos rayos separados que se alejan del centro. Se resolvieron ejemplos de ambos tipos, "
     "incluyendo uno con coeficiente en la variable, que obligó a factorizar antes de aplicar "
     "la interpretación geométrica. Ese último caso costó trabajo al grupo y se repitió con un "
     "segundo ejemplo.",
     ["El valor absoluto es la distancia al origen y nunca es negativo",
      "|x-a|<r describe un intervalo centrado en a con radio r",
      "El caso 'mayor que' produce dos intervalos separados",
      "Con coeficiente en la variable hay que factorizar antes de leer la distancia"],
     "Quedamos resolviendo |2x-1|≥5 y su interpretación como dos rayos sobre la recta.",
     ["Practicar desigualdades con valor absoluto y coeficiente"],
     "Valor absoluto es distancia, no es quitar signos. Menor que se convierte en un intervalo "
     "centrado; mayor que se abre en dos. En dos x menos uno, mayor o igual que cinco, planteo "
     "los dos casos y me quedan dos rayos. Fíjense que aquí hay un dos multiplicando a la x, "
     "entonces primero factorizo el dos para poder leer la distancia; si no, el radio les sale "
     "mal. Vamos a hacer otro igual porque veo caras."),

    ("Concepto de función, dominio y rango", [(3, "cubierto")],
     "Apertura de la Unidad 2 con la definición de función como regla de correspondencia que "
     "asigna a cada entrada una y solo una salida. Se trabajó el criterio de la recta vertical "
     "sobre tres gráficas distintas para volver operativa la definición, y quedó claro por qué "
     "la circunferencia no representa una función.\n\n"
     "El cálculo de dominios se planteó como una rutina de dos preguntas: qué anula el "
     "denominador y qué vuelve negativo el radicando de una raíz de índice par. Se resolvieron "
     "casos con cada restricción por separado y después casos combinados, donde el dominio "
     "resulta de intersectar ambas condiciones.\n\n"
     "Se observó que varios alumnos tienen dificultades para factorizar denominadores "
     "cuadráticos, lo que impide encontrar los valores excluidos. La profesora dedicó los "
     "últimos minutos a un repaso rápido de factorización y encargó ejercicios específicos, "
     "advirtiendo que ese hueco va a estorbar en toda la unidad de límites. El rango se trató "
     "solo de forma gráfica.",
     ["Cada entrada tiene exactamente una salida",
      "El criterio de la recta vertical distingue funciones de relaciones",
      "El dominio exige denominador distinto de cero y radicando no negativo",
      "Con varias restricciones, el dominio es la intersección de todas"],
     "Terminamos con el dominio de funciones racionales con radical, intersectando restricciones.",
     ["Repasar factorización de trinomios: hace falta para los dominios",
      "Ejercicios 5 a 14 de la guía"],
     "Función es una regla que asigna una sola salida a cada entrada. Recta vertical para "
     "verificar: si la toca dos veces, no es función. Para el dominio, dos preguntas: qué anula "
     "el denominador y qué vuelve negativo el radicando de una raíz par. Y cuando hay las dos "
     "restricciones, se cumplen al mismo tiempo, se intersectan. Veo que a varios les está "
     "costando factorizar el denominador, y si no factorizan no encuentran qué excluir. Vamos a "
     "repasar factorización tantito porque eso les va a estorbar toda la unidad de límites."),

    ("Tipos de funciones y transformaciones", [(4, "cubierto")],
     "Se clasificaron las funciones en algebraicas y trascendentes, adelantando que esa misma "
     "división organiza las reglas de derivación que se verán más adelante. Se revisaron "
     "ejemplos de cada familia y sus gráficas características.\n\n"
     "El tema de paridad se trabajó tanto algebraica como gráficamente: par cuando f(-x)=f(x) "
     "con simetría respecto al eje vertical, impar cuando f(-x)=-f(x) con simetría respecto al "
     "origen. Se insistió en que la mayoría de las funciones no cae en ninguna de las dos "
     "categorías.\n\n"
     "El bloque principal fue el de transformaciones. Se estableció la diferencia entre operar "
     "por fuera —que afecta verticalmente y en el sentido esperado— y operar por dentro del "
     "argumento —que afecta horizontalmente y en sentido contrario al signo—. Este último punto "
     "se repitió varias veces porque es donde el grupo se equivoca de forma sistemática. Se "
     "practicó graficando parábolas corridas y reflejadas, verificando en cada caso la posición "
     "del vértice antes de trazar.",
     ["f(x)+c traslada verticalmente en el sentido del signo",
      "f(x+c) traslada horizontalmente en sentido contrario al signo",
      "Par es simétrica respecto al eje y; impar, respecto al origen",
      "La mayoría de las funciones no son ni pares ni impares"],
     "Cerramos graficando parábolas por transformaciones sucesivas, ubicando el vértice antes "
     "de trazar.",
     ["Graficar por transformaciones las funciones del ejercicio 9"],
     "El más c por dentro mueve a la izquierda, es lo que siempre confunde y lo voy a repetir "
     "las veces que haga falta. Por fuera se comporta como esperan, por dentro va al revés. Par "
     "significa simetría respecto al eje y; impar, respecto al origen; y la mayoría no es ni "
     "una ni otra, no se obliguen a clasificar todo. Practiquen graficando parábolas corridas y "
     "reflejadas, y siempre ubiquen el vértice primero, antes de trazar cualquier cosa."),

    ("Álgebra de funciones y composición", [(5, "cubierto")],
     "Sesión condicionada por el calendario: la clase anterior se perdió por el puente, de modo "
     "que se abrió con un repaso comprimido de dominios antes de entrar al tema nuevo. La "
     "profesora avisó al grupo que van una sesión abajo del calendario original y explicó cómo "
     "piensa recuperarla.\n\n"
     "Se cubrieron las operaciones directas entre funciones —suma, resta, producto y cociente— "
     "señalando que el dominio del resultado es la intersección de los dominios, con exclusión "
     "adicional de los ceros del denominador en el caso del cociente.\n\n"
     "El tema central fue la composición. Se explicó con el modelo de máquinas encadenadas: f "
     "de g de x aplica primero g y entrega su salida a f. Se resolvió un ejemplo con una "
     "función racional y un binomio lineal, obteniendo la composición y determinando su "
     "dominio, que excluye el valor que anula el denominador resultante.\n\n"
     "Por falta de tiempo no se alcanzó a ver función inversa, que quedó explícitamente "
     "pendiente para la siguiente sesión antes de poder entrar a la Unidad 3. La profesora "
     "dejó anotado que este grupo entra a límites con un tema de rezago respecto al plan.",
     ["f∘g exige que el resultado de g caiga en el dominio de f",
      "La composición no es conmutativa",
      "El dominio de la composición puede ser más pequeño que el de ambas funciones",
      "El dominio de un cociente excluye además los ceros del denominador"],
     "Terminamos con el dominio de f∘g para f(x)=1/x y g(x)=x-2. La función inversa quedó "
     "pendiente.",
     ["Ver función inversa la próxima sesión antes de entrar a límites",
      "Recuperar el ritmo perdido por el puente"],
     "Perdimos la del martes por el puente, así que vamos a apretar un poco y les aviso desde "
     "ahorita que traemos una sesión de retraso. Repaso rápido de dominios y entramos a "
     "composición. F de g de x quiere decir que primero aplico g, como dos máquinas "
     "encadenadas. Con f igual a uno sobre x y g igual a x menos dos, la composición es uno "
     "sobre x menos dos, y el dominio excluye el dos. Nos faltó función inversa, la vemos la "
     "próxima clase sí o sí antes de entrar a límites, porque si no llegamos cojos a la unidad "
     "tres."),
]


CALCULO_3CV3 = [
    ("Desigualdades y notación de intervalos", [(1, "cubierto")],
     "Primera sesión del curso. Se revisaron las propiedades de orden de los números reales "
     "poniendo el acento en la inversión del sentido al multiplicar por cantidades negativas, "
     "propiedad que se verificó numéricamente antes de generalizarla.\n\n"
     "Se presentó la notación de intervalos con sus variantes abierta, cerrada y semiabierta, y "
     "se practicó la escritura de soluciones formadas por dos regiones mediante la unión. La "
     "profesora subrayó que la solución de una desigualdad es un conjunto y que entregar un "
     "número aislado indica que no se entendió el planteamiento.\n\n"
     "La segunda mitad se dedicó al método de regiones para desigualdades cuadráticas: "
     "factorizar la expresión, localizar los puntos críticos, dividir la recta numérica y "
     "probar el signo en cada tramo. Se resolvieron tres ejemplos de dificultad creciente, el "
     "último con un trinomio que requería factorización por agrupación.",
     ["El sentido se invierte al multiplicar o dividir por un negativo",
      "La solución de una desigualdad es un conjunto de valores",
      "Los puntos críticos dividen la recta en regiones de signo constante",
      "En cada región basta probar un solo valor para conocer el signo"],
     "Terminamos con tres desigualdades cuadráticas resueltas por regiones.",
     ["Ejercicios 1 a 10 de la guía"],
     "Orden en los reales, notación de intervalos y desigualdades. Si multiplican por un "
     "negativo, el símbolo se voltea; compruébenlo con números. La solución es un conjunto, no "
     "un número suelto. Con la cuadrática, factorizo, ubico puntos críticos, parto la recta y "
     "pruebo el signo en cada región con un solo valor de prueba. Vamos a hacer tres, el último "
     "necesita factorización por agrupación."),

    ("Valor absoluto y distancia", [(2, "cubierto")],
     "La clase presentó el valor absoluto desde su lectura geométrica: la distancia de un "
     "número al origen sobre la recta numérica. Se argumentó que esta interpretación permite "
     "resolver desigualdades leyendo el planteamiento, sin necesidad de partir en casos.\n\n"
     "Se revisaron las propiedades básicas y se llegó rápidamente al resultado que organiza "
     "todo el tema: la diferencia en valor absoluto entre dos cantidades mide la separación "
     "entre ellas. Con esa herramienta se resolvieron desigualdades del tipo menor que, "
     "identificando el centro y el radio directamente del enunciado.\n\n"
     "El caso mayor que se presentó como el complemento geométrico: en lugar de un intervalo "
     "centrado, dos rayos que se alejan. Se resolvieron ejemplos de ambos tipos y se insistió "
     "en que este segundo caso siempre produce dos regiones separadas. El grupo respondió bien "
     "a la interpretación geométrica y varios alumnos comentaron que era más clara que el "
     "método por casos que habían visto antes.",
     ["El valor absoluto es distancia al origen y nunca es negativo",
      "|x-a| mide la separación entre x y a",
      "|x-a|<r es un intervalo centrado en a con radio r",
      "El caso 'mayor que' abre dos intervalos separados"],
     "Quedamos en la interpretación geométrica de las desigualdades con valor absoluto.",
     ["Resolver desigualdades con valor absoluto de la guía"],
     "Piénsenlo como distancia, no como quitar el signo. Valor absoluto de x menos tres menor "
     "que dos son los números que están a menos de dos unidades del tres, o sea del uno al "
     "cinco. El tres es el centro, el dos es el radio, siempre. Y cuando es mayor que, se van "
     "para afuera: dos intervalos separados, nunca uno solo. Me da gusto que les esté quedando "
     "más claro así que por casos."),

    ("Concepto de función, dominio y rango", [(3, "cubierto")],
     "Se abrió la Unidad 2 con la definición de función y el criterio de la recta vertical. Se "
     "trabajaron varias gráficas para distinguir funciones de relaciones generales, poniendo "
     "atención en la unicidad de la salida.\n\n"
     "El cálculo de dominios se presentó como una rutina sistemática de dos verificaciones: los "
     "valores que anulan denominadores y los que hacen negativo el radicando de una raíz de "
     "índice par. Se resolvieron ejemplos con cada restricción y luego combinados.\n\n"
     "La profesora señaló que este grupo va con el calendario apretado por sesiones perdidas "
     "previas, así que el rango se trató únicamente de forma gráfica, leyéndolo sobre el eje "
     "vertical, sin entrar en métodos algebraicos. Se anunció que se retomará cuando se "
     "disponga de la derivada como herramienta.",
     ["Una función asigna exactamente una salida a cada entrada",
      "El criterio de la recta vertical decide si una gráfica es función",
      "Denominador distinto de cero y radicando de índice par no negativo",
      "El rango se lee sobre el eje vertical de la gráfica"],
     "Terminamos con dominios de funciones con radical y denominador.",
     ["Ejercicios de dominio de la guía"],
     "Función, dominio y rango. Recta vertical para verificar si una gráfica lo es. Dominio: "
     "cuidado con denominadores y con raíces pares, y cuando hay las dos cosas se cumplen al "
     "mismo tiempo. El rango por ahora lo leemos en la gráfica nada más, porque traemos el "
     "calendario apretado; cuando tengamos derivada lo vemos bien."),

    ("Transformaciones y álgebra de funciones", [(4, "cubierto"), (5, "cubierto")],
     "Sesión doble por presión de calendario: se cubrieron en una sola clase los dos temas que "
     "el resto de los grupos vio por separado. La profesora avisó al inicio que iban a avanzar "
     "más rápido de lo normal y pidió al grupo detenerla ante cualquier duda.\n\n"
     "En el primer bloque se trabajaron las transformaciones de gráficas, con la distinción "
     "central entre operar por fuera —efecto vertical, en el sentido del signo— y operar por "
     "dentro del argumento —efecto horizontal, en sentido contrario—. Se practicó con "
     "parábolas trasladadas y reflejadas.\n\n"
     "El segundo bloque abordó las operaciones entre funciones y la composición. Se enfatizó "
     "que componer no es multiplicar y se calculó una composición con radical, determinando su "
     "dominio. Por el ritmo acelerado no se alcanzaron a comparar las dos composiciones "
     "posibles con el detalle habitual.\n\n"
     "La función inversa quedó apenas mencionada: se enunció que requiere que la función sea "
     "inyectiva y que su gráfica es la reflexión respecto a la recta identidad, sin ejercicios. "
     "La profesora dejó registrado que ese tema debe retomarse con calma.",
     ["f(x+c) traslada en sentido contrario al signo del argumento",
      "La composición no es conmutativa y no equivale a multiplicar",
      "El dominio de la composición se hereda de ambas funciones",
      "Solo las funciones inyectivas admiten inversa"],
     "Cerramos con composiciones y sus dominios; la función inversa quedó solo enunciada.",
     ["Retomar función inversa con calma",
      "Comparar f∘g contra g∘f con ejercicios completos"],
     "Vamos a ver dos temas hoy porque traemos el calendario apretado, y si voy muy rápido me "
     "detienen. Transformaciones: el más c por dentro corre a la izquierda, por fuera se porta "
     "como esperan. Ahora, componer no es multiplicar: f de g de x significa aplicar primero g. "
     "Con raíz de x y x menos tres, la composición es raíz de x menos tres con dominio x mayor "
     "o igual que tres. Normalmente compararíamos con la composición al revés pero ya no nos da "
     "el tiempo. De inversa solo les adelanto que necesita que la función sea inyectiva y que "
     "la gráfica es el reflejo respecto a y igual a x; lo vemos bien después, me lo apunto."),

    ("Noción intuitiva de límite", [(6, "cubierto")],
     "Arranque de la Unidad 3. Se planteó el límite como una pregunta distinta a la de evaluar: "
     "importa la tendencia de la función al acercarse al punto, no su valor en él.\n\n"
     "Se usó una función racional con discontinuidad removible para separar ambas ideas. La "
     "sustitución directa produjo la forma cero sobre cero, y a partir de ahí se construyeron "
     "tablas de aproximación por la izquierda y por la derecha. El grupo verificó que ambas "
     "columnas convergían al mismo valor pese a que la función no estaba definida en el "
     "punto.\n\n"
     "Se contrastó el resultado con la gráfica, donde la discontinuidad aparece como un hueco, "
     "y se estableció que el hueco no impide la existencia del límite porque este solo observa "
     "los alrededores.\n\n"
     "Se introdujo la notación formal y se adelantó el criterio de existencia: si la "
     "aproximación por la izquierda y por la derecha difieren, el límite no existe. Quedó "
     "anunciado que la siguiente sesión formalizaría las leyes de los límites y los métodos "
     "algebraicos para resolver indeterminaciones.",
     ["El límite es tendencia, no el valor de la función en el punto",
      "Se aproxima con tablas desde la izquierda y desde la derecha",
      "Un hueco en la gráfica no impide que el límite exista",
      "Si los dos lados difieren, el límite no existe"],
     "Terminamos con la tabla de (x²-1)/(x-1) cerca de x=1, con tendencia a 2.",
     ["Construir tablas de aproximación de los ejercicios 1 a 5"],
     "El límite pregunta hacia dónde va la función, no cuánto vale al llegar. En x cuadrada "
     "menos uno sobre x menos uno, sustituir uno da cero sobre cero. Pero la tabla muestra que "
     "se acerca a dos por los dos lados: con nueve décimos, uno punto nueve; con uno punto uno, "
     "dos punto uno. Hay un hueco en la gráfica, pero el límite existe y vale dos, porque el "
     "límite solo mira alrededor. La próxima clase formalizamos las leyes y vemos cómo "
     "resolver las indeterminaciones con álgebra."),

    ("Inicio de leyes de los límites (sesión interrumpida)", [(7, "introducido")],
     "La sesión se interrumpió a los veinte minutos por el simulacro de evacuación programado "
     "por protección civil, de modo que el tema quedó apenas planteado.\n\n"
     "Alcanzaron a enunciarse las leyes de los límites: el límite de una suma es la suma de los "
     "límites, y lo análogo para producto y cociente, con la condición de que el límite del "
     "denominador sea distinto de cero. No se resolvió ningún ejercicio de aplicación.\n\n"
     "También se alcanzó a plantear la indeterminación cero sobre cero, aclarando que no es un "
     "resultado sino una señal de que numerador y denominador comparten un factor que se anula. "
     "La profesora mencionó que en esos casos hay que factorizar o racionalizar, pero la alarma "
     "sonó antes de poder desarrollar ninguno de los dos métodos.\n\n"
     "Queda pendiente el tema completo de cálculo de límites: ni la factorización ni la "
     "racionalización se trabajaron, y el grupo no vio un solo ejemplo resuelto. La sesión "
     "siguiente debe retomarse desde el principio del tema.",
     ["Las leyes permiten separar el límite de sumas, productos y cocientes",
      "La ley del cociente exige que el límite del denominador no sea cero",
      "Cero sobre cero es una indeterminación, no un resultado"],
     "Quedamos justo en el planteamiento de la indeterminación 0/0, sin alcanzar a resolver "
     "ningún ejemplo.",
     ["Retomar cálculo de límites desde el principio",
      "Falta por completo factorización y racionalización",
      "El grupo no ha visto ningún ejercicio resuelto de indeterminación"],
     "Antes de que suene la alarma del simulacro les dejo planteadas las leyes de los límites: "
     "el límite de una suma es la suma de los límites, y lo mismo con producto y cociente, "
     "siempre que el de abajo no sea cero. Cuando al sustituir les salga cero sobre cero, eso "
     "es una indeterminación, no una respuesta. Significa que arriba y abajo comparten un "
     "factor que se hace cero. Ahí es donde entra factorizar o racionalizar, pero eso ya no nos "
     "va a dar tiempo... ahí está la alarma. Salgan en orden por la puerta de atrás, seguimos "
     "la próxima clase desde aquí."),
]


GEOMETRIA_1CV1 = [
    ("Sistema coordenado y lugar geométrico", [(1, "cubierto")],
     "Sesión inaugural del curso. La profesora planteó la idea que organiza toda la materia: la "
     "geometría analítica consiste en traducir enunciados geométricos a ecuaciones algebraicas "
     "y viceversa, de modo que problemas de figuras se resuelvan con álgebra.\n\n"
     "Se estableció el sistema coordenado cartesiano y se dedujo la fórmula de distancia entre "
     "dos puntos aplicando el teorema de Pitágoras al triángulo rectángulo que forman las "
     "diferencias de coordenadas. La profesora insistió en no memorizarla: si se olvida, se "
     "reconstruye dibujando el triángulo.\n\n"
     "Se trabajó después la división de un segmento en una razón dada, obteniendo el punto medio "
     "como caso particular con razón uno a uno. Se resolvieron ejercicios con razones internas y "
     "se comentó brevemente el caso de la razón externa.\n\n"
     "El cierre introdujo el concepto de lugar geométrico: el conjunto de puntos que satisfacen "
     "una condición dada. Se propuso al grupo describir los puntos que están a cinco unidades "
     "del origen y traducir esa condición a una ecuación, obteniendo por primera vez la "
     "circunferencia sin nombrarla todavía.",
     ["La distancia entre dos puntos es Pitágoras aplicado a las diferencias de coordenadas",
      "Un lugar geométrico es una condición geométrica traducida a ecuación",
      "El punto medio es el caso particular de división en razón 1:1",
      "Si se olvida la fórmula de distancia, se reconstruye dibujando el triángulo"],
     "Terminamos con la fórmula de división de un segmento en una razón r y el primer lugar "
     "geométrico.",
     ["Ejercicios de distancia y división de segmentos"],
     "Geometría analítica es traducir geometría a álgebra, esa es toda la idea. La distancia "
     "entre dos puntos no es una fórmula que memoricen, es Pitágoras: dibujen el triángulo, la "
     "diferencia en x es un cateto, la diferencia en y es el otro, y la distancia es la "
     "hipotenusa. Si se les olvida, la reconstruyen. El punto medio es el caso fácil de dividir "
     "un segmento, cuando la razón es uno a uno. Y un lugar geométrico es una condición: si les "
     "digo los puntos que están a cinco unidades del origen, eso es una condición, y su "
     "traducción es una ecuación. Escríbanla... exacto, x cuadrada más y cuadrada igual a "
     "veinticinco. Ya hicieron su primera circunferencia sin que yo se los dijera."),

    ("La recta: pendiente y formas de la ecuación", [(2, "cubierto")],
     "La clase desarrolló la recta como primer lugar geométrico formal del curso. Se definió la "
     "pendiente como la razón entre el cambio vertical y el cambio horizontal, y se interpretó "
     "como una medida de inclinación pero sobre todo como una razón de cambio.\n\n"
     "La profesora hizo una conexión explícita con Cálculo, que este mismo grupo lleva con "
     "ella: la pendiente es exactamente la idea que después se generaliza en la derivada para "
     "curvas. Señaló que quien entienda bien pendiente aquí va a entender derivada allá con "
     "mucho menos esfuerzo.\n\n"
     "Se dedujeron las formas de la ecuación de la recta —punto-pendiente, pendiente-ordenada y "
     "general— mostrando cómo se pasa de una a otra mediante manipulación algebraica, en lugar "
     "de presentarlas como fórmulas independientes.\n\n"
     "El bloque final trató las condiciones de paralelismo y perpendicularidad. Se estableció "
     "que las paralelas comparten pendiente y que las perpendiculares tienen pendientes cuyo "
     "producto es menos uno, es decir, recíprocas y de signo contrario. Se resolvió un ejercicio "
     "de obtener la perpendicular a una recta dada que pasa por un punto específico.",
     ["La pendiente es una razón de cambio, no solo una inclinación",
      "Las formas de la ecuación de la recta se obtienen unas de otras por álgebra",
      "Dos rectas son paralelas si tienen la misma pendiente",
      "Son perpendiculares si el producto de sus pendientes es -1"],
     "Quedamos obteniendo la ecuación de la recta perpendicular a 2x-3y+6=0 que pasa por un "
     "punto dado.",
     ["Ejercicios de rectas paralelas y perpendiculares"],
     "La pendiente es una razón de cambio, y eso les va a sonar cuando en Cálculo lleguemos a "
     "la derivada: es exactamente la misma idea, pero para curvas en lugar de rectas. El que "
     "entienda bien pendiente aquí, va a entender derivada allá sin sufrir. Punto pendiente: y "
     "menos y uno igual a m por x menos x uno. De ahí sale todo lo demás, no memoricen tres "
     "fórmulas distintas, es una sola con álgebra encima. Para perpendicular, invierten la "
     "pendiente y le cambian el signo, porque el producto tiene que dar menos uno."),

    ("La circunferencia", [(3, "cubierto")],
     "Primera cónica del curso. Se definió la circunferencia como el lugar geométrico de los "
     "puntos que equidistan de un punto fijo, y se dedujo su ecuación ordinaria aplicando "
     "directamente la fórmula de distancia vista en la primera sesión.\n\n"
     "Se subrayó la ventaja de la forma ordinaria: el centro y el radio se leen de inmediato, "
     "sin cálculo adicional. Se practicó el camino directo, escribiendo la ecuación a partir de "
     "centro y radio dados.\n\n"
     "El bloque principal fue el camino inverso: pasar de la forma general a la ordinaria "
     "completando el trinomio cuadrado perfecto. Se detalló el procedimiento agrupando términos "
     "en x y en y, completando cada cuadrado y compensando del otro lado de la igualdad. Se "
     "resolvieron dos ejemplos completos.\n\n"
     "Se discutió también el caso degenerado: si al completar cuadrados el término independiente "
     "resulta negativo, no existe lugar geométrico real, y si es cero el lugar se reduce a un "
     "punto. La profesora advirtió que este detalle aparece en el examen y que casi nadie lo "
     "verifica.",
     ["La circunferencia es el lugar geométrico de los puntos que equidistan del centro",
      "La forma ordinaria muestra centro y radio de inmediato",
      "Completar el trinomio cuadrado perfecto convierte la forma general en ordinaria",
      "Si el radio al cuadrado sale negativo no existe lugar geométrico real"],
     "Terminamos convirtiendo x²+y²-6x+4y-12=0 a su forma ordinaria, con centro (3,-2) y radio 5.",
     ["Practicar completar el trinomio cuadrado perfecto",
      "Revisar los casos degenerados de la circunferencia"],
     "La circunferencia es el lugar geométrico de los puntos que equidistan de un centro, y su "
     "ecuación sale directo de la fórmula de distancia que vimos el primer día. Si me dan la "
     "forma general, completo cuadrados: agrupo las x, agrupo las y, y lo que le sumo de un lado "
     "se lo sumo del otro, si no rompo la igualdad. De x cuadrada más y cuadrada menos seis x "
     "más cuatro y menos doce igual a cero me sale centro en tres, menos dos, y radio cinco. Y "
     "algo que casi nadie verifica y sale en el examen: si al final el radio al cuadrado les da "
     "negativo, no hay circunferencia, no existe el lugar geométrico. Si da cero, es un solo "
     "punto."),

    ("La parábola: foco, directriz y ecuación", [(4, "cubierto")],
     "La sesión definió la parábola como el lugar geométrico de los puntos que equidistan de un "
     "punto fijo llamado foco y de una recta fija llamada directriz. Se dedujo la ecuación con "
     "vértice en el origen aplicando esa condición con la fórmula de distancia.\n\n"
     "Se identificaron los elementos: vértice, foco, directriz, eje focal y lado recto, "
     "explicando el significado del parámetro como la distancia del vértice al foco y su "
     "relación con la apertura de la curva. Se practicó determinar la orientación a partir del "
     "signo y de cuál variable aparece elevada al cuadrado.\n\n"
     "El bloque final trató la traslación de ejes para parábolas con vértice fuera del origen. "
     "Aquí la profesora hizo una conexión explícita con Cálculo: el mismo grupo había "
     "construido semanas antes esa parábola por transformaciones de funciones, y ahora se le "
     "estaba poniendo nombre a sus partes. Varios alumnos reconocieron de inmediato la curva.\n\n"
     "Se cerró con un ejercicio de obtener la ecuación a partir del vértice y el foco, "
     "deduciendo el parámetro por diferencia de coordenadas y determinando la directriz por "
     "simetría.",
     ["La parábola equidista de un punto fijo (foco) y una recta fija (directriz)",
      "El parámetro es la distancia del vértice al foco y determina la apertura",
      "La variable que aparece al cuadrado indica el eje de la parábola",
      "La traslación de ejes es la misma idea que las transformaciones de funciones en Cálculo"],
     "Cerramos con la parábola de vértice (2,-1) y foco (2,1), obteniendo su ecuación y su "
     "directriz.",
     ["Ejercicios de parábola con vértice trasladado",
      "Repasar la conexión con transformaciones de funciones"],
     "Aquí se juntan mis dos materias, pongan atención. En Cálculo vimos que menos x más dos al "
     "cuadrado más tres es una parábola corrida y reflejada; aquí le vamos a poner nombre a sus "
     "partes: vértice, foco, directriz, lado recto. La parábola es el lugar geométrico de los "
     "puntos que están a la misma distancia de un punto fijo y de una recta fija. El parámetro "
     "p es la distancia del vértice al foco, y define qué tan abierta es: entre más grande p, "
     "más abierta. Y para saber hacia dónde abre, vean cuál variable está al cuadrado y qué "
     "signo trae. Si el vértice está en dos, menos uno, y el foco en dos, uno, la distancia es "
     "dos, y la directriz queda del otro lado a la misma distancia, por simetría."),
]


GEOMETRIA_4CM2 = [
    ("Sistema coordenado y lugar geométrico", [(1, "cubierto")],
     "Sesión de apertura del curso con este grupo. Se planteó el objetivo de la materia como la "
     "traducción entre geometría y álgebra, y se estableció el sistema coordenado cartesiano "
     "como el puente entre ambas.\n\n"
     "Se dedujo la fórmula de distancia entre dos puntos a partir del teorema de Pitágoras, "
     "insistiendo en reconstruirla dibujando el triángulo rectángulo en lugar de memorizarla. Se "
     "resolvieron ejercicios de cálculo de distancias y de verificación de si tres puntos son "
     "colineales.\n\n"
     "Se trabajó el punto medio como promedio de coordenadas y se resolvieron aplicaciones "
     "sencillas, incluyendo la determinación del cuarto vértice de un paralelogramo a partir de "
     "los otros tres.\n\n"
     "El cierre introdujo el concepto de lugar geométrico como el conjunto de puntos que "
     "cumplen una condición, con ejemplos verbales que el grupo tradujo a ecuaciones.",
     ["La distancia entre dos puntos es Pitágoras sobre las diferencias de coordenadas",
      "El punto medio es el promedio de las coordenadas de los extremos",
      "Un lugar geométrico traduce una condición geométrica a una ecuación",
      "La fórmula de distancia se reconstruye dibujando el triángulo"],
     "Terminamos con ejercicios de distancia, punto medio y el cuarto vértice de un "
     "paralelogramo.",
     ["Ejercicios 1 a 8 de distancia y punto medio"],
     "Vamos a traducir geometría a álgebra, ese es todo el curso. Distancia entre dos puntos: "
     "Pitágoras, dibujen el triángulo y ya. Punto medio: promedio de las coordenadas, es de las "
     "pocas cosas que sí se pueden memorizar sin culpa. Y un lugar geométrico es el conjunto de "
     "puntos que cumplen una condición; les voy a dar condiciones en palabras y ustedes me las "
     "traducen a ecuación."),

    ("La recta: pendiente y formas de la ecuación", [(2, "cubierto")],
     "Se desarrolló la recta como lugar geométrico. Se definió la pendiente como el cociente "
     "entre el cambio vertical y el horizontal, interpretándola como medida de inclinación y "
     "como razón de cambio.\n\n"
     "Se dedujo la forma punto-pendiente a partir de la definición de pendiente entre un punto "
     "genérico y uno conocido, y de ahí se obtuvieron por manipulación algebraica la forma "
     "pendiente-ordenada y la forma general. La profesora insistió en que es una sola idea con "
     "distintos acomodos, no tres fórmulas para memorizar.\n\n"
     "Se trabajaron las condiciones de paralelismo y perpendicularidad, con ejercicios de "
     "obtener rectas que cumplen una u otra condición respecto a una recta dada.\n\n"
     "Se dedicó tiempo adicional a casos particulares que suelen confundir: las rectas "
     "verticales, cuya pendiente no está definida, y las horizontales, de pendiente cero. El "
     "grupo tendía a confundir ambos casos.",
     ["La pendiente es el cambio en y sobre el cambio en x",
      "Las tres formas de la ecuación de la recta son la misma idea reacomodada",
      "Las paralelas comparten pendiente; las perpendiculares tienen producto -1",
      "La recta vertical no tiene pendiente definida; la horizontal tiene pendiente cero"],
     "Quedamos practicando la conversión entre las formas de la ecuación de la recta.",
     ["Ejercicios de rectas paralelas y perpendiculares",
      "Repasar los casos de recta vertical y horizontal"],
     "La pendiente es el cambio en y sobre el cambio en x. De ahí sale punto pendiente, y de "
     "punto pendiente sale todo lo demás con puro álgebra; no memoricen tres fórmulas. Para "
     "pasar a la forma general, paso todo de un lado e igualo a cero. Y ojo con dos casos que "
     "siempre confunden: la recta vertical no tiene pendiente, no es que valga cero, es que no "
     "está definida porque estarían dividiendo entre cero. La horizontal sí tiene pendiente y "
     "vale cero. No son lo mismo."),

    ("La circunferencia", [(3, "cubierto")],
     "Primera cónica del curso para este grupo. Se definió la circunferencia como el lugar "
     "geométrico de los puntos que equidistan de un centro y se dedujo su ecuación ordinaria "
     "aplicando la fórmula de distancia.\n\n"
     "Se practicó el camino directo —de centro y radio a ecuación— y después el inverso, que "
     "requiere completar el trinomio cuadrado perfecto para pasar de la forma general a la "
     "ordinaria. Se desarrollaron dos ejemplos completos, detallando el paso de compensar la "
     "igualdad al sumar términos.\n\n"
     "Se revisaron los casos degenerados: radio al cuadrado negativo, que no produce lugar "
     "geométrico real, y radio cero, que reduce el lugar a un punto aislado.\n\n"
     "La profesora observó que el grupo domina el procedimiento mecánico pero titubea cuando el "
     "coeficiente de los términos cuadráticos no es uno, caso en que hay que dividir toda la "
     "ecuación antes de completar cuadrados. Dejó ejercicios específicos de ese tipo.",
     ["La circunferencia equidista del centro por definición",
      "La forma ordinaria expone centro y radio directamente",
      "Completar cuadrados es la herramienta para pasar de general a ordinaria",
      "Si el coeficiente cuadrático no es 1, hay que dividir antes de completar cuadrados"],
     "Terminamos identificando centro y radio desde la forma general, incluyendo casos "
     "degenerados.",
     ["Ejercicios con coeficiente cuadrático distinto de 1"],
     "Circunferencia: puntos que equidistan del centro. Su ecuación sale de la fórmula de "
     "distancia, no es magia. Si me dan la forma general, completo el trinomio cuadrado "
     "perfecto en x y en y para llegar a la ordinaria, y de ahí leo el centro y el radio. "
     "Cuidado con una cosa: si el coeficiente de x cuadrada no es uno, primero dividen toda la "
     "ecuación, si no les va a salir mal. Y verifiquen el resultado: si el radio al cuadrado da "
     "negativo, no existe la circunferencia."),

    ("Repaso y ejercicios de recta y circunferencia", [(2, "reforzado"), (3, "reforzado")],
     "Sesión de repaso previa al primer parcial, sin temas nuevos. La profesora explicó que "
     "este grupo domina los procedimientos individuales pero pierde soltura cuando un problema "
     "combina recta y circunferencia, y dedicó la clase completa a ese tipo de ejercicios.\n\n"
     "Se resolvieron problemas de intersección entre recta y circunferencia, planteando el "
     "sistema y discutiendo los tres casos posibles según el discriminante: dos puntos de corte, "
     "tangencia o ausencia de intersección real.\n\n"
     "El ejercicio central fue el de la recta tangente a una circunferencia en un punto dado de "
     "ella. Se resolvió usando la propiedad de que la tangente es perpendicular al radio en el "
     "punto de contacto, lo que reduce el problema a calcular una pendiente y aplicar la "
     "condición de perpendicularidad.\n\n"
     "Se trabajaron también problemas donde el dato faltante era el centro o el radio y había "
     "que deducirlo de condiciones geométricas. La profesora insistió en que identificar qué "
     "dato falta es la mitad del trabajo, y que conviene dibujar antes de plantear ecuaciones.",
     ["Identificar qué dato falta es la mitad del problema",
      "La tangente a una circunferencia es perpendicular al radio en el punto de contacto",
      "El discriminante del sistema decide si hay dos cortes, tangencia o ninguno",
      "Conviene dibujar la situación antes de plantear las ecuaciones"],
     "Cerramos resolviendo la recta tangente a una circunferencia en un punto dado de ella.",
     ["Entrar a la parábola la próxima sesión",
      "Resolver la serie de problemas mixtos antes del parcial"],
     "Hoy no vemos tema nuevo, hoy resolvemos. Este grupo viene bien en los procedimientos por "
     "separado pero le falta soltura en ejercicios mixtos, y en el parcial vienen mixtos. La "
     "tangente a una circunferencia en un punto es perpendicular al radio en ese punto: con eso "
     "sale todo, calculan la pendiente del radio, la invierten, le cambian el signo y ya. "
     "Cuando les falte un dato, dibujen primero. Identificar qué les falta es la mitad del "
     "problema; la otra mitad es álgebra que ya saben hacer."),
]


# Preguntas reales que los alumnos ya le hicieron al chat. Alimentan el panel de
# dudas que ve el profesor: le revela dónde falló la explicación sin preguntarle
# a nadie. El índice de clase en None significa una duda sobre el curso completo.
# (materia, grupo, índice de clase o None, pregunta, respuesta)
DUDAS = [
    ("Cálculo Diferencial", "3CV3", 5,
     "¿Por qué 0/0 no es una respuesta? A mí me sale un número al dividir.",
     "Porque cero sobre cero no determina un valor único: hay expresiones que dan cero sobre "
     "cero y tienden a 2, otras a 6 y otras a infinito. Tu profesora lo dijo tal cual antes del "
     "simulacro: es un aviso de que hay un factor común escondido, no un resultado. En tu grupo "
     "todavía no se resolvió ningún ejemplo completo, quedó justo en el planteamiento."),
    ("Cálculo Diferencial", "3CV3", 5,
     "¿Las leyes de los límites se pueden usar siempre?",
     "Casi siempre, con una excepción que tu profesora subrayó: la ley del cociente exige que "
     "el límite del denominador sea distinto de cero. Si el denominador tiende a cero, esa ley "
     "no aplica y hay que transformar la expresión antes."),
    ("Cálculo Diferencial", "3CV3", None,
     "Falté el día del simulacro, ¿qué me perdí?",
     "Poco, y por buena razón: la sesión se cortó a los veinte minutos. Solo se enunciaron las "
     "leyes de los límites y se planteó la indeterminación 0/0. No se resolvió ningún ejercicio, "
     "así que tu grupo va a retomar cálculo de límites desde el principio."),
    ("Cálculo Diferencial", "3CV3", None,
     "¿Vamos atrasados respecto a los otros grupos?",
     "Tu grupo lleva seis sesiones y viene arrastrando calendario apretado: en una clase se "
     "juntaron transformaciones y álgebra de funciones, y la función inversa quedó solo "
     "mencionada. Aun así el avance del plan es comparable; lo que falta es cerrar bien cálculo "
     "de límites, que quedó a medias por el simulacro."),
    ("Cálculo Diferencial", "1CV1", 6,
     "No entendí de dónde sale multiplicar por el conjugado.",
     "El conjugado sirve para quitar la raíz del numerador. Tu profesora lo hizo con raíz de x "
     "más nueve menos tres: al multiplicar arriba y abajo por raíz de x más nueve MÁS tres, el "
     "numerador se vuelve una diferencia de cuadrados y las raíces desaparecen. Queda x más "
     "nueve menos nueve, o sea x, que se cancela con la x del denominador."),
    ("Cálculo Diferencial", "1CV1", 4,
     "¿Por qué el dominio de la composición sale más chico?",
     "Porque hay que cumplir dos condiciones a la vez: que x esté en el dominio de g, y que el "
     "resultado de g caiga dentro del dominio de f. Esa segunda condición recorta valores que "
     "individualmente eran válidos. Tu profesora lo mostró comparando raíz de x con x menos "
     "tres en los dos órdenes posibles."),
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
    ("Cálculo Diferencial", "2CV2", None,
     "¿Cuándo vamos a ver límites?",
     "Todavía no arrancan la Unidad 3. Tu profesora dejó dicho que primero hay que cerrar "
     "función inversa, que quedó pendiente por el puente, y de ahí entran a la noción intuitiva "
     "de límite."),
    ("Geometría Analítica", "1CV1", 3,
     "¿Por qué la parábola de Geometría se parece a la de Cálculo?",
     "Porque es la misma curva vista desde dos ángulos. En Cálculo la construyeron por "
     "transformaciones —corrida, reflejada y subida— y en Geometría le están poniendo nombre a "
     "sus partes: vértice, foco y directriz. Tu profesora lo señaló en las dos clases."),
    ("Geometría Analítica", "1CV1", None,
     "¿Para qué sirve saber la pendiente si luego vemos derivada?",
     "Justamente por eso sirve. Tu profesora lo dijo en la clase de la recta: la derivada es la "
     "misma idea de razón de cambio, pero aplicada a curvas en vez de rectas. Quien entiende "
     "pendiente aquí llega con ventaja a la Unidad 4 de Cálculo."),
    ("Geometría Analítica", "4CM2", 2,
     "¿Cómo sé si completé bien el cuadrado?",
     "Verifica hacia atrás: desarrolla el binomio que obtuviste y debe regresarte los términos "
     "originales. Y cuida lo que sumas de un lado, súmalo también del otro. En tu clase se hizo "
     "con x²+y²-6x+4y-12=0 y salió centro en (3,-2) con radio 5."),
    ("Geometría Analítica", "4CM2", 3,
     "¿Cómo saco la tangente si no me dan el radio?",
     "No necesitas el radio como número: necesitas su dirección. Calculas la pendiente del "
     "segmento que va del centro al punto de contacto, la inviertes y le cambias el signo. Esa "
     "es la pendiente de la tangente, y con el punto ya tienes la recta."),
]
