param(
    [int[]]$CoreCounts = @(1, 2, 4),
    [string]$OutputPath = "data/generated/benchmarks/wrf_validation_benchmark.csv"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path (Split-Path $OutputPath) | Out-Null
$results = @()

foreach ($core in $CoreCounts) {
    Write-Host "Running WRF validation benchmark with NPROC=$core"
    $env:NPROC = [string]$core
    $logPath = "data/generated/benchmarks/wrf_validation_nproc_${core}.log"
    $dockerCommand = "docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh"
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
        nproc = $core
        seconds = [Math]::Round($elapsed.TotalSeconds, 2)
        exit_code = $exitCode
        log = $logPath
    }

    if ($exitCode -ne 0) {
        Write-Host "NPROC=$core failed. See $logPath"
    }
}

Remove-Item Env:NPROC -ErrorAction SilentlyContinue
$results | Export-Csv -Path $OutputPath -NoTypeInformation
$results | Format-Table -AutoSize
Write-Host "Benchmark written to $OutputPath"
