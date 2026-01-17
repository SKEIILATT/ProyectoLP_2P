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

            // Establecer el directorio de trabajo al directorio del script
            $scriptDir = dirname($scriptPath);
            $process->setWorkingDirectory($scriptDir);

            // Configurar timeouts
            $process->setTimeout(60); // 60 segundos máximo
            $process->setIdleTimeout(30); // 30 segundos de inactividad

            // Configurar variables de entorno para matplotlib
            $env = $_SERVER;
            $env['HOME'] = getenv('USERPROFILE') ?: getenv('HOME') ?: 'C:\Users\Default';
            $env['USERPROFILE'] = getenv('USERPROFILE') ?: 'C:\Users\Default';
            $env['MPLCONFIGDIR'] = sys_get_temp_dir() . '/matplotlib';
            
            // Crear directorio temporal para matplotlib si no existe
            if (!is_dir($env['MPLCONFIGDIR'])) {
                mkdir($env['MPLCONFIGDIR'], 0755, true);
            }
            
            $process->setEnv($env);

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