<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AbandonoController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::prefix('abandono')->group(function () {
    Route::get('/stats', [AbandonoController::class, 'stats']);
    Route::get('/graphs', [AbandonoController::class, 'graphs']);
    Route::post('/sync', [AbandonoController::class, 'sync']);
});
