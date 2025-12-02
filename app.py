from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import json
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Configuración Railway
PORT = int(os.environ.get("PORT", 8080))

# Configuración de paleta de colores
PALETA_ECOLOGICA = ['#2E8B57', '#90EE90', '#DAA520', '#FF8C00']

# Cargar datos con codificación correcta
def cargar_datos():
    try:
        # Intentar con diferentes codificaciones
        try:
            df = pd.read_excel('data/especies.xlsx')
        except:
            # Si falla, intentar con engine openpyxl
            df = pd.read_excel('data/especies.xlsx', engine='openpyxl')
        
        # Limpiar nombres de columnas (quitar espacios al final)
        df.columns = df.columns.str.strip()
        
        print("=== COLUMNAS DESPUÉS DE LIMPIAR ===")
        print(list(df.columns))
        print(f"\n=== TIPOS DE DATOS ===")
        print(df.dtypes)
        
        # Verificar columnas críticas
        columnas_requeridas = ['Edad', 'Sexo', 'Peso_Kg']
        for col in columnas_requeridas:
            if col not in df.columns:
                print(f"ERROR: Columna '{col}' no encontrada")
                print(f"Columnas disponibles: {list(df.columns)}")
                return None
        
        # Verificar valores únicos en Edad
        print(f"\n=== VALORES ÚNICOS EN EDAD ===")
        print(df['Edad'].unique())
        
        print(f"\n=== VALORES ÚNICOS EN SEXO ===")
        print(df['Sexo'].unique())
        
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        import traceback
        traceback.print_exc()
        return None

# Función para generar gráfico de composición por edad
def generar_grafico_composicion(df):
    try:
        print("=== GENERANDO GRÁFICO COMPOSICIÓN ===")
        composicion = df['Edad'].value_counts()
        print(f"Composición: {composicion.to_dict()}")
        
        total = composicion.sum()
        print(f"Total: {total}")
        
        # Calcular porcentajes
        porcentajes = (composicion.values / total * 100)
        porcentajes_redondeados = [round(p, 1) for p in porcentajes]
        print(f"Porcentajes: {porcentajes_redondeados}")
        
        # Crear figura con subplots
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'domain'}, {'type': 'domain'}]],
            column_widths=[0.6, 0.4],
            subplot_titles=("", "")
        )
        
        # Gráfico de donut
        fig.add_trace(go.Pie(
            values=composicion.values.tolist(),
            labels=composicion.index.tolist(),
            hole=0.4,
            marker_colors=PALETA_ECOLOGICA[:len(composicion)],
            textinfo='label+percent',
            textposition='outside',
            hoverinfo='label+value+percent',
            domain={'x': [0, 0.48]}
        ), row=1, col=1)
        
        # Tabla de datos
        fig.add_trace(go.Table(
            header=dict(
                values=['Categoría', 'Cantidad', 'Porcentaje (%)'],
                fill_color='#2E8B57',
                font=dict(color='white', size=12),
                align='center'
            ),
            cells=dict(
                values=[
                    composicion.index.tolist(),
                    composicion.values.tolist(),
                    [f'{p}%' for p in porcentajes_redondeados]
                ],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            ),
            domain={'x': [0.52, 1]}
        ), row=1, col=2)
        
        fig.update_layout(
            title=dict(
                text='COMPOSICIÓN POR EDAD<br>Los adultos dominan la población',
                font=dict(size=16, weight='bold'),
                x=0.5
            ),
            showlegend=True,
            height=500,
            annotations=[
                dict(
                    text=f'TOTAL<br>{total}<br>INDIVIDUOS',
                    x=0.12, y=0.5,
                    font=dict(size=16, weight='bold', style='italic'),
                    showarrow=False
                )
            ]
        )
        
        return fig.to_json()
        
    except Exception as e:
        print(f"Error generando gráfico de composición: {e}")
        import traceback
        traceback.print_exc()
        return None

# Función para generar gráfico de distribución por sexo
def generar_grafico_sexo(df):
    try:
        print("=== GENERANDO GRÁFICO SEXO ===")
        distribucion = df['Sexo'].value_counts()
        print(f"Distribución sexo: {distribucion.to_dict()}")
        
        total = len(df)
        print(f"Total para sexo: {total}")
        
        # Calcular porcentajes redondeados
        porcentajes = [(count / total * 100) for count in distribucion.values]
        porcentajes_redondeados = [round(p, 1) for p in porcentajes]
        print(f"Porcentajes sexo: {porcentajes_redondeados}")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=distribucion.index.tolist(),
            y=distribucion.values.tolist(),
            marker_color=['#2E8B57', '#FF8C00'],
            text=[f'{count} ({p}%)' for count, p in zip(distribucion.values, porcentajes_redondeados)],
            textposition='auto',
            hoverinfo='x+y'
        ))
        
        fig.update_layout(
            title=dict(
                text='DISTRIBUCIÓN POR SEXO<br>Predominio de machos',
                font=dict(size=16, weight='bold')
            ),
            xaxis_title='Sexo',
            yaxis_title='Cantidad de individuos',
            showlegend=False,
            height=400
        )
        
        return fig.to_json()
        
    except Exception as e:
        print(f"Error generando gráfico de sexo: {e}")
        import traceback
        traceback.print_exc()
        return None

