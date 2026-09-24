[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ReleaseZip,

    [Parameter(Mandatory = $false)]
    [string]$RepositoryRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$expectedZipName = 'SFM_Bring_Near_Lights_v1_02.zip'
$expectedZipSize = 29613
$expectedZipHash = 'E5940F8BC229CD325AF4AA9EE6E62B8D3CDB87EDA5A2C9087C6F9BD5329162C2'

$expectedEntries = [ordered]@{
    'README.txt' = @{
        Size = 3136
        Sha256 = '32ECDA40A5702AC1A93DB20DAD48EAA113E46AF481C733735141846454242BA3'
        RepositoryPath = 'README.txt'
    }
    'workshop/scripts/sfm/animset/SFM_Bring_Near_Lights.py' = @{
        Size = 105382
        Sha256 = '7F57BDF58A7273276CC1423E30B4988808276FF05940790025AB3E286D2C0051'
        RepositoryPath = 'workshop\scripts\sfm\animset\SFM_Bring_Near_Lights.py'
    }
}

function Get-StreamSha256 {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Stream]$Stream
    )

    $hasher = [System.Security.Cryptography.SHA256]::Create()

    try {
        $bytes = $hasher.ComputeHash($Stream)
        return ([System.BitConverter]::ToString($bytes)).Replace('-', '')
    }
    finally {
        $hasher.Dispose()
    }
}

function Assert-Equal {
    param(
        [Parameter(Mandatory = $true)]
        $Actual,

        [Parameter(Mandatory = $true)]
        $Expected,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    if ($Actual -ne $Expected) {
        throw (
            '{0}: expected "{1}", got "{2}"' -f
            $Description,
            $Expected,
            $Actual
        )
    }
}

if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = Split-Path -Parent $PSScriptRoot
}

$resolvedZip = (Resolve-Path -LiteralPath $ReleaseZip).Path
$resolvedRepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path

$zipItem = Get-Item -LiteralPath $resolvedZip

Assert-Equal `
    -Actual $zipItem.Name `
    -Expected $expectedZipName `
    -Description 'Release asset filename'

Assert-Equal `
    -Actual $zipItem.Length `
    -Expected $expectedZipSize `
    -Description 'Release asset size'

$actualZipHash = (
    Get-FileHash -LiteralPath $resolvedZip -Algorithm SHA256
).Hash.ToUpperInvariant()

Assert-Equal `
    -Actual $actualZipHash `
    -Expected $expectedZipHash `
    -Description 'Release asset SHA-256'

Add-Type -AssemblyName System.IO.Compression.FileSystem

$archive = [System.IO.Compression.ZipFile]::OpenRead($resolvedZip)

try {
    foreach ($entry in $archive.Entries) {
        $entryPath = $entry.FullName

        if ([System.IO.Path]::IsPathRooted($entryPath)) {
            throw "Unsafe rooted archive path: $entryPath"
        }

        if ($entryPath -match '(^|[\\/])\.\.([\\/]|$)') {
            throw "Unsafe parent traversal archive path: $entryPath"
        }

        if ($entryPath -match '^[A-Za-z]:') {
            throw "Unsafe drive-qualified archive path: $entryPath"
        }
    }

    $fileEntries = @(
        $archive.Entries |
            Where-Object { -not [string]::IsNullOrEmpty($_.Name) }
    )

    Assert-Equal `
        -Actual $fileEntries.Count `
        -Expected $expectedEntries.Count `
        -Description 'Archive payload file count'

    $actualEntryNames = @(
        $fileEntries |
            ForEach-Object { $_.FullName }
    )

    $uniqueEntryNames = @(
        $actualEntryNames |
            Sort-Object -Unique
    )

    Assert-Equal `
        -Actual $uniqueEntryNames.Count `
        -Expected $actualEntryNames.Count `
        -Description 'Unique archive payload path count'

    foreach ($expectedPath in $expectedEntries.Keys) {
        if ($actualEntryNames -cnotcontains $expectedPath) {
            throw "Missing expected archive entry: $expectedPath"
        }
    }

    foreach ($actualPath in $actualEntryNames) {
        if (-not $expectedEntries.Contains($actualPath)) {
            throw "Unexpected archive entry: $actualPath"
        }
    }

    foreach ($entry in $fileEntries) {
        $entrySpec = $expectedEntries[$entry.FullName]

        Assert-Equal `
            -Actual $entry.Length `
            -Expected $entrySpec.Size `
            -Description "Archive entry size for $($entry.FullName)"

        $entryStream = $entry.Open()

        try {
            $entryHash = (
                Get-StreamSha256 -Stream $entryStream
            ).ToUpperInvariant()
        }
        finally {
            $entryStream.Dispose()
        }

        Assert-Equal `
            -Actual $entryHash `
            -Expected $entrySpec.Sha256 `
            -Description "Archive entry SHA-256 for $($entry.FullName)"

        $repositoryPath = Join-Path `
            $resolvedRepositoryRoot `
            $entrySpec.RepositoryPath

        if (-not (Test-Path -LiteralPath $repositoryPath -PathType Leaf)) {
            throw "Missing repository payload file: $($entrySpec.RepositoryPath)"
        }

        $repositoryItem = Get-Item -LiteralPath $repositoryPath

        Assert-Equal `
            -Actual $repositoryItem.Length `
            -Expected $entrySpec.Size `
            -Description "Repository file size for $($entrySpec.RepositoryPath)"

        $repositoryHash = (
            Get-FileHash -LiteralPath $repositoryPath -Algorithm SHA256
        ).Hash.ToUpperInvariant()

        Assert-Equal `
            -Actual $repositoryHash `
            -Expected $entrySpec.Sha256 `
            -Description "Repository file SHA-256 for $($entrySpec.RepositoryPath)"

        Assert-Equal `
            -Actual $repositoryHash `
            -Expected $entryHash `
            -Description "ZIP/repository payload match for $($entry.FullName)"
    }
}
finally {
    $archive.Dispose()
}

Write-Output 'PASS: authoritative v1.0.2 ZIP identity verified.'
Write-Output 'PASS: archive paths and payload file list verified.'
Write-Output 'PASS: archive entry sizes and SHA-256 values verified.'
Write-Output 'PASS: repository payload matches the authoritative ZIP.'
Write-Output "ZIP_NAME=$expectedZipName"
Write-Output "ZIP_SIZE=$expectedZipSize"
Write-Output "ZIP_SHA256=$actualZipHash"
