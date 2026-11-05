import io
from datetime import datetime
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.repositories.estadisticas_repository import (
    obtener_cancelaciones_db,
    obtener_franjas_horarias_db,
    obtener_ocupacion_db,
    obtener_peliculas_mas_vistas_db,
    obtener_ventas_por_genero_db,
)


def obtener_ocupacion_service(id_funcion=None, id_pelicula=None):
    """
    Calcula el porcentaje de ocupación por función y da formato ISO a las fechas.
    """
    filas = obtener_ocupacion_db(id_funcion=id_funcion, id_pelicula=id_pelicula)
    resultado = []

    for fila in filas:
        capacidad = int(fila["capacidad"])
        entradas_vendidas = int(fila["entradas_vendidas"])

        porcentaje = (entradas_vendidas / capacidad * 100.0) if capacidad > 0 else 0.0
        porcentaje_ocupacion = round(float(porcentaje), 2)

        fecha_hora = fila["fecha_hora"]
        fecha_hora_str = fecha_hora.isoformat() if isinstance(fecha_hora, datetime) else str(fecha_hora)

        resultado.append({
            "id_funcion": int(fila["id_funcion"]),
            "titulo_pelicula": str(fila["titulo_pelicula"]),
            "nombre_sala": str(fila["nombre_sala"]),
            "fecha_hora": fecha_hora_str,
            "capacidad": capacidad,
            "entradas_vendidas": entradas_vendidas,
            "porcentaje_ocupacion": porcentaje_ocupacion,
        })

    return resultado, None, 200


def obtener_ventas_por_genero_service():
    """
    Convierte montos Decimal a Float y estructura la respuesta de ventas por género.
    """
    filas = obtener_ventas_por_genero_db()
    resultado = []

    for fila in filas:
        monto = fila["total_ventas"]
        total_ventas = float(monto) if isinstance(monto, Decimal) else float(monto or 0.0)

        resultado.append({
            "genero": str(fila["genero"]),
            "total_ventas": round(total_ventas, 2),
            "entradas_vendidas": int(fila["entradas_vendidas"]),
        })

    return resultado, None, 200


def obtener_franjas_horarias_service():
    """
    Formatea las franjas horarias más vendidas.
    """
    filas = obtener_franjas_horarias_db()
    resultado = []

    for fila in filas:
        resultado.append({
            "hora": str(fila["hora"]),
            "entradas_vendidas": int(fila["entradas_vendidas"]),
        })

    return resultado, None, 200


def obtener_cancelaciones_service():
    """
    Obtiene el resumen de compras canceladas.
    """
    total = obtener_cancelaciones_db()
    data = {
        "total_cancelaciones": int(total)
    }
    return data, None, 200


def generar_reporte_pdf_service():
    """
    Genera en memoria un documento PDF profesional con todas las métricas.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6
    )
    normal_style = styles['Normal']

    elements = []

    # Encabezado principal
    elements.append(Paragraph("Cine Paradiso - Reporte General de Estadísticas", title_style))
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    elements.append(Paragraph(f"<b>Fecha de emisión:</b> {fecha_emision}", normal_style))
    elements.append(Spacer(1, 12))

    # 1. Resumen de Cancelaciones
    total_cancelaciones = obtener_cancelaciones_db()
    elements.append(Paragraph("Resumen de Cancelaciones", section_style))
    tabla_canc_data = [
        ["Métrica", "Valor"],
        ["Total de Compras Canceladas (QR CANCELADO)", str(total_cancelaciones)]
    ]
    t_canc = Table(tabla_canc_data, colWidths=[300, 200])
    t_canc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t_canc)
    elements.append(Spacer(1, 12))

    # 2. Ranking Películas Más Vistas
    top_peliculas = obtener_peliculas_mas_vistas_db(limit=5)
    elements.append(Paragraph("Películas Más Vistas", section_style))
    top_pelis_data = [["Título", "Género", "Entradas Vendidas", "Total Recaudado"]]

    for p in top_peliculas:
        monto = float(p["total_recaudado"]) if isinstance(p["total_recaudado"], Decimal) else float(p["total_recaudado"])
        top_pelis_data.append([
            str(p["titulo"]),
            str(p["genero"]),
            str(p["entradas_vendidas"]),
            f"${monto:,.2f}"
        ])

    if len(top_pelis_data) == 1:
        top_pelis_data.append(["Sin datos registrados", "-", "-", "-"])

    t_pelis = Table(top_pelis_data, colWidths=[200, 100, 100, 100])
    t_pelis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t_pelis)
    elements.append(Spacer(1, 12))

    # 3. Ventas por Género
    ventas_genero = obtener_ventas_por_genero_db()
    elements.append(Paragraph("Ventas por Género Cinematográfico", section_style))
    genero_data = [["Género", "Entradas Vendidas", "Total Recaudado"]]

    for vg in ventas_genero:
        monto = float(vg["total_ventas"]) if isinstance(vg["total_ventas"], Decimal) else float(vg["total_ventas"])
        genero_data.append([
            str(vg["genero"]),
            str(vg["entradas_vendidas"]),
            f"${monto:,.2f}"
        ])

    if len(genero_data) == 1:
        genero_data.append(["Sin datos registrados", "-", "-"])

    t_genero = Table(genero_data, colWidths=[200, 150, 150])
    t_genero.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t_genero)
    elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer, None, 200
