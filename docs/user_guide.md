# 📖 Guía de Usuario - Crypto Sentinel Bot

Bienvenido a la guía oficial de **Crypto Sentinel Bot**, tu asistente personal para el seguimiento de criptomonedas, alertas de precio y monitoreo de blockchain (Stellar y Solana) directamente en Telegram.

## 🚀 Comandos Rápidos

Si eres nuevo, estos son los comandos que más utilizarás:

- `/start`: Inicia el bot y recibe un mensaje de bienvenida.
- `/help`: Muestra la lista completa de comandos disponibles.
- `/price`: Muestra los precios de las principales criptomonedas (SOL, XLM, BTC, ETH, ADA).
- `/price [SÍMBOLO]`: Consulta el precio de una moneda específica (ej: `/price SOL`).

---

## 💰 Consulta de Precios y Mercado

El bot obtiene datos en tiempo real de CoinGecko.

- `/coins`: Lista todas las monedas soportadas por el bot (más de 28 activos).
- `/trending`: Muestra las 7 monedas que son tendencia en este momento.
- `/chart [SÍMBOLO] [días]`: Genera un gráfico de precios (ej: `/chart SOL 7`).
- `/convert [CANTIDAD] [DE] [A]`: Conversor de divisas (ej: `/convert 1 BTC USD`).

---

## 🔔 Sistema de Alertas

Configura alertas para que el bot te notifique cuando ocurra algo importante.

### Alertas de Precio
- `/alert [MONEDA] > [PRECIO]`: Te avisa cuando el precio suba de cierto nivel.
  - Ejemplo: `/alert SOL > 150`
- `/alert [MONEDA] < [PRECIO]`: Te avisa cuando el precio baje de cierto nivel.
  - Ejemplo: `/alert XLM < 0.10`
- `/alert [MONEDA] [PORCENTAJE]%`: Te avisa cuando el precio cambie un porcentaje determinado.
  - Ejemplo: `/alert BTC 5%`

### Gestión de Alertas
- `/myalerts`: Lista todas tus alertas activas.
- `/deletealert [ID]`: Elimina una alerta específica usando su ID.

---

## 🌐 Funciones Blockchain (Web3)

Monitorea tus billeteras de Stellar y Solana sin salir de Telegram.

### Stellar (XLM)
- `/sbalance [DIRECCIÓN]`: Consulta el balance de XLM y otros activos en una cuenta.
- `/swatch [DIRECCIÓN]`: Activa el monitoreo en tiempo real. Recibirás un mensaje cada vez que haya una nueva transacción en esa cuenta.
- `/sunwatch [DIRECCIÓN]`: Detiene el monitoreo de la cuenta.
- `/stransactions [DIRECCIÓN]`: Muestra las últimas 5 transacciones de la cuenta.

### Solana (SOL)
- `/sobalance [DIRECCIÓN]`: Consulta el balance de SOL.
- `/sotokens [DIRECCIÓN]`: Lista los tokens SPL (tokens en la red Solana) que posee la cuenta.
- `/sowatch [DIRECCIÓN]`: Activa el monitoreo en tiempo real de transacciones.
- `/sounwatch [DIRECCIÓN]`: Detiene el monitoreo.
- `/sotransactions [DIRECCIÓN]`: Muestra las últimas firmas de transacciones.

---

## 📊 Gestión de Portafolio

Lleva un registro de tus inversiones y mira tus ganancias o pérdidas.

- `/portfolio`: Muestra el valor total de tus inversiones y el rendimiento (Profit/Loss).
- `/padd [SÍMBOLO] [CANTIDAD] [PRECIO_COMPRA]`: Añade una compra a tu portafolio.
  - Ejemplo: `/padd SOL 10 95.5`
- `/pdel [ID]`: Elimina una entrada de tu portafolio.

---

## 🤖 Inteligencia y Análisis

- `/predict [SÍMBOLO]`: El bot analiza indicadores técnicos (como RSI y niveles de soporte/resistencia) para darte una predicción sobre el próximo movimiento del precio.
- `/stats`: Muestra estadísticas generales del uso del bot.

---

## 🛠️ Soporte y Ayuda

Si tienes problemas con algún comando, asegúrate de escribir correctamente el símbolo de la moneda (ej: SOL, XLM, BTC). 

Recuerda que este bot es una herramienta informativa y **no constituye consejo financiero**.
