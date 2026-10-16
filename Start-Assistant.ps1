$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$python = Join-Path $projectDir '.venv\Scripts\pythonw.exe'

try {
    if (-not (Test-Path -LiteralPath $python)) {
        throw 'Python environment is missing. Follow the setup instructions in README.md.'
    }

    $ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
    $ollama = if ($ollamaCommand) { $ollamaCommand.Source } else {
        Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
    }
    try {
        $null = Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2
    } catch {
        if (-not (Test-Path -LiteralPath $ollama)) {
            throw 'Ollama is missing. Install it from https://ollama.com/download/windows.'
        }
        Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
        $ready = $false
        for ($attempt = 0; $attempt -lt 30; $attempt++) {
            Start-Sleep -Seconds 1
            try {
                $null = Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2
                $ready = $true
                break
            } catch { }
        }
        if (-not $ready) { throw 'Ollama did not start. Open Ollama and try again.' }
    }

    Start-Process -FilePath $python -ArgumentList '-m', 'local_ai_assistant.main' -WorkingDirectory $projectDir
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
