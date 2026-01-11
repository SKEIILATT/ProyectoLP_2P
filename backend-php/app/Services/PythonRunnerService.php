<?php

namespace App\Services;

use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class PythonRunnerService
{
    /**
     * Ejecuta un script de Python y devuelve el resultado
     *
     * @param string $scriptPath Ruta absoluta al script de Python
     * @param array $arguments Argumentos a pasar al script
     * @return array Resultado con 'success', 'output', 'error'
     */
    public function runScript(string $scriptPath, array $arguments = []): array
    {
        try {
            // Verificar que el archivo existe
            if (!file_exists($scriptPath)) {
                return [
                    'success' => false,
                    'output' => null,
                    'error' => 'Script file not found: ' . $scriptPath
                ];
            }

            // Construir el comando
            $command = array_merge(['python', $scriptPath], $arguments);

            // Crear el proceso
            $process = new Process($command);

            // Configurar timeouts
            $process->setTimeout(60); // 60 segundos máximo
            $process->setIdleTimeout(30); // 30 segundos de inactividad

            // Ejecutar el proceso
            $process->run();

            // Verificar si fue exitoso
            if ($process->isSuccessful()) {
                return [
                    'success' => true,
                    'output' => trim($process->getOutput()),
                    'error' => null
                ];
            } else {
                return [
                    'success' => false,
                    'output' => trim($process->getOutput()),
                    'error' => trim($process->getErrorOutput())
                ];
            }

        } catch (ProcessFailedException $e) {
            return [
                'success' => false,
                'output' => $e->getProcess()->getOutput(),
                'error' => $e->getMessage()
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'output' => null,
                'error' => 'Unexpected error: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Ejecuta un script simple de Python
     *
     * @param string $code Código Python a ejecutar
     * @return array Resultado
     */
    public function runCode(string $code): array
    {
        try {
            // Crear un archivo temporal con el código
            $tempFile = tempnam(sys_get_temp_dir(), 'python_code_') . '.py';
            file_put_contents($tempFile, $code);

            // Ejecutar el archivo temporal
            $result = $this->runScript($tempFile);

            // Limpiar el archivo temporal
            if (file_exists($tempFile)) {
                unlink($tempFile);
            }

            return $result;

        } catch (\Exception $e) {
            return [
                'success' => false,
                'output' => null,
                'error' => 'Error creating temporary file: ' . $e->getMessage()
            ];
        }
    }
}