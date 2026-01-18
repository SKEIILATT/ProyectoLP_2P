<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AbandonoController;
use App\Http\Controllers\Api\RagController;
use App\Services\PythonRunnerService;
use App\Http\Controllers\RendimientoController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Rutas de Abandono
Route::prefix('abandono')->group(function () {
    Route::get('/stats', [AbandonoController::class, 'stats']);
    Route::get('/graphs', [AbandonoController::class, 'graphs']);
    Route::post('/sync', [AbandonoController::class, 'sync']);
});

// Rutas de RAG
Route::prefix('rag')->group(function () {
    Route::post('/query', [RagController::class, 'query']);
    Route::post('/insights', [RagController::class, 'insights']);
    Route::get('/stats', [RagController::class, 'stats']);
    Route::get('/health', [RagController::class, 'health']);
    Route::get('/models', [RagController::class, 'models']);
});

// Rutas para PythonRunnerService
Route::get('/test-python', function () {
    $pythonService = new PythonRunnerService();
    $result = $pythonService->runCode("print('Hola')");
    return response()->json($result);
});

Route::post('/run-python-script', function (Request $request) {
    $request->validate([
        'script_path' => 'required|string',
        'arguments' => 'array'
    ]);

    $pythonService = new PythonRunnerService();
    $result = $pythonService->runScript(
        $request->script_path,
        $request->arguments ?? []
    );

    return response()->json($result);
});

// Rutas de Rendimiento
Route::get('/rendimiento/general', [RendimientoController::class, 'general']);
Route::post('/chat/ask', [RendimientoController::class, 'ask']);
