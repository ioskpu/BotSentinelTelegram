# 🖥️ Guía de Usuario - Dashboard Web

Bienvenido al Dashboard de **Crypto Sentinel Bot**, la interfaz visual diseñada para que gestiones tus activos, alertas y portafolio de forma rápida y eficiente desde cualquier navegador.

---

## 🚀 Inicio Rápido

Para acceder al dashboard, dirígete a la URL proporcionada para tu despliegue (ej. `https://crypto-sentinel-bot.vercel.app`).

### Registro e Inicio de Sesión
1. **Login**: Utiliza las mismas credenciales que configuraste en tu cuenta.
2. **Registro**: Si eres nuevo, puedes crear una cuenta directamente desde la pantalla de registro.
3. **Persistencia**: El sistema recordará tu sesión para que no tengas que iniciar sesión cada vez.

---

## 📊 Panel Principal (Dashboard)

El panel principal te ofrece una visión 360° de tus activos y el mercado:

- **Métricas Globales**: Visualiza el Market Cap global, la dominancia de Bitcoin y el volumen de 24h en la parte superior.
- **Precios en Vivo**: Una lista de las criptomonedas más importantes con sus precios actualizados en tiempo real.
- **Gráfico de Alertas**: Un resumen visual de tus alertas activas frente a las ya disparadas.
- **Actividad Reciente**: Un feed con las últimas acciones realizadas en tu cuenta.

---

## 🔔 Gestión de Alertas

Desde la sección de **Alertas**, puedes tener control total sobre tus notificaciones:

- **Crear Alerta**:
    1. Selecciona la moneda (ej. SOL, BTC).
    2. Elige la condición: "Sube de" (Price Above) o "Baja de" (Price Below).
    3. Introduce el precio objetivo.
    4. ¡Listo! Recibirás una notificación en Telegram y en el Dashboard cuando se cumpla.
- **Estado de Alertas**:
    - **Activa**: La alerta está siendo monitoreada.
    - **Disparada**: La alerta ya se cumplió.
- **Acciones**: Puedes eliminar alertas antiguas o desactivar el monitoreo temporalmente.

---

## 💼 Portafolio y Seguimiento

Mantén el control de tus inversiones de forma visual:

- **Balance Total**: Visualiza el valor actual de todos tus activos sumados.
- **P&L (Ganancias y Pérdidas)**: El dashboard calcula automáticamente cuánto has ganado o perdido basándose en el precio actual de mercado.
- **Distribución**: Mira qué porcentaje de tu capital está en cada moneda.

---

## ⛓️ Monitoreo Blockchain (Web3)

Si utilizas las funciones de Stellar o Solana:

- **Live Feed**: En el panel lateral o en la sección dedicada, verás un flujo constante de las transacciones detectadas en las cuentas que has decidido "vigilar" con los comandos `/swatch` o `/sowatch`.
- **Estado de Conexión**: El indicador en la parte superior derecha te confirmará si estás conectado al servidor de datos en vivo (WebSocket).

---

## ⚙️ Configuración y Perfil

Personaliza tu experiencia:

- **Notificaciones**: Elige si prefieres recibir alertas solo por Telegram, por el Dashboard o por ambos.
- **Tema**: Cambia entre modo claro y oscuro según tu preferencia.
- **Idioma y Zona Horaria**: Ajusta el dashboard a tu horario local para ver las gráficas con precisión.

---

## ❓ Preguntas Frecuentes

**¿Por qué dice "Live Feed Offline"?**
Esto significa que la conexión de datos en tiempo real se ha perdido momentáneamente. El sistema intentará reconectarse automáticamente en unos segundos.

**¿Las alertas que creo aquí se ven en Telegram?**
Sí, el sistema está totalmente sincronizado. Una alerta creada en el dashboard te notificará por el bot de Telegram y viceversa.

**¿Es seguro?**
Toda la comunicación está cifrada y tus datos se almacenan de forma segura en MongoDB Atlas.
