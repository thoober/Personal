@echo off
for %%a in (%*) do ("C:\Program Files\7-Zip\7z.exe" x "%%a" -oD:\extracted\* -aos)
echo extracted mxds and gdbs to v101 folder

