# CombinePyFiles.ps1
param(
    [switch]$Recurse,
    [switch]$IncludeRoot
)

$currentDir = Get-Location | Select-Object -ExpandProperty Path
Write-Host "Processing Python files in: $currentDir" -ForegroundColor Cyan

if ($Recurse) {
    $dirs = @(Get-ChildItem -Path $currentDir -Directory -Recurse | ForEach-Object { $_.FullName })
} else {
    $dirs = @(Get-ChildItem -Path $currentDir -Directory | ForEach-Object { $_.FullName })
}

if ($IncludeRoot) {
    $dirs = @($currentDir) + $dirs
}

$totalFiles = 0
$foldersWithFiles = 0

foreach ($dir in $dirs) {
    $pyFiles = @(Get-ChildItem -Path $dir -Filter "*.py" -File -ErrorAction SilentlyContinue)
    
    if ($pyFiles.Count -gt 0) {
        $foldersWithFiles++
        $totalFiles += $pyFiles.Count
        
        $dirName = Split-Path $dir -Leaf
        if ($dirName -eq "") { $dirName = "root" }
        $outputFile = Join-Path $dir "combined_python_$dirName.txt"
        
        $content = @()
        $content += "=" * 70
        $content += "PYTHON FILES FROM: $dir"
        $content += "GENERATED: $(Get-Date)"
        $content += "=" * 70
        $content += ""
        
        foreach ($file in $pyFiles) {
            $content += "#" * 70
            $content += "# FILE: $($file.FullName)"
            $content += "# MODIFIED: $($file.LastWriteTime)"
            $content += "#" * 70
            $content += ""
            $content += (Get-Content $file.FullName -Raw)
            $content += ""
            $content += "-" * 70
            $content += ""
        }
        
        $content += "=" * 70
        $content += "SUMMARY: $($pyFiles.Count) files combined"
        $content += "=" * 70
        
        $content | Out-File $outputFile -Encoding UTF8
        Write-Host "Created: $outputFile ($($pyFiles.Count) files)" -ForegroundColor Green
    }
}

Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  Folders processed: $($dirs.Count)" -ForegroundColor Yellow
Write-Host "  Folders with Python files: $foldersWithFiles" -ForegroundColor Green
Write-Host "  Total Python files combined: $totalFiles" -ForegroundColor Green