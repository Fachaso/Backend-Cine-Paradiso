import io
from datetime import datetime
from decimal import Decimal
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.repositories.estadisticas_repository import (
    obtener_cancelaciones_db,
    obtener_franjas_horarias_db,
    obtener_ocupacion_db,
    obtener_peliculas_mas_vistas_db,
    obtener_ventas_por_genero_db,
)


def obtener_ocupacion_service(id_funcion=None, id_pelicula=None):
    """
    Calcula el porcentaje de ocupacion por funcion y da formato ISO a las fechas.
    """
    filas = obtener_ocupacion_db(
        id_funcion=id_funcion,
        id_pelicula=id_pelicula
    )
    resultado = []

    for fila in filas:
        capacidad = int(fila["capacidad"])
        entradas_vendidas = int(fila["entradas_vendidas"])

        porcentaje = (
            entradas_vendidas / capacidad * 100.0
        ) if capacidad > 0 else 0.0

        porcentaje_ocupacion = round(float(porcentaje), 2)

        fecha_hora = fila["fecha_hora"]
        fecha_hora_str = (
            fecha_hora.isoformat()
            if isinstance(fecha_hora, datetime)
            else str(fecha_hora)
        )

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
    Convierte los importes a números compatibles con JSON
    y estructura las ventas por género cinematográfico.
    """
    filas = obtener_ventas_por_genero_db()
    resultado = []

    for fila in filas:
        monto = fila["total_ventas"]

        total_ventas = (
            float(monto)
            if isinstance(monto, Decimal)
            else float(monto or 0.0)
        )

        resultado.append({
            "genero": str(fila["genero"]),
            "total_ventas": round(total_ventas, 2),
            "entradas_vendidas": int(fila["entradas_vendidas"]),
        })

    return resultado, None, 200


def obtener_franjas_horarias_service():
    """
    Formatea la cantidad de entradas vendidas
    por horario de función.
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
    Obtiene el resumen de compras canceladas
    según el estado del código QR.
    """
    total = obtener_cancelaciones_db()

    data = {
        "total_cancelaciones": int(total)
    }

    return data, None, 200


def generar_reporte_pdf_service():
    """
    Genera en memoria un reporte PDF con estadísticas
    de ventas, películas más vistas y cancelaciones.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=10,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
    )

    normal_style = styles["Normal"]

    cell_style = ParagraphStyle(
        "TableCell",
        parent=normal_style,
        fontSize=9,
        leading=12,
        splitLongWords=True,
    )

    header_style = ParagraphStyle(
        "TableHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    elements = []

    # Encabezado principal
    elements.append(
        Paragraph(
            "Cine Paradiso - Reporte General de Estadísticas",
            title_style,
        )
    )

    fecha_emision = datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    ).strftime("%d/%m/%Y %H:%M:%S")

    elements.append(
        Paragraph(
            f"<b>Fecha de emisión:</b> {fecha_emision}",
            normal_style,
        )
    )

    elements.append(Spacer(1, 12))

    # 1. Resumen de cancelaciones
    total_cancelaciones = obtener_cancelaciones_db()

    elements.append(
        Paragraph("Resumen de Cancelaciones", section_style)
    )

    tabla_canc_data = [
        [
            Paragraph("Métrica", header_style),
            Paragraph("Valor", header_style),
        ],
        [
            Paragraph(
                "Total de Compras Canceladas (QR CANCELADO)",
                cell_style,
            ),
            Paragraph(str(total_cancelaciones), cell_style),
        ],
    ]

    t_canc = Table(
        tabla_canc_data,
        colWidths=[300, 200],
        repeatRows=1,
        hAlign="LEFT",
    )

    t_canc.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#3B82F6"),
        ),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#CBD5E1"),
        ),
    ]))

    elements.append(t_canc)
    elements.append(Spacer(1, 12))

    # 2. Ranking de peliculas mas vistas
    top_peliculas = obtener_peliculas_mas_vistas_db(limit=5)

    elements.append(
        Paragraph("Películas Más Vistas", section_style)
    )

    top_pelis_data = [[
        Paragraph("Título", header_style),
        Paragraph("Género", header_style),
        Paragraph("Entradas Vendidas", header_style),
        Paragraph("Total Recaudado", header_style),
    ]]

    for pelicula in top_peliculas:
        monto = pelicula["total_recaudado"]

        top_pelis_data.append([
            Paragraph(
                escape(str(pelicula["titulo"])),
                cell_style,
            ),
            Paragraph(
                escape(str(pelicula["genero"])),
                cell_style,
            ),
            Paragraph(
                str(pelicula["entradas_vendidas"]),
                cell_style,
            ),
            Paragraph(
                f"${monto:,.2f}",
                cell_style,
            ),
        ])

    if len(top_pelis_data) == 1:
        top_pelis_data.append([
            Paragraph("Sin datos registrados", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
        ])

    t_pelis = Table(
        top_pelis_data,
        colWidths=[200, 100, 100, 100],
        repeatRows=1,
        hAlign="LEFT",
    )

    t_pelis.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#1E293B"),
        ),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#CBD5E1"),
        ),
    ]))

    elements.append(t_pelis)
    elements.append(Spacer(1, 12))

    # 3. Ventas por genero
    ventas_genero = obtener_ventas_por_genero_db()

    elements.append(
        Paragraph(
            "Ventas por Género Cinematográfico",
            section_style,
        )
    )

    genero_data = [[
        Paragraph("Género", header_style),
        Paragraph("Entradas Vendidas", header_style),
        Paragraph("Total Recaudado", header_style),
    ]]

    for venta in ventas_genero:
        monto = venta["total_ventas"]

        genero_data.append([
            Paragraph(
                escape(str(venta["genero"])),
                cell_style,
            ),
            Paragraph(
                str(venta["entradas_vendidas"]),
                cell_style,
            ),
            Paragraph(
                f"${monto:,.2f}",
                cell_style,
            ),
        ])

    if len(genero_data) == 1:
        genero_data.append([
            Paragraph("Sin datos registrados", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
        ])

    t_genero = Table(
        genero_data,
        colWidths=[200, 150, 150],
        repeatRows=1,
        hAlign="LEFT",
    )

    t_genero.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#475569"),
        ),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#CBD5E1"),
        ),
    ]))

    elements.append(t_genero)
    elements.append(Spacer(1, 12))

    # Construir el documento PDF
    doc.build(elements)

    buffer.seek(0)

    return buffer, None, 200
