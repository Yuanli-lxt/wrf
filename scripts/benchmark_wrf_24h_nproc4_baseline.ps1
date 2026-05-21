param(
    [int]$RepeatCount = 3,
    [int]$Nproc = 4,
    [string]$OutputPath = "data/generated/benchmarks/wrf_validation_24h_nproc4_baseline.csv"
)

$ErrorActionPreference = "Stop"

$RunLabel = "validation_20241001_00"
$dockerCommand = "docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh"
$outputDir = Split-Path $OutputPath
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

try {
    $gitCommit = (git rev-parse --short HEAD 2>$null).Trim()
} catch {
    $gitCommit = ""
}

$results = @()

for ($index = 1; $index -le $RepeatCount; $index++) {
    Write-Host "Running $RunLabel baseline repeat $index/$RepeatCount with NPROC=$Nproc"
    $env:NPROC = [string]$Nproc
    $logPath = "data/generated/benchmarks/wrf_validation_24h_nproc${Nproc}_repeat_${index}.log"
    $exitCode = 0

    $elapsed = Measure-Command {
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            cmd /c "$dockerCommand > `"$logPath`" 2>&1"
            $script:exitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $previousPreference
        }
    }

    $results += [PSCustomObject]@{
        run_label = $RunLabel
        run_index = $index
        nproc = $Nproc
        seconds = [Math]::Round($elapsed.TotalSeconds, 2)
        exit_code = $exitCode
        git_commit = $gitCommit
        log = $logPath
        command = $dockerCommand
    }

    if ($exitCode -ne 0) {
        Write-Host "Repeat $index failed. See $logPath"
    }
}

Remove-Item Env:NPROC -ErrorAction SilentlyContinue
$results | Export-Csv -Path $OutputPath -NoTypeInformation
$results | Format-Table -AutoSize
Write-Host "24h 4-core baseline benchmark written to $OutputPath"

$failed = @($results | Where-Object { $_.exit_code -ne 0 })
if ($failed.Count -gt 0) {
    throw "$($failed.Count) baseline benchmark repeat(s) failed."
}