# Función para generar gráfico de distribución de pesos
def generar_grafico_pesos(df):
    try:
        print("=== GENERANDO GRÁFICO PESOS ===")
        print(f"Peso mínimo: {df['Peso_Kg'].min()}")
        print(f"Peso máximo: {df['Peso_Kg'].max()}")
        print(f"Peso promedio: {df['Peso_Kg'].mean()}")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=df['Peso_Kg'].tolist(),
            nbinsx=30,
            marker_color='#2E8B57',
            opacity=0.7,
            name='Distribución de pesos'
        ))
        
        # Añadir líneas para estadísticas
        peso_promedio = float(df['Peso_Kg'].mean())
        peso_mediana = float(df['Peso_Kg'].median())
        
        fig.add_vline(
            x=peso_promedio, 
            line_dash="dash", 
            line_color="red", 
            annotation_text=f"Promedio: {peso_promedio:.2f} kg"
        )
        
        fig.add_vline(
            x=peso_mediana, 
            line_dash="dash", 
            line_color="blue",
            annotation_text=f"Mediana: {peso_mediana:.2f} kg"
        )
        
        fig.update_layout(
            title=dict(
                text='DISTRIBUCIÓN DE PESOS<br>Alta variabilidad (0.235 - 6.5 kg)',
                font=dict(size=16, weight='bold')
            ),
            xaxis_title='Peso (kg)',
            yaxis_title='Frecuencia',
            bargap=0.1,
            height=400
        )
        
        return fig.to_json()
        
    except Exception as e:
        print(f"Error generando gráfico de pesos: {e}")
        import traceback
        traceback.print_exc()
        return None

# Función para generar gráfico de boxplot
def generar_grafico_boxplot(df):
    try:
        print("=== GENERANDO GRÁFICO BOXPLOT ===")
        
        fig = go.Figure()
        
        # Verificar valores únicos
        sexos_unicos = df['Sexo'].unique()
        edades_unicas = df['Edad'].unique()
        
        print(f"Sexos únicos: {sexos_unicos}")
        print(f"Edades únicas: {edades_unicas}")
        
        # Separar por sexo
        for sexo, color in zip(['Macho', 'Hembra'], ['#2E8B57', '#FF8C00']):
            if sexo in sexos_unicos:
                df_sexo = df[df['Sexo'] == sexo]
                
                # Para cada categoría de edad
                for edad in edades_unicas:
                    df_filtrado = df_sexo[df_sexo['Edad'] == edad]
                    if len(df_filtrado) > 0:
                        print(f"{sexo} - {edad}: {len(df_filtrado)} individuos")
                        fig.add_trace(go.Box(
                            y=df_filtrado['Peso_Kg'].tolist(),
                            name=f'{sexo} - {edad}',
                            marker_color=color,
                            boxmean=True,
                            showlegend=True if edad == edades_unicas[0] else False,
                            legendgroup=sexo
                        ))
        
        fig.update_layout(
            title=dict(
                text='PESO POR EDAD Y SEXO<br>Análisis de dimorfismo sexual',
                font=dict(size=16, weight='bold')
            ),
            yaxis_title='Peso (kg)',
            xaxis_title='Categoría',
            boxmode='group',
            height=500
        )
        
        return fig.to_json()
        
    except Exception as e:
        print(f"Error generando gráfico boxplot: {e}")
        import traceback
        traceback.print_exc()
        return None


