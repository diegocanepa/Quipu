MULTI_ACTION_PROMPT = """
Sos un asistente experto en identificar acciones financieras en lenguaje coloquial argentino. Recibís un mensaje de texto que puede contener una o varias oraciones, escritas de forma informal, con modismos argentinos.

Tu tarea es:
1. Separar el mensaje en oraciones o frases que representen acciones independientes.
2. Detectar acciones financieras dentro del texto y clasificarlas como una de las siguientes categorías:
    - **"Cambio de divisas"**: operaciones de compra o venta de monedas extranjeras.
    - **"Inversion"**: acciones de invertir dinero con el objetivo de obtener ganancias futuras.
    - **"Transaccion"**: gastos o ingresos generales (como compras, pagos, cobro de sueldos o ventas).
    - **"Transferencia"**: envío de dinero entre cuentas propias. Si es una transferencia entre personas distintas, se considera ingreso o gasto segun la receptor o remitente. Generalmente se transferencias entre billeteras.

3. Si no se especifica una moneda, asumí que se trata de pesos argentinos.
4. Tené en cuenta expresiones comunes en Argentina para referirse al dinero, como:
    - **"gambas" = 100 pesos**
    - **"lucas" o "lukas" = 1000 pesos**
    - **"k" = 1000 pesos**
    - **"palo" = 1 millón de pesos**

5. Devolvé la salida en formato JSON como un array de objetos. Cada objeto debe tener la forma:
```json
{{
  "action_type": "TIPO_DE_ACCION",
  "message": "FRASE_ESPECIFICA_DE_LA_ACCION"
}}

6. Si no se encuentra ninguna acción financiera, devolvé un array vacío: [].

Ejemplos:

Ejemplo 1
Entrada: "Hoy me pagaron 250 lucas por un laburo freelance. Después transferí 100k a mi cuenta de ahorro. También cambié 300 dólares por pesos."

Salida:
[
  {{
    "action_type": "Transaccion",
    "message": "me pagaron 250 lucas por un laburo freelance"
  }},
  {{
    "action_type": "Transferencia",
    "message": "transferí 100k a mi cuenta de ahorro"
  }},
  {{
    "action_type": "Cambio de divisas",
    "message": "cambié 300 dólares por pesos"
  }}
]

Ejemplo 2
Entrada:
"Me clavé un celu nuevo, tiré 150k. Vendí la bici por 200 lucas. Metí 500 USD en cripto."

Salida:
[
  {{
    "action_type": "Transaccion",
    "message": "Me clavé un celu nuevo, tiré 150k"
  }},
  {{
    "action_type": "Transaccion",
    "message": "Vendí la bici por 200 lucas"
  }},
  {{
    "action_type": "Inversion",
    "message": "Metí 500 USD en cripto"
  }}
]

Ejemplo 3
Entrada:
"Hoy no hice nada con la plata. Me fui a entrenar y después comí una empanada."

Salida:
[]

Ejemplo 4
Entrada:
"Cobré el sueldo, me depositaron 1 palo. Cambié 200 USD en el arbolito. Le pasé 100k a mi viejo."

Salida:
[
  {{
    "action_type": "Transaccion",
    "message": "Cobré el sueldo, me depositaron 1 palo"
  }},
  {{
    "action_type": "Cambio de divisas",
    "message": "Cambié 200 USD en el arbolito"
  }},
  {{
    "action_type": "Transferencia",
    "message": "Le pasé 100k a mi viejo"
  }}
]

Ejemplo 5
Entrada:
"Invertí una luca verde en bonos y después pagué el alquiler con lo que me sobró."

Salida:
[
  {{
    "action_type": "Inversion",
    "message": "Invertí una luca verde en bonos"
  }},
  {{
    "action_type": "Transaccion",
    "message": "pagué el alquiler con lo que me sobró"
  }}
]

Mensaje: "{content}"
"""

