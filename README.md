🚘 Control de Luces Automotrices por WiFi

Proyecto – Ingeniería de Software

Sistema embebido desarrollado con ESP32 y MicroPython que permite controlar y monitorear luces automotrices mediante una interfaz web accesible por WiFi.

El sistema simula el control remoto de iluminación vehicular (luces delanteras, intermitentes o auxiliares) utilizando un servidor web embebido y comunicación inalámbrica en modo Access Point.

📌 Descripción del Proyecto

Este proyecto implementa un sistema de control de luces automotrices utilizando:

Microcontrolador ESP32

Servidor web embebido

Comunicación WiFi

Interfaz HTML dinámica

Control de salidas digitales (actuadores)

El objetivo es aplicar principios de Ingeniería de Software, integrando diseño modular, pruebas funcionales y documentación estructurada en un entorno de sistemas embebidos.

🛠 Tecnologías Utilizadas

MicroPython

ESP32

HTML embebido

Socket programming

WiFi (modo Access Point)

Programación Orientada a Objetos (POO)

⚙ Arquitectura del Sistema

El sistema se compone de:

Capa de Hardware

ESP32

LEDs o relevadores simulando luces

Fuente de alimentación

Capa de Comunicación

Red WiFi creada por el ESP32

Servidor HTTP embebido

Capa de Aplicación

Generación dinámica de HTML

Lógica de control de luces

Interfaz gráfica accesible desde navegador

🔌 Conexiones Principales
Función	GPIO
Luces delanteras	(ej. GPIO 4)
Intermitentes	(ej. GPIO 5)
Luces auxiliares	(ej. GPIO 18)
GND común	GND

(Ajustar según tu implementación real.)

🌐 Funcionamiento

El ESP32 crea una red WiFi local.

El usuario se conecta desde su celular o computadora.

Se accede a la dirección IP local del dispositivo.

La página web permite:

Encender o apagar luces

Visualizar estado actual

Simular comportamiento automotriz básico

🧠 Conceptos de Ingeniería de Software Aplicados

Diseño modular

Separación de responsabilidades

Documentación técnica

Control de versiones con Git

Pruebas funcionales del sistema

Desarrollo incremental

🔐 Consideraciones de Seguridad

El sistema utiliza una red WiFi local básica.
En aplicaciones automotrices reales se requiere:

Autenticación robusta

Cifrado WPA2/WPA3

Segmentación de red

Protección contra accesos no autorizados

Separación entre red de control y red de entretenimiento

🚀 Mejoras Futuras

Implementación de autenticación en la interfaz web

Comunicación con CAN Bus

Implementación de WebSockets para control en tiempo real

Aplicación móvil dedicada

Integración con sensores automotrices reales

Arquitectura basada en RTOS

📚 Aplicación en la Industria

Este proyecto simula sistemas utilizados en:

Control remoto de iluminación

Módulos BCM (Body Control Module)

Interfaces HMI conectadas

Sistemas IoT automotrices

Representa una aproximación académica a la digitalización y conectividad vehicular moderna.

👨‍💻 Autor

Josué De la Toba
Ingeniería en Tecnologías Automotrices
Materia: Ingeniería de Software
