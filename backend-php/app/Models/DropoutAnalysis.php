<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class DropoutAnalysis extends Model
{
    protected $fillable = [
        'estadisticas_por_sexo',
        'estadisticas_por_tipo_institucion',
        'resumen_general',
        'grafico_sexo_url',
        'grafico_institucion_url',
        'grafico_general_url',
        'analisis_texto',
    ];

    protected $casts = [
        'estadisticas_por_sexo' => 'array',
        'estadisticas_por_tipo_institucion' => 'array',
        'resumen_general' => 'array',
    ];
}
