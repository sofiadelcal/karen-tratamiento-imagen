"""Diagnóstico y corrección moderada de una captura con sombra intensa.

Ejecutar desde la carpeta del proyecto con ``python analisis_tratamiento.py``.
Las cuatro fotografías originales se leen sin modificarlas. Las métricas son
descriptivas: por sí solas no demuestran que un sistema reconozca mejor el objeto.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2
import numpy as np


BASE = Path(__file__).resolve().parent
FOTOS = BASE / "fotos"
SALIDA = BASE / "resultados"
ARCHIVOS = {
    "referencia": FOTOS / "referencia.png",
    "luz_desigual": FOTOS / "luz_desigual.png",
    "sombra_fuerte": FOTOS / "sombra_fuerte.png",
    "movimiento": FOTOS / "movimiento.jpg",
}
# Coordenadas (x inicial, y inicial, x final, y final) del rostro en sombra_fuerte.
ROI_ROSTRO = (300, 300, 950, 900)


def cargar(ruta: Path) -> np.ndarray:
    imagen = cv2.imread(str(ruta), cv2.IMREAD_COLOR)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {ruta}")
    return imagen


def medir(imagen: np.ndarray) -> dict[str, float | int]:
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    bordes = cv2.Canny(gris, 100, 200)
    laplaciano = cv2.Laplacian(gris, cv2.CV_64F, ksize=3)
    return {
        "ancho_px": int(gris.shape[1]),
        "alto_px": int(gris.shape[0]),
        "luminancia_media": round(float(np.mean(gris)), 2),
        "contraste_desv_est": round(float(np.std(gris)), 2),
        "percentil_5": round(float(np.percentile(gris, 5)), 2),
        "percentil_95": round(float(np.percentile(gris, 95)), 2),
        "pixeles_oscuros_pct": round(float(np.mean(gris < 50) * 100), 2),
        "varianza_laplaciano": round(float(np.var(laplaciano)), 2),
        "bordes_canny_pct": round(float(np.mean(bordes > 0) * 100), 2),
    }


def recortar(imagen: np.ndarray, caja: tuple[int, int, int, int]) -> np.ndarray:
    x0, y0, x1, y1 = caja
    if x1 > imagen.shape[1] or y1 > imagen.shape[0]:
        raise ValueError("La región del rostro excede el tamaño de la imagen")
    return imagen[y0:y1, x0:x1]


def corregir_sombra(imagen: np.ndarray) -> np.ndarray:
    # CLAHE sobre L en Lab: mejora el contraste local sin ecualizar A y B.
    lab = cv2.cvtColor(imagen, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    l_corregida = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l_corregida, a, b)), cv2.COLOR_LAB2BGR)


def tarjeta(imagen: np.ndarray, etiqueta: str, ancho: int = 520, alto: int = 680) -> np.ndarray:
    escala = min(ancho / imagen.shape[1], alto / imagen.shape[0])
    foto = cv2.resize(imagen, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
    lienzo = np.full((alto + 62, ancho, 3), 247, dtype=np.uint8)
    x = (ancho - foto.shape[1]) // 2
    y = 62 + (alto - foto.shape[0]) // 2
    lienzo[y:y + foto.shape[0], x:x + foto.shape[1]] = foto
    cv2.putText(lienzo, etiqueta, (18, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.72, (30, 30, 30), 2, cv2.LINE_AA)
    return lienzo


def guardar_imagen(ruta: Path, imagen: np.ndarray) -> None:
    if not cv2.imwrite(str(ruta), imagen):
        raise OSError(f"No se pudo guardar {ruta}")


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    originales = {nombre: cargar(ruta) for nombre, ruta in ARCHIVOS.items()}
    tratada = corregir_sombra(originales["sombra_fuerte"])
    guardar_imagen(SALIDA / "sombra_tratada.png", tratada)

    filas = []
    for nombre, imagen in originales.items():
        filas.append({"imagen": nombre, "region": "completa", **medir(imagen)})
    filas.append({"imagen": "sombra_tratada", "region": "completa", **medir(tratada)})
    for nombre, imagen in (("sombra_fuerte", originales["sombra_fuerte"]),
                           ("sombra_tratada", tratada)):
        filas.append({"imagen": nombre, "region": "rostro", **medir(recortar(imagen, ROI_ROSTRO))})

    with (SALIDA / "metricas.csv").open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    with (SALIDA / "metricas.json").open("w", encoding="utf-8") as archivo:
        json.dump({"region_rostro_xyxy": ROI_ROSTRO, "filas": filas}, archivo,
                  ensure_ascii=False, indent=2)

    panel_capturas = np.vstack((
        np.hstack((tarjeta(originales["referencia"], "1. Referencia"),
                   tarjeta(originales["luz_desigual"], "2. Luz desigual"))),
        np.hstack((tarjeta(originales["sombra_fuerte"], "3. Sombra intensa"),
                   tarjeta(originales["movimiento"], "4. Movimiento"))),
    ))
    guardar_imagen(SALIDA / "cuatro_capturas.png", panel_capturas)
    comparacion = np.hstack((
        tarjeta(originales["referencia"], "Referencia"),
        tarjeta(originales["sombra_fuerte"], "Antes: sombra"),
        tarjeta(tratada, "Despues: CLAHE"),
    ))
    guardar_imagen(SALIDA / "comparacion_tratamiento.png", comparacion)
    print(f"Resultados escritos en {SALIDA}")


if __name__ == "__main__":
    main()