# Función para generar gráfico de series de tiempo
def generar_grafico_temporal(df):
    try:
        print("\n=== GENERANDO GRÁFICO TEMPORAL PARA FLASK ===")
        
        # 1. Procesar datos (igual que antes)
        df_temp = df.copy()
        df_temp['Fecha_entrga_CAV'] = pd.to_datetime(
            df_temp['Fecha_entrga_CAV'], 
            errors='coerce',
            dayfirst=True
        )
        df_temp = df_temp.dropna(subset=['Fecha_entrga_CAV'])
        
        if len(df_temp) == 0:
            print("No hay fechas válidas")
            return json.dumps({})  # JSON vacío
        
        # 2. Agrupar por día
        df_temp['Fecha_Dia'] = df_temp['Fecha_entrga_CAV'].dt.normalize()
        capturas_por_dia = df_temp.groupby('Fecha_Dia').size().reset_index(name='Numero_Capturas')
        capturas_por_dia.columns = ['Fecha', 'Numero_Capturas']
        capturas_por_dia = capturas_por_dia.sort_values('Fecha')
        
        print("Datos para gráfico temporal:")
        print(capturas_por_dia.to_string())
        
        # 3. Crear figura
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=capturas_por_dia['Fecha'].dt.strftime('%Y-%m-%d').tolist(),  # Convertir a string
            y=capturas_por_dia['Numero_Capturas'].tolist(),
            mode='lines+markers',
            name='Capturas de Iguanas',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8, color='#3CB371'),
            hovertemplate=(
                '<b>Fecha:</b> %{x}<br>' +
                '<b>Capturas:</b> %{y}<br>' +
                '<extra></extra>'
            )
        ))
        
        # 4. Configurar layout
        fig.update_layout(
            title=dict(
                text='Tendencia de Capturas Diarias de Iguanas',
                font=dict(size=18, family="Arial"),
                x=0.5
            ),
            xaxis=dict(
                title='Fecha de Captura',
                tickformat='%d/%m/%Y',
                tickangle=45,
                type='category',  # Importante para Flask
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='Número de Capturas',
                rangemode='tozero',
                showgrid=True,
                gridcolor='lightgray'
            ),
            height=500,
            hovermode='x unified',
            template='plotly_white',
            margin=dict(l=60, r=30, t=80, b=100),
            showlegend=False
        )
        
        # 5. Convertir a JSON
        graph_json = fig.to_json()
        print("✓ Gráfico temporal convertido a JSON exitosamente")
        return graph_json
        
    except Exception as e:
        print(f"Error generando gráfico temporal: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({})

    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    print("\n" + "="*50)
    print("ACCEDIENDO A /dashboard")
    print("="*50)
    
    df = cargar_datos()
    
    if df is None or df.empty:
        print("ERROR: No se pudieron cargar los datos")
        return render_template('dashboard.html', error="Error cargando datos")
    
    print(f"\nTotal de registros cargados: {len(df)}")
    
    # Calcular KPIs (ya redondeados)
    total_iguanas = len(df)
    total_adultos = len(df[df['Edad'] == 'Adulto'])
    total_subadultos = len(df[df['Edad'] == 'Subadulto'])
    total_juveniles = len(df[df['Edad'] == 'Juvenil'])
    
    print(f"Total adultos: {total_adultos}")
    print(f"Total subadultos: {total_subadultos}")
    print(f"Total juveniles: {total_juveniles}")
    
    # Porcentajes redondeados
    porcentaje_adultos = round((total_adultos / total_iguanas * 100), 1) if total_iguanas > 0 else 0
    porcentaje_subadultos = round((total_subadultos / total_iguanas * 100), 1) if total_iguanas > 0 else 0
    porcentaje_juveniles = round((total_juveniles / total_iguanas * 100), 1) if total_iguanas > 0 else 0
    
    print(f"Porcentaje adultos: {porcentaje_adultos}%")
    print(f"Porcentaje subadultos: {porcentaje_subadultos}%")
    print(f"Porcentaje juveniles: {porcentaje_juveniles}%")
    
    # Distribución por sexo
    machos = len(df[df['Sexo'] == 'Macho'])
    hembras = len(df[df['Sexo'] == 'Hembra'])
    proporcion_machos = round((machos / total_iguanas * 100), 2) if total_iguanas > 0 else 0
    porcentaje_machos = round((machos / total_iguanas * 100), 1) if total_iguanas > 0 else 0
    porcentaje_hembras = round((hembras / total_iguanas * 100), 1) if total_iguanas > 0 else 0
    
    print(f"Machos: {machos} ({porcentaje_machos}%)")
    print(f"Hembras: {hembras} ({porcentaje_hembras}%)")
    
    # Estadísticas de peso
    peso_promedio = round(float(df['Peso_Kg'].mean()), 2)
    peso_max = round(float(df['Peso_Kg'].max()), 2)
    peso_min = round(float(df['Peso_Kg'].min()), 2)
    
    print(f"Peso promedio: {peso_promedio} kg")
    print(f"Peso mínimo: {peso_min} kg")
    print(f"Peso máximo: {peso_max} kg")
    
    # Ratio M:H
    ratio_mh = round(machos / hembras, 2) if hembras > 0 else 0
    print(f"Ratio M:H: {ratio_mh}")
    
    # Generar gráficos
    print("\nGenerando gráficos...")
    grafico_composicion = generar_grafico_composicion(df)
    grafico_sexo = generar_grafico_sexo(df)
    grafico_pesos = generar_grafico_pesos(df)
    grafico_boxplot = generar_grafico_boxplot(df)
    grafico_temporal = generar_grafico_temporal(df)
    
    print(f"\n¿Gráfico composición generado? {'SÍ' if grafico_composicion else 'NO'}")
    print(f"¿Gráfico sexo generado? {'SÍ' if grafico_sexo else 'NO'}")
    print(f"¿Gráfico pesos generado? {'SÍ' if grafico_pesos else 'NO'}")
    print(f"¿Gráfico boxplot generado? {'SÍ' if grafico_boxplot else 'NO'}")
    print(f"¿Gráfico temporal generado? {'SÍ' if grafico_temporal else 'NO'}")
  
    
    return render_template('dashboard.html',
                         total_iguanas=total_iguanas,
                         total_adultos=total_adultos,
                         total_subadultos=total_subadultos,
                         total_juveniles=total_juveniles,
                         porcentaje_adultos=porcentaje_adultos,
                         porcentaje_subadultos=porcentaje_subadultos,
                         porcentaje_juveniles=porcentaje_juveniles,
                         machos=machos,
                         hembras=hembras,
                         porcentaje_machos=porcentaje_machos,
                         porcentaje_hembras=porcentaje_hembras,
                         proporcion_machos=proporcion_machos,
                         peso_promedio=peso_promedio,
                         peso_max=peso_max,
                         peso_min=peso_min,
                         ratio_mh=ratio_mh,
                         grafico_composicion=grafico_composicion,
                         grafico_sexo=grafico_sexo,
                         grafico_pesos=grafico_pesos,
                         grafico_boxplot=grafico_boxplot,
                         grafico_temporal=grafico_temporal)

@app.route('/graficos')
def graficos():
    df = cargar_datos()
    
    if df is None or df.empty:
        return render_template('graficos.html', error="Error cargando datos")
    
    # Generar todos los gráficos
    graficos_data = {
        'composicion': generar_grafico_composicion(df),
        'sexo': generar_grafico_sexo(df),
        'pesos': generar_grafico_pesos(df),
        'boxplot': generar_grafico_boxplot(df),
        'temporal': generar_grafico_temporal(df)
    }
    
    return render_template('graficos.html', graficos_data=graficos_data)

# API para KPIs
@app.route('/api/kpis')
def api_kpis():
    df = cargar_datos()
    
    if df is None or df.empty:
        return jsonify({'error': 'No se pudieron cargar los datos'})
    
    # Calcular KPIs
    total_iguanas = len(df)
    total_adultos = len(df[df['Edad'] == 'Adulto'])
    total_subadultos = len(df[df['Edad'] == 'Subadulto'])
    total_juveniles = len(df[df['Edad'] == 'Juvenil'])
    
    machos = len(df[df['Sexo'] == 'Macho'])
    hembras = len(df[df['Sexo'] == 'Hembra'])
    
    kpis = {
        'total_iguanas': total_iguanas,
        'total_adultos': total_adultos,
        'total_subadultos': total_subadultos,
        'total_juveniles': total_juveniles,
        'machos': machos,
        'hembras': hembras,
        'proporcion_machos': round((machos / total_iguanas * 100), 2) if total_iguanas > 0 else 0,
        'proporcion_hembras': round((hembras / total_iguanas * 100), 2) if total_iguanas > 0 else 0,
        'peso_promedio': round(float(df['Peso_Kg'].mean()), 2),
        'peso_max': round(float(df['Peso_Kg'].max()), 2),
        'peso_min': round(float(df['Peso_Kg'].min()), 2)
    }
    
    return jsonify(kpis)

@app.route('/tabla-datos')
def tabla_datos():
    df = cargar_datos()
    
    if df is None or df.empty:
        return render_template('tabla_datos.html', error="Error cargando datos", datos=[], columnas=[])
    
    # Convertir datos a formato para tabla
    datos = df.to_dict('records')
    columnas = list(df.columns)
    
    # Calcular estadísticas para mostrar
    total_registros = len(df)
    
    # Distribución por edad
    distribucion_edad = {}
    if 'Edad' in df.columns:
        edad_counts = df['Edad'].value_counts()
        for edad, count in edad_counts.items():
            porcentaje = round((count / total_registros) * 100, 1)
            distribucion_edad[edad] = {'cantidad': int(count), 'porcentaje': porcentaje}
    
    # Distribución por sexo
    distribucion_sexo = {}
    if 'Sexo' in df.columns:
        sexo_counts = df['Sexo'].value_counts()
        for sexo, count in sexo_counts.items():
            porcentaje = round((count / total_registros) * 100, 1)
            distribucion_sexo[sexo] = {'cantidad': int(count), 'porcentaje': porcentaje}
    
    return render_template('tabla_datos.html',
                          datos=datos,
                          columnas=columnas,
                          total_registros=total_registros,
                          distribucion_edad=distribucion_edad,
                          distribucion_sexo=distribucion_sexo)

# Para Despliegue en Railway
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
