# Tratamiento de imagen — Karen Sofía Delgado Calderon

Las cuatro fotografías muestran el mismo elefante de peluche. Conservé los originales en `fotos/` y elegí la captura con sombra intensa porque oscurece parte del rostro. El script aplica CLAHE solo al canal de luminancia y deja los colores sin tratamiento directo.

## Archivos

- `main.tex`: informe APA con diagnóstico, decisión, resultados, discusión y referencias.
- `analisis_tratamiento.py`: cálculo de indicadores, tratamiento y generación de figuras.
- `fotos/`: las cuatro capturas originales.
- `resultados/`: tablas CSV/JSON, imagen tratada y dos figuras usadas en el informe.

## Reproducir el análisis

```bash
python -m pip install -r requirements.txt
python analisis_tratamiento.py
```

El programa vuelve a generar `resultados/metricas.csv`, `metricas.json`, `cuatro_capturas.png`, `comparacion_tratamiento.png` y `sombra_tratada.png`. Se probó con Python 3.14.7, OpenCV 5.0.0 y NumPy 2.5.2. La varianza del Laplaciano y los bordes Canny describen cambios de intensidad; no equivalen a una medida de reconocimiento del objeto. La sombra sobre el ojo sigue siendo visible tras el tratamiento.

## Uso en Overleaf

El proyecto está en https://www.overleaf.com/project/6ad54fa7c198f030e4bdb0bf. Para reemplazar los marcadores de posición del PDF, cargar dentro de la carpeta `resultados` del proyecto los archivos `cuatro_capturas.png` y `comparacion_tratamiento.png`. El paquete local también incluye una versión completa de `main.tex` que compila con ambas figuras.

El código y las evidencias se publican en https://github.com/sofiadelcal/karen-tratamiento-imagen por indicación del usuario. Karen figura como autora del informe; `sofiadelcal` es la cuenta que aloja el repositorio. Esta carpeta no se ha enviado a Moodle.
