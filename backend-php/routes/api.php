<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Services\PythonRunnerService;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

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
