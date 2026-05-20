param(
    [string]$Url = "https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_low_res_mandatory.tar.gz",
    [string]$ArchivePath = "data/downloads/geog_low_res_mandatory.tar.gz",
    [string]$TargetDir = "data/geog"
)

$ErrorActionPreference = "Stop"

function Assert-ArchiveSize {
    param(
        [string]$Path,
        [int64]$ExpectedBytes
    )

    if (-not (Test-Path $Path)) {
        return $false
    }
    return ((Get-Item $Path).Length -eq $ExpectedBytes)
}

function Test-GeogReady {
    param([string]$Root)

    $expectedRoot = Join-Path $Root "WPS_GEOG_LOW_RES"
    $required = @(
        $expectedRoot,
        (Join-Path $expectedRoot "topo_gmted2010_5m"),
        (Join-Path $expectedRoot "modis_landuse_20class_5m_with_lakes"),
        (Join-Path $expectedRoot "soiltype_top_5m"),
        (Join-Path $expectedRoot "soiltype_bot_5m")
    )

    foreach ($path in $required) {
        if (-not (Test-Path $path)) {
            return $false
        }
    }
    return $true
}

New-Item -ItemType Directory -Force -Path (Split-Path $ArchivePath) | Out-Null
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Write-Host "Checking WPS geog package:"
Write-Host $Url
$head = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing
$length = [int64]$head.Headers["Content-Length"]
Write-Host ("Remote size: {0:n0} bytes" -f $length)

if (-not (Assert-ArchiveSize -Path $ArchivePath -ExpectedBytes $length)) {
    if (Test-Path $ArchivePath) {
        Write-Host "Removing incomplete archive: $ArchivePath"
        Remove-Item -LiteralPath $ArchivePath -Force
    }
    Write-Host "Downloading geog archive to $ArchivePath"
    Invoke-WebRequest -Uri $Url -OutFile $ArchivePath -UseBasicParsing
    if (-not (Assert-ArchiveSize -Path $ArchivePath -ExpectedBytes $length)) {
        throw "Downloaded archive size does not match remote Content-Length."
    }
} else {
    Write-Host "Archive already exists with expected size: $ArchivePath"
}

if (-not (Test-GeogReady -Root $TargetDir)) {
    Write-Host "Extracting archive to $TargetDir"
    tar -xzf $ArchivePath -C $TargetDir
    if (-not (Test-GeogReady -Root $TargetDir)) {
        throw "Geog extraction did not produce required WPS_GEOG_LOW_RES directories."
    }
} else {
    Write-Host "Geog directory already contains required low-resolution data: $TargetDir"
}

Write-Host "Geog preparation complete."
