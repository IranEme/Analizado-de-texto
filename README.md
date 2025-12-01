# Proyecto de Búsqueda y Análisis de Texto

## 1. Propósito y Objetivos

El objetivo de este proyecto es proporcionar una herramienta interactiva para buscar y analizar datos de publicaciones médicas, específicamente del conjunto de datos `LitCovid`. La aplicación permite a los usuarios realizar búsquedas de texto completo en los títulos de las publicaciones y visualiza la frecuencia de los resultados por revista (`journal`).

El sistema está diseñado para ser una aplicación web simple y fácil de usar, construida con Python y la biblioteca Streamlit.

## 2. Arquitectura y Diseño

La aplicación sigue una arquitectura simple de un solo script (`buscale.py`) que se encarga de la interfaz de usuario, la carga de datos y la lógica de búsqueda.

-   **Interfaz de Usuario (UI):** Creada con `Streamlit`. Proporciona un campo de búsqueda y un botón. Los resultados se muestran en una tabla y un gráfico de barras.
-   **Carga de Datos:** Los datos se cargan desde el archivo `litcovid.export.all.tsv` utilizando la biblioteca `pandas`. Se implementa un caché (`@st.cache_data`) para optimizar el rendimiento y evitar recargar los datos en cada interacción.
-   **Lógica de Búsqueda:** La funcionalidad de búsqueda se implementa en la función `search_dataframe`, que filtra el DataFrame de `pandas` en base a la consulta del usuario.
-   **Visualización:** Se utiliza la biblioteca `altair` para generar un gráfico de barras que muestra las 10 revistas con más publicaciones encontradas en la búsqueda.

## 3. Componentes Clave

-   `buscale.py`: El script principal que contiene toda la lógica de la aplicación.
-   `litcovid.export.all.tsv`: El archivo de datos en formato TSV que contiene la información a analizar.
-   `requerimientos.txt`: El archivo que lista las dependencias de Python necesarias para ejecutar el proyecto.

## 4. Dependencias

El proyecto requiere las siguientes bibliotecas de Python:
-   `streamlit`
-   `pandas`
-   `altair`

Estas dependencias se pueden instalar utilizando el archivo `requerimientos.txt`.

## 5. Uso y Ejecución

1.  **Instalar dependencias:**
    ```bash
    pip install -r requerimientos.txt
    ```

2.  **Ejecutar la aplicación:**
    ```bash
    streamlit run buscale.py
    ```

Al ejecutar el comando, se abrirá una nueva pestaña en el navegador web con la aplicación en funcionamiento.

## 6. Futuras Mejoras

Se planea expandir la funcionalidad del proyecto para incluir un sistema de búsqueda más inteligente y escalable, así como mejorar su accesibilidad.

-   **Integración de Base de Datos SQLite:** Se agregará un diccionario de datos específico para cada tema a una base de datos SQLite. Esto permitirá una gestión más estructurada de los datos y facilitará la búsqueda dirigida.
-   **Clasificación Automática de Temas:** Implementar un modelo o sistema que detecte automáticamente el tema de la consulta del usuario (por ejemplo, "cardiología", "neurología", "COVID-19").
-   **Búsqueda Dirigida:** Una vez detectado el tema, la aplicación dirigirá la búsqueda a la tabla o colección correspondiente dentro de la base de datos SQLite, mejorando la precisión y la velocidad de los resultados.
-   **Despliegue en Render:** La aplicación Streamlit será desplegada en la plataforma Render, ofreciendo una alternativa robusta y escalable a otras opciones de hosting.