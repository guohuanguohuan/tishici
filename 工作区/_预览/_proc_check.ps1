$procs = Get-CimInstance Win32_Process -Filter "Name='WINWORD.EXE' or Name='python.exe' or Name='pythonw.exe'"
foreach ($p in $procs) {
    $title = ''
    try { $title = (Get-Process -Id $p.ProcessId -ErrorAction Stop).MainWindowTitle } catch {}
    $cmd = $p.CommandLine
    if ($cmd -and $cmd.Length -gt 140) { $cmd = $cmd.Substring(0,140) }
    $parentName = ''
    try { $parentName = (Get-CimInstance Win32_Process -Filter ("ProcessId=" + $p.ParentProcessId) -ErrorAction Stop).Name } catch { $parentName = '<gone>' }
    if (-not $parentName) { $parentName = '<gone>' }
    Write-Output ("PID={0}  NAME={1}  PARENT={2}({3})  WINDOW=[{4}]" -f $p.ProcessId, $p.Name, $p.ParentProcessId, $parentName, $title)
    Write-Output ("    CMD: " + $cmd)
}
Write-Output "---- total: $($procs.Count)"
