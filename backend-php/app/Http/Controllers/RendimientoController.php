<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Services\PythonRunnerService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class RendimientoController extends Controller
{
    protected PythonRunnerService $pythonService;

    public function __construct(PythonRunnerService $pythonService)
    {
        $this->pythonService = $pythonService;
    }

    /**
     * Obtener datos generales de rendimiento
     */
    public function general(): JsonResponse
    {
        try {
            // Leer los archivos JSON pre-generados (no re-ejecutar el script)
            $outputPath = dirname(base_path()) . '/backend-python/output/';

            $rendimientoMateria = $this->readJsonFile($outputPath . 'rendimiento_por_materia.json');
            $clicksVsNota = $this->readJsonFile($outputPath . 'clicks_vs_nota.json');
            $evaluacionesVsNota = $this->readJsonFile($outputPath . 'evaluaciones_vs_nota.json');

            // Verificar que los archivos existan
            if ($rendimientoMateria === null && $clicksVsNota === null && $evaluacionesVsNota === null) {
                return response()->json([
                    'success' => false,
                    'message' => 'No se encontraron datos de rendimiento',
                    'error' => 'Los archivos JSON no existen en: ' . $outputPath
                ], 404);
            }

            return response()->json([
                'success' => true,
                'data' => [
                    'rendimiento_por_materia' => $rendimientoMateria ?? [],
                    'clicks_vs_nota' => $clicksVsNota ?? [],
                    'evaluaciones_vs_nota' => $evaluacionesVsNota ?? []
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error interno del servidor',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Leer archivo JSON de forma segura
     */
    private function readJsonFile(string $filePath): ?array
    {
        if (!file_exists($filePath)) {
            return null;
        }

        $content = file_get_contents($filePath);
        if ($content === false) {
            return null;
        }

        $data = json_decode($content, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return null;
        }

        return $data;
    }

    /**
     * Procesar pregunta del chat usando RAG
     */
    public function ask(Request $request): JsonResponse
    {
        try {
            $request->validate([
                'question' => 'required|string|max:1000'
            ]);

            // TODO: Integrar con el script RAG real de Javier

            // Simulación de llamada al script RAG
            $mockResponse = [
                'question' => $request->question,
                'answer' => 'Esta es una respuesta simulada del sistema RAG. Para integrar con el script real, necesitamos la ruta al script de Javier.',
                'confidence' => 0.85,
                'sources' => ['documento1.pdf', 'documento2.pdf']
            ];

            return response()->json([
                'success' => true,
                'data' => $mockResponse
            ]);

        } catch (\Illuminate\Validation\ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Datos de entrada inválidos',
                'errors' => $e->errors()
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error interno del servidor',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
