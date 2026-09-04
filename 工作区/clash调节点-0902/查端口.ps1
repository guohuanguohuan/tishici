$p = Get-Process verge-mihomo -ErrorAction SilentlyContinue
if ($p) {
  $p | Select-Object Id, StartTime | Format-Table -AutoSize
  Get-NetTCPConnection -State Listen -OwningProcess $p.Id -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort | Sort-Object LocalPort -Unique | Format-Table -AutoSize
} else {
  'verge-mihomo process not found'
}
