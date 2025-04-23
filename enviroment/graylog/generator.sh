#!/bin/bash

# Solicita la contraseña al usuario y captura la salida
PASSWORD=$(/bin/bash -c 'read -sp "Por favor, introduce la contraseña y presiona Enter: " PASS && echo "$PASS"')
echo  # Añade una nueva línea después de la entrada de la contraseña

# Comprueba si se introdujo una contraseña
if [ -z "$PASSWORD" ]; then
  echo "ERROR: No se introdujo ninguna contraseña."
  exit 1
fi

# Genera hash SHA256
HASH=$(echo -n '$PASSWORD' | sha256sum | awk '{print $1}')
# Comprueba si el hash se generó correctamente
if [ -z "$HASH" ]; then
  echo "ERROR: No se pudo generar el hash."
  exit 1
fi
# Crea el archivo .env si no existe
if [ ! -f graylog.env ]; then
  touch graylog.env
fi
# Comprueba si el archivo se creó correctamente
if [ ! -f graylog.env ]; then
  echo "ERROR: No se pudo crear el archivo graylog.env."
  exit 1
fi

PASSWORD_LENGTH=${#PASSWORD}
if [ "$PASSWORD_LENGTH" -lt 17 ]; then
  GRAYLOG_PASSWORD_SECRET="${PASSWORD}$(printf "%0$((16 - PASSWORD_LENGTH))d" 0)"
elif [ "$PASSWORD_LENGTH" -gt 17 ]; then
  GRAYLOG_PASSWORD_SECRET="${PASSWORD:0:16}"
else
  GRAYLOG_PASSWORD_SECRET="$PASSWORD"
fi

# Guarda la contraseña original y el hash en .env
echo "POWER_PASSWORD=$PASSWORD" >> graylog.env
echo "APP_ENCRYPT_PASSWORD=$HASH" >> graylog.env
echo "APP_PASSWORD=$PASSWORD" >> graylog.env
echo "GRAYLOG_PASSWORD_SECRET=$GRAYLOG_PASSWORD_SECRET" >> graylog.env

echo "Archivo graylog.env generado con éxito."