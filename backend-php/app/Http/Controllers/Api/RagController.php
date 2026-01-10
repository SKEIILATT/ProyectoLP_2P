<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;

class RagController extends Controller
{
    private string $ragApiUrl = 'http://localhost:5000';

    /**
     * POST /api/rag/query
     * Realiza una consulta al sistema RAG
     */
    public function query(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'pregunta' => 'required|string|min:3',
            'modelo' => 'nullable|string|in:mistral,llama3,llama3.1'
        ]);

        try {
            // Llamar al servicio Python RAG
            $response = Http::timeout(60)->post("{$this->ragApiUrl}/api/rag/query", [
                'pregunta' => $validated['pregunta'],
                'modelo' => $validated['modelo'] ?? 'mistral'
            ]);

            if ($response->failed()) {
                return response()->json([
                    'success' => false,
                    'error' => 'Error al conectar con el servicio RAG'
                ], 503);
            }

            return response()->json($response->json());

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'El servicio RAG no está disponible. Asegúrate de que el servidor Python esté corriendo.',
                'details' => $e->getMessage()
            ], 503);
        }
    }

    /**
     * GET /api/rag/health
     * Verifica el estado del servicio RAG
     */
    public function health(): JsonResponse
    {
        try {
            $response = Http::timeout(5)->get("{$this->ragApiUrl}/health");

            if ($response->successful()) {
                return response()->json($response->json());
            }

            return response()->json([
                'status' => 'error',
                'message' => 'RAG service is down'
            ], 503);

        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Cannot connect to RAG service',
                'details' => $e->getMessage()
            ], 503);
        }
    }

    /**
     * GET /api/rag/models
     * Obtiene la lista de modelos disponibles
     */
    public function models(): JsonResponse
    {
        try {
            $response = Http::timeout(5)->get("{$this->ragApiUrl}/api/rag/models");

            if ($response->successful()) {
                return response()->json($response->json());
            }

            return response()->json([
                'models' => []
            ], 503);

        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Cannot fetch models',
                'details' => $e->getMessage()
            ], 503);
        }
    }

    /**
     * POST /api/rag/insights
     * Genera insights automáticos del RAG
     */
    public function insights(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'modelo' => 'nullable|string|in:mistral,llama3,llama3.1'
        ]);

        try {
            $response = Http::timeout(90)->post("{$this->ragApiUrl}/api/rag/insights", [
                'modelo' => $validated['modelo'] ?? 'mistral'
            ]);

            if ($response->failed()) {
                return response()->json([
                    'success' => false,
                    'error' => 'Error al generar insights'
                ], 503);
            }

            return response()->json($response->json());

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'El servicio RAG no está disponible',
                'details' => $e->getMessage()
            ], 503);
        }
    }

    /**
     * GET /api/rag/stats
     * Obtiene estadísticas del conocimiento almacenado en el RAG
     */
    public function stats(): JsonResponse
    {
        try {
            $response = Http::timeout(10)->get("{$this->ragApiUrl}/api/rag/stats");

            if ($response->successful()) {
                return response()->json($response->json());
            }

            return response()->json([
                'error' => 'Error al obtener estadísticas'
            ], 503);

        } catch (\Exception $e) {
            return response()->json([
                'error' => 'El servicio RAG no está disponible',
                'details' => $e->getMessage()
            ], 503);
        }
    }
}
