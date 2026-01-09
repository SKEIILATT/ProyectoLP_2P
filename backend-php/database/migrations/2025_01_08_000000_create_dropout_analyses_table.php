<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('dropout_analyses', function (Blueprint $table) {
            $table->id();
            $table->json('estadisticas_por_sexo')->nullable();
            $table->json('estadisticas_por_tipo_institucion')->nullable();
            $table->json('resumen_general')->nullable();
            $table->string('grafico_sexo_url')->nullable();
            $table->string('grafico_institucion_url')->nullable();
            $table->string('grafico_general_url')->nullable();
            $table->text('analisis_texto')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('dropout_analyses');
    }
};
