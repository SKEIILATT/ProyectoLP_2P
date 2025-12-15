import pandas as pd
import matplotlib.pyplot as plt
import os

# ===============================
# CONFIGURACIÓN DE RUTAS
# ===============================

DATA_PATH = "data/"
OUTPUT_PATH = "output/"
print("Buscando datos en:", DATA_PATH)
print("Archivos encontrados:", os.listdir(DATA_PATH))

os.makedirs(OUTPUT_PATH, exist_ok=True)

# ===============================
# CARGA DE DATASETS
# ===============================

student_info = pd.read_csv(DATA_PATH + "studentInfo.csv")
student_assessment = pd.read_csv(DATA_PATH + "studentAssessment.csv")
assessments = pd.read_csv(DATA_PATH + "assessments.csv")
student_vle = pd.read_csv(DATA_PATH + "studentVle.csv")

# ===============================
# LIMPIEZA DE DATOS
# ===============================

# Eliminar registros sin resultado final
student_info = student_info.dropna(subset=["final_result"])

# Limpieza y conversión de scores
student_assessment["score"] = pd.to_numeric(
    student_assessment["score"],
    errors="coerce"
)

student_assessment = student_assessment.dropna(subset=["score"])

student_assessment = student_assessment[
    (student_assessment["score"] >= 0) &
    (student_assessment["score"] <= 100)
]

student_vle = student_vle.dropna(subset=["sum_click"])

# Mapear resultados finales a valores numéricos
final_result_map = {
    "Fail": 40,
    "Withdrawn": 30,
    "Pass": 65,
    "Distinction": 85
}

student_info["final_score"] = student_info["final_result"].map(final_result_map)

# ===============================
# GRÁFICA 1: PROMEDIO DE NOTAS POR MATERIA
# ===============================

assessment_full = student_assessment.merge(
    assessments,
    on="id_assessment",
    how="inner"
)

avg_scores = (
    assessment_full
    .groupby("code_module")["score"]
    .mean()
    .reset_index()
    .rename(columns={"score": "average_score"})
)

avg_scores.to_json(
    OUTPUT_PATH + "rendimiento_por_materia.json",
    orient="records",
    indent=2
)

plt.figure()
plt.bar(avg_scores["code_module"], avg_scores["average_score"])
plt.xlabel("Materia")
plt.ylabel("Promedio de notas")
plt.title("Promedio de notas por materia")
plt.tight_layout()
plt.savefig(OUTPUT_PATH + "promedio_notas_por_materia.png")
plt.close()

# ===============================
# GRÁFICA 2: CLICKS EN PLATAFORMA VS NOTA FINAL
# ===============================

clicks_per_student = (
    student_vle
    .groupby("id_student")["sum_click"]
    .sum()
    .reset_index()
)

performance_clicks = student_info.merge(
    clicks_per_student,
    on="id_student",
    how="inner"
)

performance_clicks[[
    "id_student",
    "sum_click",
    "final_score"
]].to_json(
    OUTPUT_PATH + "clicks_vs_nota.json",
    orient="records",
    indent=2
)

plt.figure()
plt.scatter(
    performance_clicks["sum_click"],
    performance_clicks["final_score"],
    alpha=0.6
)
plt.xlabel("Total de clicks en la plataforma")
plt.ylabel("Nota final")
plt.title("Relación entre interacción en plataforma y nota final")
plt.tight_layout()
plt.savefig(OUTPUT_PATH + "clicks_vs_nota.png")
plt.close()

# ===============================
# GRÁFICA 3: EVALUACIONES RENDIDAS VS NOTA FINAL
# ===============================

# Contar número de evaluaciones rendidas por estudiante
assessments_per_student = (
    student_assessment
    .groupby("id_student")["id_assessment"]
    .count()
    .reset_index()
    .rename(columns={"id_assessment": "num_assessments"})
)

# Unir con información final del estudiante
performance_assessments = student_info.merge(
    assessments_per_student,
    on="id_student",
    how="inner"
)

# Guardar JSON
performance_assessments[[
    "id_student",
    "num_assessments",
    "final_score"
]].to_json(
    OUTPUT_PATH + "evaluaciones_vs_nota.json",
    orient="records",
    indent=2
)

# Graficar
plt.figure()
plt.scatter(
    performance_assessments["num_assessments"],
    performance_assessments["final_score"],
    alpha=0.6
)
plt.xlabel("Número de evaluaciones rendidas")
plt.ylabel("Nota final")
plt.title("Relación entre evaluaciones rendidas y nota final")
plt.tight_layout()
plt.savefig(OUTPUT_PATH + "evaluaciones_vs_nota.png")
plt.close()


# MENSAJE FINAL


print("Análisis de rendimiento académico completado.")
print("Resultados generados:")
print("- output/rendimiento_por_materia.json")
print("- output/clicks_vs_nota.json")
print("- output/evaluaciones_vs_nota.json")
print("- Gráficas PNG en la carpeta output/")
