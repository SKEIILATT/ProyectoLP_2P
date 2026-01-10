<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AbandonoController;
use App\Http\Controllers\Api\RagController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::prefix('abandono')->group(function () {
    Route::get('/stats', [AbandonoController::class, 'stats']);
    Route::get('/graphs', [AbandonoController::class, 'graphs']);
    Route::post('/sync', [AbandonoController::class, 'sync']);
});

Route::prefix('rag')->group(function () {
    Route::post('/query', [RagController::class, 'query']);
    Route::post('/insights', [RagController::class, 'insights']);
    Route::get('/stats', [RagController::class, 'stats']);
    Route::get('/health', [RagController::class, 'health']);
    Route::get('/models', [RagController::class, 'models']);
});
