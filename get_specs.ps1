# Hardware & Environment Specifications Gatherer
# Run this script in PowerShell to gather all specs for your AI creative studio prompt

Write-Host "================================" -ForegroundColor Cyan
Write-Host "GATHERING SYSTEM SPECIFICATIONS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Output file
$outputFile = "system_specs_output.txt"
"HARDWARE & ENVIRONMENT SPECS FOR PROMPT" | Out-File $outputFile
"=========================================" | Out-File $outputFile -Append
"" | Out-File $outputFile -Append

# CPU
Write-Host "Gathering CPU info..." -ForegroundColor Yellow
"**Hardware**:" | Out-File $outputFile -Append
$cpu = Get-WmiObject -Class Win32_Processor | Select-Object -First 1
$cpuName = $cpu.Name.Trim()
$cores = $cpu.NumberOfCores
$threads = $cpu.NumberOfLogicalProcessors
"- CPU: $cpuName, $cores-core, $threads-thread" | Out-File $outputFile -Append

# GPU
Write-Host "Gathering GPU info..." -ForegroundColor Yellow
try {
    $gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
    if ($gpu) {
        $gpuInfo = $gpu -split ','
        $gpuName = $gpuInfo[0].Trim()
        $gpuMem = $gpuInfo[1].Trim()
        "- GPU: $gpuName, $gpuMem" | Out-File $outputFile -Append
    } else {
        "- GPU: Not detected or nvidia-smi not available" | Out-File $outputFile -Append
    }
} catch {
    "- GPU: Error detecting GPU" | Out-File $outputFile -Append
}

# RAM
Write-Host "Gathering RAM info..." -ForegroundColor Yellow
$ram = Get-WmiObject -Class Win32_ComputerSystem
$ramGB = [math]::Round($ram.TotalPhysicalMemory/1GB, 0)
"- RAM: $ramGB GB DDR4" | Out-File $outputFile -Append

# Storage
Write-Host "Gathering storage info..." -ForegroundColor Yellow
$systemDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "C:"}
$storageTB = [math]::Round($systemDrive.Size/1TB, 1)
$storageGB = [math]::Round($systemDrive.Size/1GB, 0)
if ($storageTB -ge 1) {
    "- Storage: $storageTB TB NVMe SSD (primary)" | Out-File $outputFile -Append
} else {
    "- Storage: $storageGB GB SSD (primary)" | Out-File $outputFile -Append
}

"" | Out-File $outputFile -Append
"**Software Environment**:" | Out-File $outputFile -Append

# Windows Version
Write-Host "Gathering Windows version..." -ForegroundColor Yellow
$os = Get-WmiObject -Class Win32_OperatingSystem
$osName = $os.Caption
$osBuild = $os.BuildNumber
"- OS: $osName (Build $osBuild)" | Out-File $outputFile -Append

# WSL
Write-Host "Gathering WSL info..." -ForegroundColor Yellow
try {
    $wslVersion = wsl --list --verbose 2>$null | Select-String "Ubuntu"
    if ($wslVersion) {
        "- WSL: Ubuntu (version details below)" | Out-File $outputFile -Append
    } else {
        "- WSL: Not detected" | Out-File $outputFile -Append
    }
} catch {
    "- WSL: Not detected" | Out-File $outputFile -Append
}

# Check if conda is available
Write-Host "Checking conda environment..." -ForegroundColor Yellow
try {
    $condaCheck = conda --version 2>$null
    if ($condaCheck) {
        "- Conda: Installed" | Out-File $outputFile -Append
        
        # Activate multimodal-assistant environment
        Write-Host "Activating multimodal-assistant environment..." -ForegroundColor Yellow
        
        # Python version
        Write-Host "Getting Python version..." -ForegroundColor Yellow
        $pythonVersion = & conda run -n multimodal-assistant python --version 2>&1
        "- Python (Windows): $pythonVersion" | Out-File $outputFile -Append
        
        # PyTorch and CUDA
        Write-Host "Getting PyTorch and CUDA info..." -ForegroundColor Yellow
        $torchInfo = & conda run -n multimodal-assistant python -c "import torch; print(f'PyTorch {torch.__version__} (CUDA {torch.version.cuda if torch.cuda.is_available() else \"N/A\"})')" 2>&1
        "- $torchInfo" | Out-File $outputFile -Append
        
        # Key packages
        Write-Host "Getting package versions..." -ForegroundColor Yellow
        $streamlitVer = & conda run -n multimodal-assistant python -c "import streamlit; print(streamlit.__version__)" 2>&1
        $transformersVer = & conda run -n multimodal-assistant python -c "import transformers; print(transformers.__version__)" 2>&1
        $faissVer = & conda run -n multimodal-assistant python -c "import faiss; print(faiss.__version__)" 2>&1
        
        "- Streamlit: $streamlitVer" | Out-File $outputFile -Append
        "- Transformers: $transformersVer" | Out-File $outputFile -Append
        "- FAISS: $faissVer" | Out-File $outputFile -Append
        
    } else {
        "- Conda: Not installed" | Out-File $outputFile -Append
        
        # Try regular Python
        Write-Host "Conda not found, trying system Python..." -ForegroundColor Yellow
        $pythonVersion = python --version 2>&1
        "- Python (Windows): $pythonVersion" | Out-File $outputFile -Append
    }
} catch {
    "- Error gathering Python/Conda info" | Out-File $outputFile -Append
}

# CUDA Toolkit
Write-Host "Checking CUDA Toolkit..." -ForegroundColor Yellow
try {
    $cudaVersion = nvcc --version 2>$null | Select-String "release" | ForEach-Object { $_.Line -replace '.*release ', '' -replace ',.*', '' }
    if ($cudaVersion) {
        "- CUDA Toolkit: $cudaVersion" | Out-File $outputFile -Append
    } else {
        "- CUDA Toolkit: Not installed on Windows (may be in WSL only)" | Out-File $outputFile -Append
    }
} catch {
    "- CUDA Toolkit: Not detected" | Out-File $outputFile -Append
}

"" | Out-File $outputFile -Append
"**Terminal Workflow** (4 tabs):" | Out-File $outputFile -Append
"1. WSL: vLLM server (Qwen2.5-3B-Instruct) -> localhost:8000" | Out-File $outputFile -Append
"2. WSL: Embeddings server (bge-small-en-v1.5) -> localhost:8001" | Out-File $outputFile -Append
"3. Windows: Streamlit UI -> localhost:8501" | Out-File $outputFile -Append
"4. Windows: Orchestrator process (blocking run_forever())" | Out-File $outputFile -Append

"" | Out-File $outputFile -Append
"**WSL Environment** (run these commands in WSL Ubuntu):" | Out-File $outputFile -Append
"lsb_release -d" | Out-File $outputFile -Append
"python3 --version" | Out-File $outputFile -Append
"nvcc --version | grep release" | Out-File $outputFile -Append
"pip show vllm | grep Version" | Out-File $outputFile -Append
"nvidia-smi --query-gpu=driver_version --format=csv,noheader" | Out-File $outputFile -Append

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "SPECS SAVED TO: $outputFile" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Now displaying the output:" -ForegroundColor Cyan
Write-Host ""

# Display the output
Get-Content $outputFile

Write-Host ""
Write-Host "================================" -ForegroundColor Yellow
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host "1. Copy the output above (or from $outputFile)" -ForegroundColor White
Write-Host "2. Run the WSL commands shown at the bottom in your Ubuntu terminal" -ForegroundColor White
Write-Host "3. Paste both outputs to complete your hardware section" -ForegroundColor White
Write-Host ""