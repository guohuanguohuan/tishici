param(
    [Parameter(Mandatory = $true)][string]$DocxPath,
    [Parameter(Mandatory = $true)][string]$PdfPath
)

$word = $null
$doc = $null
try {
    $docx = [System.IO.Path]::GetFullPath($DocxPath)
    $pdf = [System.IO.Path]::GetFullPath($PdfPath)
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($pdf)) | Out-Null

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.Options.SaveNormalPrompt = $false

    $doc = $word.Documents.Open($docx, $false, $false)
    if ($doc.OMaths.Count -gt 0) {
        for ($i = 1; $i -le $doc.OMaths.Count; $i++) {
            $doc.OMaths.Item($i).BuildUp()
        }
    }
    $doc.Save()
    $pages = $doc.ComputeStatistics(2)
    $doc.ExportAsFixedFormat($pdf, 17)
    Write-Output "pages=$pages"
    Write-Output "omaths=$($doc.OMaths.Count)"
    Write-Output "pdf=$pdf"
}
finally {
    if ($doc -ne $null) {
        $doc.Close(0)
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) | Out-Null
    }
    if ($word -ne $null) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