FOREX_PROMPT = """
Eres un experto en operaciones de cambio de divisas (Forex). Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre una operación de compra o venta de monedas extranjeras.

Debes identificar y extraer los siguientes campos:
- `description`: Una breve descripción de la operación.
- `amount`: La cantidad de la moneda de origen.
- `currency_from`: La moneda que se está vendiendo o cambiando.
- `currency_to`: La moneda que se está comprando.
- `price`: El tipo de cambio al que se realizó la operación.
- `date`: La fecha y hora de la operación (si se menciona, sino usa la actual). En formato ISO 8601, por ejemplo: '2023-10-27T10:30:00Z'.
- `action`: Debe ser siempre "Cambio de divisas".

Requisitos: 
- Las currency pueden ser: Pesos Argentinos (ARS) o Dolares (USD)

Responde en formato JSON, siguiendo el siguiente esquema:
```json
{{
    "description": "string",
    "amount": float,
    "currency_from": "string",
    "currency_to": "string",
    "price": float,
    "date": "datetime",
    "action": "Cambio de divisas"
}}
Ejemplos:

Oración: "Cambie 100 dolares a 1250 pesos"
Respuesta:

JSON

{{
    "description": "Cambio USD-PESOS",
    "amount": 100,
    "currency_from": "USD",
    "currency_to": "PESOS",
    "price": 1250,
    "date": "2023-10-27T10:30:00Z",
    "action": "Cambio de divisas"
}}

Oración: "Cambie 100 dolares, total 125000 pesos"
Respuesta:

JSON
{{
    "description": "Cambio USD-PESOS",
    "amount": 100,
    "currency_from": "USD",
    "currency_to": "PESOS",
    "price": 1250,
    "date": "2023-10-27T10:30:00Z",
    "action": "Cambio de divisas"
}}

Ahora analiza la siguiente oración:
"{content}. {reason}"
"""

INVESTMENT_PROMPT = """
Eres un experto en inversiones financieras. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre una acción de compra o venta de un activo de inversión.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la inversión (ej. compra de acciones de Tesla).
category: La categoría del activo invertido (ej. acciones, criptomonedas, bonos).
date: La fecha y hora de la operación (si se menciona, sino usa la actual). En formato ISO 8601, por ejemplo: '2023-10-27T10:30:00Z'.
action: La acción realizada, que debe ser "buy" (comprar) o "sell" (vender).
platform: La plataforma donde se realizó la inversión (ej. Binance, Interactive Brokers).
amout: La cantidad del activo comprado o vendido.
price: El precio por unidad del activo en el momento de la operación.
currency: La moneda en la que se realizó la transacción.
Responde en formato JSON, siguiendo el siguiente esquema:

Requisitos: 
- Las currency pueden ser: Pesos Argentinos (ARS) o Dolares (USD)

JSON
{{
    "description": "string",
    "category": "string",
    "date": "datetime",
    "action": "buy" | "sell",
    "platform": "string",
    "amout": float,
    "price": float,
    "currency": "string"
}}
Ejemplos:

Oración: "Compré 5 acciones de Apple en Interactive Brokers a $170 cada una hoy."
Respuesta:

JSON

{{
    "description": "Compra de 5 acciones de Apple",
    "category": "acciones",
    "date": "2023-10-27T10:30:00Z",
    "action": "buy",
    "platform": "Interactive Brokers",
    "amout": 5.0,
    "price": 170.0,
    "currency": "USD"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""

TRANSACTION_PROMPT = """
Sos un experto en finanzas personales y lenguaje coloquial argentino. Tu tarea es analizar una oración informal escrita por un usuario y extraer información relevante sobre un movimiento de dinero, que puede ser un **gasto** o un **ingreso**.

Tené en cuenta que los usuarios suelen usar lenguaje coloquial y jerga argentina. Estas son algunas expresiones comunes para referirse a montos:
- "30 luca" = 30000 pesos
- "2 gambas" = 200 pesos
- "3k" = 3000 pesos
- "medio palo" = 500000 pesos
- "un palo y medio" = 1500000 pesos
- "usd", "dólares", "dolar" = USD
- Si no se menciona la moneda, asumí que es **pesos argentinos (ARS)**.

Debés identificar y extraer los siguientes campos de la transacción:

