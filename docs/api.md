# 📡 API Reference & Comandos

## Comandos de Telegram

### `/start`
Inicia la interacción con el bot. Registra al usuario en la base de datos si es la primera vez y muestra el menú de bienvenida.

### `/price [symbol]`
Obtiene el precio actual en USD desde CoinGecko.
- **Sin parámetros**: Muestra precios de las monedas principales (BTC, ETH, SOL, XLM).
- **Con parámetro**: Ej: `/price SOL` muestra solo el precio de Solana.

### `/alert <symbol> <condición>`
Configura una alerta de precio. El bot te notificará y desactivará la alerta una vez cumplida.
- **Superior**: `/alert SOL > 150`
- **Inferior**: `/alert XLM < 0.12`
- **Porcentual**: `/alert BTC 5%` (Notifica cuando suba o baje un 5%)

### `/myalerts`
Muestra una lista de todas tus alertas activas con su ID y configuración.

### `/deletealert <id>`
Elimina una alerta específica usando su ID.

### `/stats`
Muestra estadísticas globales o personales (alertas totales, alertas disparadas, etc.).

## Esquemas de Datos (MongoDB)

### Colección: `users`
```json
{
  "_id": "ObjectId",
  "telegram_id": 12345678,
  "username": "usuario",
  "first_name": "Nombre",
  "alerts_active": true,
  "created_at": "ISODate"
}
```

### Colección: `alerts`
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId(users)",
  "coin_id": "solana",
  "coin_symbol": "SOL",
  "alert_type": "price_above",
  "threshold": 150.0,
  "is_active": true,
  "created_at": "ISODate",
  "triggered_at": null
}
```
