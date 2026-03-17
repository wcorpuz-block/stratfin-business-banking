@echo off
echo ========================================
echo 🚀 CLAUDE CLI INSTALLATION (No Admin)
echo ========================================

cd /d "%USERPROFILE%"

echo.
echo 📦 Step 1: Creating Claude CLI directory...
if not exist "ClaudeCLI" mkdir ClaudeCLI
cd ClaudeCLI

echo ✅ Working directory: %CD%

echo.
echo 📥 Step 2: Downloading portable Node.js...
echo This will download Node.js without requiring admin rights...

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip' -OutFile 'node.zip'}"

if exist node.zip (
    echo ✅ Node.js downloaded successfully
) else (
    echo ❌ Download failed. Please check internet connection.
    pause
    exit /b 1
)

echo.
echo 📂 Step 3: Extracting Node.js...
powershell -Command "Expand-Archive -Path 'node.zip' -DestinationPath '.' -Force"

if exist "node-v20.11.0-win-x64" (
    echo ✅ Node.js extracted successfully
    ren "node-v20.11.0-win-x64" "nodejs"
) else (
    echo ❌ Extraction failed
    pause
    exit /b 1
)

echo.
echo 🧹 Cleaning up...
del node.zip

echo.
echo 🔧 Step 4: Testing Node.js installation...
set "NODE_PATH=%CD%\nodejs"
set "PATH=%NODE_PATH%;%PATH%"

"%NODE_PATH%\node.exe" --version
if %errorlevel% neq 0 (
    echo ❌ Node.js test failed
    pause
    exit /b 1
)

echo ✅ Node.js is working!

echo.
echo 📦 Step 5: Installing Claude CLI...
echo This may take a few minutes...

"%NODE_PATH%\npm.cmd" install -g @anthropic-ai/claude-cli

if %errorlevel% neq 0 (
    echo ❌ Claude CLI installation failed
    echo Trying alternative installation...
    "%NODE_PATH%\npm.cmd" install @anthropic-ai/claude-cli
)

echo.
echo 🔑 Step 6: Setting up environment...

echo.
echo Creating PowerShell profile script...
set "PROFILE_DIR=%USERPROFILE%\Documents\WindowsPowerShell"
if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

echo # Claude CLI Environment Setup > "%PROFILE_DIR%\Microsoft.PowerShell_profile.ps1"
echo $env:PATH += ";%CD%\nodejs" >> "%PROFILE_DIR%\Microsoft.PowerShell_profile.ps1"
echo $env:PATH += ";%CD%\nodejs\node_modules\.bin" >> "%PROFILE_DIR%\Microsoft.PowerShell_profile.ps1"
echo Write-Host "Claude CLI environment loaded" -ForegroundColor Green >> "%PROFILE_DIR%\Microsoft.PowerShell_profile.ps1"

echo.
echo Creating batch file for easy access...
echo @echo off > "%USERPROFILE%\claude.bat"
echo set "NODE_PATH=%CD%\nodejs" >> "%USERPROFILE%\claude.bat"
echo set "PATH=%%NODE_PATH%%;%%PATH%%" >> "%USERPROFILE%\claude.bat"
echo "%%NODE_PATH%%\node.exe" "%%NODE_PATH%%\node_modules\@anthropic-ai\claude-cli\bin\claude" %%* >> "%USERPROFILE%\claude.bat"

echo.
echo 🧪 Step 7: Testing Claude CLI...
set "NODE_PATH=%CD%\nodejs"
set "PATH=%NODE_PATH%;%PATH%"

echo Testing Claude CLI installation...
"%NODE_PATH%\node.exe" "%NODE_PATH%\node_modules\@anthropic-ai\claude-cli\bin\claude" --version

if %errorlevel% neq 0 (
    echo ❌ Claude CLI test failed
    echo Checking installation...
    dir "%NODE_PATH%\node_modules" | findstr claude
) else (
    echo ✅ Claude CLI is working!
)

echo.
echo 🎉 INSTALLATION COMPLETE!
echo ========================================
echo.
echo 📍 Installation Location: %CD%
echo.
echo 🚀 How to use Claude CLI:
echo.
echo Method 1 - Direct command:
echo   %CD%\nodejs\node.exe %CD%\nodejs\node_modules\@anthropic-ai\claude-cli\bin\claude --help
echo.
echo Method 2 - Using batch file:
echo   %USERPROFILE%\claude.bat --help
echo.
echo Method 3 - PowerShell (restart PowerShell first):
echo   claude --help
echo.
echo 🔑 Next Steps:
echo 1. Get your API key from: https://console.anthropic.com/
echo 2. Set up authentication: claude auth login
echo 3. Start using Claude: claude chat
echo.
echo 💡 Tip: Restart PowerShell to use 'claude' command directly
echo.

pause
