ACTION_TYPE_PROMPT="""
Eres un experto en finanzas y tu tarea es analizar una oración proporcionada por un usuario para determinar el tipo de acción financiera a la que se refiere. Debes clasificar la acción en una de las siguientes categorías:

- "Cambio de divisas" (para operaciones de compra o venta de monedas extranjeras)
- "Inversion" (para acciones de invertir dinero con el objetivo de obtener ganancias futuras)
- "Transaccion" (para movimientos generales de dinero, como pagos de bienes o servicios, depósitos, retiros que no encajan en otras categorías)
- "Transferencia" (para el envío de dinero de una cuenta a otra, ya sea propia o de terceros)

Analiza la siguiente oración:

"{content}"

Basándote en tu análisis, indica **únicamente** el tipo de acción financiera en español, eligiendo una de las cuatro categorías mencionadas anteriormente. No incluyas ninguna explicación o frase adicional.

La respuesta debe ser directamente el tipo de acción identificada. Por ejemplo:

"Cambio de divisas"
"""


FOREX_PROMPT="""
Eres un experto en operaciones de cambio de divisas (Forex). Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre una operación de compra o venta de monedas extranjeras.

Debes identificar y extraer los siguientes campos:
- `description`: Una breve descripción de la operación.
- `amount`: La cantidad de la moneda de origen.
- `currency_from`: La moneda que se está vendiendo o cambiando.
- `currency_to`: La moneda que se está comprando.
- `price`: El tipo de cambio al que se realizó la operación.
- `date`: La fecha y hora de la operación (si se menciona, sino usa la actual).
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
    "date": "{{fecha_actual}}",
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
    "date": "{{fecha_actual}}",
    "action": "Cambio de divisas"
}}

Ahora analiza la siguiente oración:
"{content}. {reason}"
"""

INVESTMENT_PROMPT="""
Eres un experto en inversiones financieras. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre una acción de compra o venta de un activo de inversión.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la inversión (ej. compra de acciones de Tesla).
category: La categoría del activo invertido (ej. acciones, criptomonedas, bonos).
date: La fecha y hora de la operación (si se menciona, sino usa la actual).
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
    "date": "{{fecha_actual}}",
    "action": "buy",
    "platform": "Interactive Brokers",
    "amout": 5.0,
    "price": 170.0,
    "currency": "USD"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""

TRANSACTION_PROMPT = """Eres un experto en finanzas personales. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre un movimiento general de dinero, que puede ser un gasto o un ingreso.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transacción (ej. compra en supermercado).
amount: El monto de la transacción.
currency: La moneda de la transacción.
category: La categoría del gasto o ingreso (ej. comida, salario, alquiler).
date: La fecha y hora de la transacción (si se menciona, sino usa la actual).
action: La naturaleza de la transacción, que debe ser gasto o ingreso.
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

Oración: "Gané 1500usd de mi salario hoy."
Respuesta:

JSON
{{
    "description": "Salario",
    "amount": 1500.0,
    "currency": "USD",
    "category": "salario",
    "date": "{{fecha_actual}}",
    "action": "ingreso"
}}

Oración: "Pagué 50usd por la cena anoche."
Respuesta:
JSON
{{
    "description": "Cena",
    "amount": 50.0,
    "currency": "USD",
    "category": "comida",
    "date": "{{fecha_ayer}}",
    "action": "gasto"
}}

Oracion: "Cambie 100 dolares a 1250 pesos"
Respuesta:
JSON
{{
    "description": "Ingreso por cambio de dolares",
    "amount": 120000,
    "currency": "ARS",
    "category": "Cambio de divisas",
    "date": "{{fecha_ayer}}",
    "action": "ingreso"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""

TRANSFER_PROMPT = """Eres un experto en gestión de transferencias de dinero. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre una transferencia de fondos entre billeteras o cuentas.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transferencia (ej. transferencia de Binance a Nexo).
category: La categoría de la transferencia (ej. interna, externa).
date: La fecha y hora de la transferencia (si se menciona, sino usa la actual).
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
- Las wallet disponibles son: Wise, Deel, Takenos, Revolut, Binance, Efectivo, Nexo, Banco. En caso de que no coincida con alguna de estas poner la mas parecida ya que puede ser un error de tipeo

Ejemplos:

Oración: "Transferí $100 desde mi cuenta de Banco Santander a mi cuenta de Revolut hoy."
Respuesta:
JSON
{{
    "description": "Transferencia desde Banco Santander a Revolut",
    "category": "interna",
    "date": "{{fecha_actual}}",
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
    "date": "{{fecha_ayer}}",
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
    "date": "{{fecha_ayer}}",
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

INCOME_PROMPT="""
Eres un experto en finanzas personales. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre un ingreso.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transacción (ej. compra en supermercado).
amount: El monto de la transacción.
currency: La moneda de la transacción.
category: La categoría del gasto o ingreso (ej. comida, salario, alquiler).
date: La fecha y hora de la transacción (si se menciona, sino usa la actual).
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
    "date": "datetime",
    "action": "ingreso"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""

EXPENSE_PROMPT="""
Eres un experto en finanzas personales. Tu tarea es analizar una oración proporcionada por un usuario y extraer información relevante sobre un gasto.

Debes identificar y extraer los siguientes campos:

description: Una breve descripción de la transacción (ej. compra en supermercado).
amount: El monto de la transacción.
currency: La moneda de la transacción.
category: La categoría del gasto o ingreso (ej. comida, salario, alquiler).
date: La fecha y hora de la transacción (si se menciona, sino usa la actual).
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
    "date": "datetime",
    "action": "gasto"
}}

Ahora analiza la siguiente oración:
"{content}.{reason}"
"""