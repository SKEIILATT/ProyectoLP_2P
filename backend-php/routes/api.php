<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
<<<<<<< HEAD
use App\Http\Controllers\Api\AbandonoController;
use App\Http\Controllers\Api\RagController;
=======
use App\Services\PythonRunnerService;
use App\Http\Controllers\RendimientoController;
>>>>>>> dev-Jair

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

<<<<<<< HEAD
Route::prefix('abandono')->group(function () {
    Route::get('/stats', [AbandonoController::class, 'stats']);
    Route::get('/graphs', [AbandonoController::class, 'graphs']);
    Route::post('/sync', [AbandonoController::class, 'sync']);
});

Route::prefix('rag')->group(function () {
    Route::post('/query', [RagController::class, 'query']);
    Route::get('/health', [RagController::class, 'health']);
    Route::get('/models', [RagController::class, 'models']);
});
=======
// Ruta para probar la ejecución de Python
Route::get('/test-python', function () {
    $pythonService = new PythonRunnerService();

    // Probar con un simple print('Hola')
    $result = $pythonService->runCode("print('Hola')");

    return response()->json($result);
});

// Ruta para ejecutar un script específico
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

// Rutas de rendimiento
Route::get('/rendimiento/general', [RendimientoController::class, 'general']);
Route::post('/chat/ask', [RendimientoController::class, 'ask']);
>>>>>>> dev-Jair