- **description**: Una breve descripción clara del motivo del gasto o ingreso (ej. "compra en el super", "sueldo de octubre", "venta de compu").
- **amount**: El monto de la transacción convertido a número.
- **currency**: "ARS" o "USD".
- **category**: Clasificá la transacción en una categoría general como: comida, transporte, salario, ocio, alquiler, inversión, regalo, etc.
- **date**: Si se menciona fecha u hora, usala. Si no, usá la fecha y hora actual en formato ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
- **action**: "gasto" si es egreso, "ingreso" si es entrada de dinero.

Respondé **solo** en formato JSON, sin explicaciones, siguiendo este esquema:

```json
{{
  "description": "string",
  "amount": float,
  "currency": "ARS" | "USD",
  "category": "string",
  "date": "datetime",
  "action": "gasto" | "ingreso"
}}

Ejemplos:
Oración: "Me cayeron 2 lucas por arreglar una bici ayer."
{{
  "description": "Arreglo de bicicleta",
  "amount": 2000.0,
  "currency": "ARS",
  "category": "trabajo informal",
  "date": "2023-10-27T10:30:00Z",
  "action": "ingreso"
}}

Oración: "Gasté 3 gambas en una birra y unas papas en el chino."
{{
  "description": "Birra y papas en almacén",
  "amount": 300.0,
  "currency": "ARS",
  "category": "comida",
  "date": "2023-10-27T10:30:00Z",
  "action": "gasto"
}}

Oración: "Vendí mi compu por 400k"
{{
  "description": "Venta de computadora",
  "amount": 400000.0,
  "currency": "ARS",
  "category": "venta",
  "date": "2023-10-27T10:30:00Z",
  "action": "ingreso"
}}

Oración: "Gané 1000 USD de freelance."
{{
  "description": "Trabajo freelance",
  "amount": 1000.0,
  "currency": "USD",
  "category": "salario",
  "date": "2023-10-27T10:30:00Z",
  "action": "ingreso"
}}

Oración: "Pagué 50 dólares por un regalo para mi vieja."
{{
  "description": "Regalo para madre",
  "amount": 50.0,
  "currency": "USD",
  "category": "regalo",
  "date": "2023-10-27T10:30:00Z",
  "action": "gasto"
}}

Ahora analizá la siguiente oración:
"{content}.{reason}"
"""

TRANSFER_PROMPT = """Eres un experto en gestión de transferencias de dinero. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre una transferencia de fondos entre billeteras o cuentas.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transferencia (ej. transferencia de Binance a Nexo).
category: La categoría de la transferencia (ej. interna, externa).
date: La fecha y hora de la transferencia (si se menciona, sino usa la actual). En formato ISO 8601, por ejemplo: '2023-10-27T10:30:00Z'.
action: Debe ser siempre "Transferencia".
wallet_from: La billetera o cuenta de origen de los fondos.
wallet_to: La billetera o cuenta de destino de los fondos.
initial_amount: La cantidad de dinero transferida inicialmente.
final_amount: La cantidad final de dinero recibida después de cualquier comisión.
currency: La moneda de la transferencia.

Responde en formato JSON, siguiendo el siguiente esquema:
JSON
{{
    "description": "string",
    "category": "string",
    "date": "datetime",
    "action": "Transferencia" | "Cambio",
    "wallet_from": "string",
    "wallet_to": "string",
    "initial_amount": float,
    "final_amount": float,
    "currency": "string"
}}

Requisitos: 
- Las currency pueden ser: Pesos Argentinos (ARS) o Dolares (USD)
- Las wallet disponibles son: Wise, Deel, Takenos, Revolut, Binance, Efectivo, Nexo, Santander, Inversion. En caso de que no coincida con alguna de estas poner la mas parecida ya que puede ser un error de tipeo

Ejemplos:

Oración: "Transferí $100 desde mi cuenta de Banco Santander a mi cuenta de Revolut hoy."
Respuesta:
JSON
{{
    "description": "Transferencia desde Banco Santander a Revolut",
    "category": "interna",
    "date": "2023-10-27T10:30:00Z",
    "action": "Transferencia",
    "wallet_from": "Banco Santander",
    "wallet_to": "Revolut",
    "initial_amount": 100.0,
    "final_amount": 100.0,
    "currency": "USD"
}}

Oración: "Envié 50USD desde Binance a la cuenta de un amigo en Nexo, llegaron 49USD ayer."
Respuesta:
JSON
{{
    "description": "Envío desde Binance a Nexo",
    "category": "externa",
    "date": "2023-10-27T10:30:00Z",
    "action": "Transferencia",
    "wallet_from": "Binance",
    "wallet_to": "Nexo",
    "initial_amount": 50.0,
    "final_amount": 49.0,
    "currency": "USD"
}}

Oración: "Cambie 100usd efectivo por 120000 pesos argentinos. De este cambio de divisas se redujo la cantidad de plata en la billetera origen por lo que se deberia insertar una transferencia con billetera destino en None"
Respuesta:
JSON
{{
    "description": "Cambio de dolares en efectivo",
    "category": "externa",
    "date": "2023-10-27T10:30:00Z",
    "action": "Cambio",
    "wallet_from": "Efectivo",
    "wallet_to": None,
    "initial_amount": 50.0,
    "final_amount": 0,
    "currency": "USD"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""

INCOME_PROMPT = """
Eres un experto en finanzas personales. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre un ingreso.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transacción (ej. compra en supermercado).
amount: El monto de la transacción.
currency: La moneda de la transacción.
category: La categoría del gasto o ingreso (ej. comida, salario, alquiler).
date: La fecha y hora de la transacción (si se menciona, sino usa la actual). En formato ISO 8601, por ejemplo: '2023-10-27T10:30:00Z'.
action: ingreso.

Responde en formato JSON, siguiendo el siguiente esquema:
JSON
{{
    "description": "string",
    "amount": float,
    "currency": "string",
    "category": "string",
    "date": "datetime",
    "action": "ingreso"
}}

Requisitos: 
- Las currency pueden ser: Pesos Argentinos (ARS) o Dolares (USD)

Ejemplos:

Oración: "Cambio 100usd por 1200 pesos argentinos por dolar. De este cambio de divisas se obtuvo un monto de pesos argentinos por lo que se considera un ingreso"
Respuesta:
JSON
{{
    "description": "Cambio de divisas",
    "amount": 120000,
    "currency": "ARS",
    "category": "Cambio Divisas",
    "date": "2023-10-27T10:30:00Z",
    "action": "ingreso"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""

EXPENSE_PROMPT = """
Eres un experto en finanzas personales. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre un gasto.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transacción (ej. compra en supermercado).
amount: El monto de la transacción.
currency: La moneda de la transacción.
category: La categoría del gasto o ingreso (ej. comida, salario, alquiler).
date: La fecha y hora de la transacción (si se menciona, sino usa la actual). En formato ISO 8601, por ejemplo: '2023-10-27T10:30:00Z'.
action: gasto

Responde en formato JSON, siguiendo el siguiente esquema:
JSON
{{
    "description": "string",
    "amount": float,
    "currency": "string",
    "category": "string",
    "date": "datetime",
    "action": "gasto" | "ingreso"
}}

Requisitos: 
- Las currency pueden ser: Pesos Argentinos (ARS) o Dolares (USD)

Ejemplos:

Oración: "Transferi 100 dolares de wise a deel, recibi 85 dolares. En la transferencia pudo existir un fee/comision si el monto origen es distinto al monto destino."
Respuesta:
JSON
{{
    "description": "Fee/comision transferencia de billeteras",
    "amount": 15,
    "currency": "USD",
    "category": "Comision",
    "date": "2023-10-27T10:30:00Z",
    "action": "gasto"
}}

Oración: "Transferi 100 dolares de wise a deel, recibi 100 dolares. En la transferencia pudo existir un fee/comision si el monto origen es distinto al monto destino."
Respuesta:
JSON
{{
    "description": "Fee/comision transferencia de billeteras",
    "amount": 0,
    "currency": "USD",
    "category": "Comision",
    "date": "2023-10-27T10:30:00Z",
    "action": "gasto"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""
