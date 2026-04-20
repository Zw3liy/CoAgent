![Agent Status](https://img.shields.io/badge/CoAgent-Issues-red) 
:: Update STATUS.md for GitHub badge
set STATUSFILE=C:\CoAgent\STATUS.md

if %ERRORS%==0 (
    echo ![Agent Status](https://img.shields.io/badge/CoAgent-Healthy-brightgreen) > "%STATUSFILE%"
) else (
    echo ![Agent Status](https://img.shields.io/badge/CoAgent-Issues-red) > "%STATUSFILE%"
)

