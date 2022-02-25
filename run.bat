del *.log
type nul > RAS.log
type nul > SEM_UDP.log
type nul > SEM_STATE.log
type nul > UPR_RECIEVE.log
type nul > UPR_STATE.log
start powershell -executionpolicy remotesigned -File  RAS.ps1
start powershell -executionpolicy remotesigned -File  SEM_UDP.ps1
start powershell -executionpolicy remotesigned -File  SEM_STATE.ps1
start powershell -executionpolicy remotesigned -File  UPR_RECIEVE.ps1
start powershell -executionpolicy remotesigned -File  UPR_STATE.ps1
python main.py
