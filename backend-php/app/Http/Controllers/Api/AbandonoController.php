<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\DropoutAnalysis;
use Illuminate\Http\JsonResponse;

class AbandonoController extends Controller
{
    /**
     * GET /api/abandono/stats
     * Devuelve las estadísticas de abandono
     */
    public function stats(): JsonResponse
    {
        $analysis = DropoutAnalysis::latest()->first();

        if (!$analysis) {
            return response()->json([
                'message' => 'No hay datos de abandono disponibles',
                'data' => null
            ], 404);
        }

        return response()->json([
            'message' => 'Estadísticas de abandono',
            'data' => [
                'por_sexo' => $analysis->estadisticas_por_sexo,
                'por_tipo_institucion' => $analysis->estadisticas_por_tipo_institucion,
                'resumen_general' => $analysis->resumen_general,
                'analisis' => $analysis->analisis_texto,
                'fecha_actualizacion' => $analysis->updated_at,
            ]
        ], 200);
    }

    /**
     * GET /api/abandono/graphs
     * Devuelve las URLs o data de las gráficas
     */
    public function graphs(): JsonResponse
    {
        $analysis = DropoutAnalysis::latest()->first();

        if (!$analysis) {
            return response()->json([
                'message' => 'No hay gráficos disponibles',
                'data' => null
            ], 404);
        }

        return response()->json([
            'message' => 'Gráficos de abandono',
            'data' => [
                'grafico_sexo' => $analysis->grafico_sexo_url,
                'grafico_institucion' => $analysis->grafico_institucion_url,
                'grafico_general' => $analysis->grafico_general_url,
            ]
        ], 200);
    }

    /**
     * POST /api/abandono/sync
     * Para sincronizar datos desde Python
     */
    public function sync(): JsonResponse
    {
        return response()->json([
            'message' => 'Endpoint para sincronizar datos',
        ], 200);
    }
}
